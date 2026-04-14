import { Router } from 'express';
import type { LLMClient } from '../services/llm-service.js';
import {
  getPersonalities,
  startSession,
  sendMessage,
  getDiagnosis,
} from '../services/psychiatrist-service.js';
import type { StartSessionRequest, ChatRequest } from '../types.js';

export function createPsychiatristRouter(gemini: LLMClient): Router {
  const router = Router();

  // GET /personalities — list available personalities
  router.get('/personalities', (_req, res) => {
    const result = getPersonalities().map(({ id, name, tagline, description }) => ({
      id,
      name,
      tagline,
      description,
    }));
    res.json({ data: result });
  });

  // POST /sessions — start a new therapy session
  router.post('/sessions', async (req, res) => {
    const body = req.body as Partial<StartSessionRequest>;
    try {
      const result = await startSession({ personality: body.personality }, gemini);
      res.status(201).json({ data: result });
    } catch (err) {
      if (err instanceof Error && err.message.startsWith('Unknown personality')) {
        res.status(400).json({ error: err.message });
      } else {
        res.status(500).json({ error: 'Internal server error' });
      }
    }
  });

  // POST /sessions/:id/messages — chat with the psychiatrist
  router.post('/sessions/:id/messages', async (req, res) => {
    const { id } = req.params;
    const body = req.body as Partial<ChatRequest>;

    if (!body.message) {
      res.status(400).json({ error: 'message is required' });
      return;
    }

    try {
      const response = await sendMessage(id, body.message, gemini);
      if (response === null) {
        res.status(404).json({ error: `Session "${id}" not found` });
        return;
      }
      res.json({ data: { response } });
    } catch (err) {
      if (err instanceof Error && err.message === 'Message cannot be empty') {
        res.status(400).json({ error: err.message });
      } else {
        res.status(500).json({ error: 'Internal server error' });
      }
    }
  });

  // GET /sessions/:id/diagnosis — get funny session diagnosis
  router.get('/sessions/:id/diagnosis', async (req, res) => {
    const { id } = req.params;
    try {
      const diagnosis = await getDiagnosis(id, gemini);
      if (diagnosis === null) {
        res.status(404).json({ error: `Session "${id}" not found` });
        return;
      }
      res.json({ data: { diagnosis } });
    } catch (err) {
      res.status(500).json({ error: 'Internal server error' });
    }
  });

  return router;
}
