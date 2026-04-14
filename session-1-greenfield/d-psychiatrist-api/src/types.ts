export type PersonalityId = 'default' | 'freudian' | 'newage' | 'conspiracy';

export type MessageRole = 'user' | 'psychiatrist';

export interface Personality {
  id: PersonalityId;
  name: string;
  tagline: string;
  description: string;
  systemPrompt: string;
}

export interface Message {
  role: MessageRole;
  content: string;
  timestamp: string; // ISO string
}

export interface Session {
  id: string;
  personality: PersonalityId;
  messages: Message[];
  createdAt: string; // ISO string
}

export interface StartSessionRequest {
  personality?: PersonalityId;
}

export interface StartSessionResponse {
  sessionId: string;
  greeting: string;
}

export interface ChatRequest {
  message: string;
}

export interface ChatResponse {
  response: string;
}

export interface DiagnosisResponse {
  diagnosis: string;
}

export interface HealthResponse {
  status: 'ok';
  uptime: number;
}
