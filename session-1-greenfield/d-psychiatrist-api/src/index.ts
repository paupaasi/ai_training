import express from 'express';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { OllamaService } from './services/llm-service.js';
import { createPsychiatristRouter } from './routes/psychiatrist.js';

const __dirname = dirname(fileURLToPath(import.meta.url));

const app = express();
const PORT = process.env.PORT ?? 3000;
const OLLAMA_HOST = process.env.OLLAMA_HOST ?? 'http://127.0.0.1:11434';
const OLLAMA_MODEL = process.env.OLLAMA_MODEL ?? 'gemma3';
const startTime = Date.now();

app.use(express.json());

// Serve the frontend from public/
app.use(express.static(join(__dirname, '..', 'public')));

// Health check — no auth, no external deps
app.get('/health', (_req, res) => {
  res.json({
    status: 'ok',
    uptime: Math.floor((Date.now() - startTime) / 1000),
  });
});

const ollamaService = new OllamaService(OLLAMA_HOST, OLLAMA_MODEL);
app.use('/', createPsychiatristRouter(ollamaService));

app.listen(PORT, () => {
  console.log(`🧠 Home Psychiatrist API running on http://localhost:${PORT}`);
  console.log(`   Model: ${OLLAMA_MODEL} via Ollama at ${OLLAMA_HOST}`);
  console.log('');
  console.log('  POST /sessions                   Start a therapy session');
  console.log('  POST /sessions/:id/messages      Chat with your psychiatrist');
  console.log('  GET  /sessions/:id/diagnosis     Get your official diagnosis');
  console.log('  GET  /personalities              List available personalities');
  console.log('  GET  /health                     Health check');
});
