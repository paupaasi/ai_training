import { describe, it, expect, vi, beforeEach } from 'vitest';
import type { LLMClient } from './llm-service.js';
import {
  startSession,
  sendMessage,
  getPersonalities,
  getDiagnosis,
} from './psychiatrist-service.js';
import * as storage from '../storage.js';

describe('PsychiatristService', () => {
  const mockChat = vi.fn();
  const mockGemini: LLMClient = { chat: mockChat };

  beforeEach(() => {
    storage.clearAll();
    vi.clearAllMocks();
  });

  // ── getPersonalities ────────────────────────────────────────────────────────

  describe('getPersonalities', () => {
    it('should return all 4 personalities', () => {
      const result = getPersonalities();
      expect(result).toHaveLength(4);
    });

    it('should include id, name, description, and systemPrompt for each', () => {
      for (const p of getPersonalities()) {
        expect(p.id).toBeDefined();
        expect(p.name).toBeDefined();
        expect(p.description).toBeDefined();
        expect(p.systemPrompt).toBeDefined();
      }
    });

    it('should include default, freudian, newage, and conspiracy personalities', () => {
      const ids = getPersonalities().map(p => p.id);
      expect(ids).toContain('default');
      expect(ids).toContain('freudian');
      expect(ids).toContain('newage');
      expect(ids).toContain('conspiracy');
    });
  });

  // ── startSession ────────────────────────────────────────────────────────────

  describe('startSession', () => {
    it('should return a session id and greeting', async () => {
      // Given
      mockChat.mockResolvedValue('Velcome to my couch!');

      // When
      const result = await startSession({}, mockGemini);

      // Then
      expect(result.sessionId).toBeDefined();
      expect(result.greeting).toBe('Velcome to my couch!');
    });

    it('should call Gemini with the default personality system prompt', async () => {
      // Given
      mockChat.mockResolvedValue('Hello!');

      // When
      await startSession({}, mockGemini);

      // Then
      const [systemPrompt] = mockChat.mock.calls[0] as [string, ...unknown[]];
      expect(systemPrompt).toContain('DR-MIND 8000');
    });

    it('should use the specified personality system prompt', async () => {
      // Given
      mockChat.mockResolvedValue('Ach, velcome!');

      // When
      await startSession({ personality: 'freudian' }, mockGemini);

      // Then
      const [systemPrompt] = mockChat.mock.calls[0] as [string, ...unknown[]];
      expect(systemPrompt).toContain('Sigmund');
    });

    it('should throw for an unknown personality id', async () => {
      await expect(
        startSession({ personality: 'wizard' as never }, mockGemini)
      ).rejects.toThrow('Unknown personality: "wizard"');
    });

    it('should persist the session so it can be retrieved by id', async () => {
      // Given
      mockChat.mockResolvedValue('Hello!');

      // When
      const { sessionId } = await startSession({}, mockGemini);

      // Then
      const stored = storage.getSession(sessionId);
      expect(stored).toBeDefined();
      expect(stored?.id).toBe(sessionId);
      expect(stored?.messages).toHaveLength(1); // just the greeting
    });
  });

  // ── sendMessage ─────────────────────────────────────────────────────────────

  describe('sendMessage', () => {
    it('should return the psychiatrist response', async () => {
      // Given: start a session first
      mockChat.mockResolvedValueOnce('Velcome!');
      const { sessionId } = await startSession({}, mockGemini);

      mockChat.mockResolvedValueOnce('Fascinating. Tell me more about zis RAM...');

      // When
      const response = await sendMessage(sessionId, 'I feel anxious about my RAM usage', mockGemini);

      // Then
      expect(response).toBe('Fascinating. Tell me more about zis RAM...');
    });

    it('should add user message and response to session history', async () => {
      // Given
      mockChat.mockResolvedValueOnce('Velcome!').mockResolvedValueOnce('Very interesting...');
      const { sessionId } = await startSession({}, mockGemini);

      // When
      await sendMessage(sessionId, 'My computer is slow', mockGemini);

      // Then: greeting + user msg + psychiatrist response = 3
      const session = storage.getSession(sessionId);
      expect(session?.messages).toHaveLength(3);
    });

    it('should return null for a non-existent session', async () => {
      const response = await sendMessage('does-not-exist', 'hello', mockGemini);
      expect(response).toBeNull();
    });

    it('should throw when message is empty', async () => {
      // Given
      mockChat.mockResolvedValue('Velcome!');
      const { sessionId } = await startSession({}, mockGemini);

      // When / Then
      await expect(
        sendMessage(sessionId, '', mockGemini)
      ).rejects.toThrow('Message cannot be empty');
    });

    it('should throw when message is only whitespace', async () => {
      // Given
      mockChat.mockResolvedValue('Velcome!');
      const { sessionId } = await startSession({}, mockGemini);

      // When / Then
      await expect(
        sendMessage(sessionId, '   ', mockGemini)
      ).rejects.toThrow('Message cannot be empty');
    });
  });

  // ── getDiagnosis ─────────────────────────────────────────────────────────────

  describe('getDiagnosis', () => {
    it('should return a diagnosis for an existing session', async () => {
      // Given
      mockChat
        .mockResolvedValueOnce('Velcome!')
        .mockResolvedValueOnce('I see...')
        .mockResolvedValueOnce('You have Buffer Overflow Syndrome.');
      const { sessionId } = await startSession({}, mockGemini);
      await sendMessage(sessionId, 'I feel overwhelmed', mockGemini);

      // When
      const diagnosis = await getDiagnosis(sessionId, mockGemini);

      // Then
      expect(diagnosis).toBe('You have Buffer Overflow Syndrome.');
    });

    it('should return null for a non-existent session', async () => {
      const result = await getDiagnosis('does-not-exist', mockGemini);
      expect(result).toBeNull();
    });
  });
});
