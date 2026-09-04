export interface SourceCitation {
  episode_id: string;
  guest: string;
  title: string;
  youtube_url?: string;
  timestamp: string;
  score: number;
  snippet: string;
}

export interface Artifact {
  id?: string;
  message_id?: string;
  session_id?: string;
  artifact_type: 'markdown' | 'html';
  title: string;
  identifier: string;
  content: string;
  created_at?: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceCitation[];
  created_at: string;
}

export interface SessionSummary {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface SessionDetail {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
  artifacts: Artifact[];
}

export interface ProviderStatus {
  id: string;
  name: string;
  is_default: boolean;
  status: string;
  model: string;
  available_models?: string[];
  latency_ms?: number;
  error?: string;
}

export interface HealthStatus {
  status: string;
  app_name: string;
  environment: string;
  database: {
    status: string;
    pgvector_enabled: boolean;
    indexed_chunks: number;
  };
  llm: {
    default_provider: string;
    active_model: string;
    providers: ProviderStatus[];
  };
  embeddings: {
    model: string;
    dimension: number;
  };
}
