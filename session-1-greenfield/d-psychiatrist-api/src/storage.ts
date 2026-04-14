import type { Session } from './types.js';

const sessions = new Map<string, Session>();

export function createSession(session: Session): void {
  sessions.set(session.id, session);
}

export function getSession(id: string): Session | undefined {
  return sessions.get(id);
}

export function updateSession(session: Session): void {
  sessions.set(session.id, session);
}

export function clearAll(): void {
  sessions.clear();
}
