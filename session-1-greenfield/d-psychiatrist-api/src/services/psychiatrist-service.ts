import { randomUUID } from 'crypto';
import type { LLMClient } from './llm-service.js';
import type {
  Session,
  StartSessionRequest,
  StartSessionResponse,
  Personality,
  PersonalityId,
} from '../types.js';
import { personalities, getPersonalityById } from '../data/personalities.js';
import * as storage from '../storage.js';

const GREETING_PROMPT =
  'Greet this new patient with your opening statement. Be brief (2-3 sentences).';

const DIAGNOSIS_PROMPT =
  'Based on everything discussed in this session, give this patient a brief, dramatic, funny official diagnosis (2-3 sentences). Make it sound like a real medical certificate.';

export function getPersonalities(): Personality[] {
  return personalities;
}

export async function startSession(
  request: StartSessionRequest,
  gemini: LLMClient
): Promise<StartSessionResponse> {
  const personalityId: PersonalityId = request.personality ?? 'default';
  const personality = getPersonalityById(personalityId);

  if (!personality) {
    throw new Error(`Unknown personality: "${personalityId}"`);
  }

  const greeting = await gemini.chat(personality.systemPrompt, [], GREETING_PROMPT);

  const session: Session = {
    id: randomUUID(),
    personality: personalityId,
    messages: [
      { role: 'psychiatrist', content: greeting, timestamp: new Date().toISOString() },
    ],
    createdAt: new Date().toISOString(),
  };

  storage.createSession(session);
  return { sessionId: session.id, greeting };
}

export async function sendMessage(
  sessionId: string,
  message: string,
  gemini: LLMClient
): Promise<string | null> {
  if (!message || message.trim().length === 0) {
    throw new Error('Message cannot be empty');
  }

  const session = storage.getSession(sessionId);
  if (!session) return null;

  const personality = getPersonalityById(session.personality);
  if (!personality) {
    throw new Error(`Unknown personality: "${session.personality}"`);
  }

  // Convert stored messages to the format expected by LLMClient.chat().
  // The initial greeting (index 0) has role 'psychiatrist' — OllamaService maps this to 'assistant'.
  const history = session.messages.map(msg => ({
    role: msg.role as 'user' | 'psychiatrist',
    content: msg.content,
    timestamp: msg.timestamp,
  }));

  const response = await gemini.chat(personality.systemPrompt, history, message.trim());

  session.messages.push(
    { role: 'user', content: message.trim(), timestamp: new Date().toISOString() },
    { role: 'psychiatrist', content: response, timestamp: new Date().toISOString() }
  );
  storage.updateSession(session);

  return response;
}

export async function getDiagnosis(
  sessionId: string,
  gemini: LLMClient
): Promise<string | null> {
  const session = storage.getSession(sessionId);
  if (!session) return null;

  const personality = getPersonalityById(session.personality);
  if (!personality) {
    throw new Error(`Unknown personality: "${session.personality}"`);
  }

  return gemini.chat(personality.systemPrompt, session.messages, DIAGNOSIS_PROMPT);
}
