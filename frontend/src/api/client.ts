import { Artifact, HealthStatus, SessionDetail, SessionSummary } from '../types';

const BASE_URL = ''; // Relative path leverages Vite proxy to backend

export async function fetchHealth(): Promise<HealthStatus> {
  const res = await fetch(`${BASE_URL}/api/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return res.json();
}

export async function fetchSessions(): Promise<SessionSummary[]> {
  const res = await fetch(`${BASE_URL}/api/sessions`);
  if (!res.ok) throw new Error(`Fetch sessions failed: ${res.status}`);
  return res.json();
}

export async function fetchSession(sessionId: string): Promise<SessionDetail> {
  const res = await fetch(`${BASE_URL}/api/sessions/${sessionId}`);
  if (!res.ok) throw new Error(`Fetch session ${sessionId} failed: ${res.status}`);
  return res.json();
}

export async function createSession(title?: string): Promise<SessionSummary> {
  const res = await fetch(`${BASE_URL}/api/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: title || 'New Growth Session' }),
  });
  if (!res.ok) throw new Error(`Create session failed: ${res.status}`);
  return res.json();
}

export async function deleteSession(sessionId: string): Promise<void> {
  const res = await fetch(`${BASE_URL}/api/sessions/${sessionId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error(`Delete session failed: ${res.status}`);
}

export interface StreamChatHandlers {
  onMetadata?: (metadata: any) => void;
  onToken?: (token: string) => void;
  onArtifact?: (artifact: Artifact) => void;
  onDone?: (data: any) => void;
  onError?: (err: any) => void;
}

export async function streamChat(
  message: string,
  sessionId?: string,
  provider?: string,
  handlers: StreamChatHandlers = {},
  signal?: AbortSignal
): Promise<void> {
  const res = await fetch(`${BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(provider ? { 'X-LLM-Provider': provider } : {}),
    },
    body: JSON.stringify({
      message,
      session_id: sessionId,
      provider,
    }),
    signal,
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Chat request failed (${res.status}): ${errText}`);
  }

  await parseSSE(res, handlers);
}

export async function streamShip30(
  topic: string,
  sessionId?: string,
  provider?: string,
  handlers: StreamChatHandlers = {},
  signal?: AbortSignal
): Promise<void> {
  const res = await fetch(`${BASE_URL}/api/skills/ship30`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(provider ? { 'X-LLM-Provider': provider } : {}),
    },
    body: JSON.stringify({
      topic,
      session_id: sessionId,
      provider,
    }),
    signal,
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Ship 30 request failed (${res.status}): ${errText}`);
  }

  await parseSSE(res, handlers);
}

async function parseSSE(response: Response, handlers: StreamChatHandlers) {
  if (!response.body) return;
  const reader = response.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let buffer = '';

  let currentEvent = 'message';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;

        if (trimmed.startsWith('event:')) {
          currentEvent = trimmed.slice(6).trim();
        } else if (trimmed.startsWith('data:')) {
          const rawData = trimmed.slice(5).trim();
          try {
            const parsed = JSON.parse(rawData);
            if (currentEvent === 'metadata' && handlers.onMetadata) {
              handlers.onMetadata(parsed);
            } else if (currentEvent === 'token' && handlers.onToken) {
              handlers.onToken(parsed.token);
            } else if (currentEvent === 'artifact' && handlers.onArtifact) {
              handlers.onArtifact(parsed);
            } else if (currentEvent === 'done' && handlers.onDone) {
              handlers.onDone(parsed);
            } else if (currentEvent === 'error' && handlers.onError) {
              handlers.onError(parsed);
            }
          } catch (e) {
            // raw string data
            if (currentEvent === 'token' && handlers.onToken) {
              handlers.onToken(rawData);
            }
          }
        }
      }
    }
  } catch (err) {
    if (handlers.onError) handlers.onError(err);
    throw err;
  }
}
