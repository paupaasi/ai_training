import { Ollama } from 'ollama';
import type { Message } from '../types.js';

// Generic LLM interface — implemented by OllamaService (and by mocks in tests)
export interface LLMClient {
  chat(
    systemPrompt: string,
    history: Message[],
    userMessage: string
  ): Promise<string>;
}

export class OllamaService implements LLMClient {
  private client: Ollama;
  private model: string;

  constructor(
    host: string = 'http://127.0.0.1:11434',
    model: string = 'gemma3'
  ) {
    this.client = new Ollama({ host });
    this.model = model;
  }

  async chat(
    systemPrompt: string,
    history: Message[],
    userMessage: string
  ): Promise<string> {
    const messages = [
      { role: 'system' as const, content: systemPrompt },
      ...history.map(msg => ({
        role: msg.role === 'user' ? ('user' as const) : ('assistant' as const),
        content: msg.content,
      })),
      { role: 'user' as const, content: userMessage },
    ];

    const response = await this.client.chat({
      model: this.model,
      messages,
    });

    return response.message.content;
  }
}
