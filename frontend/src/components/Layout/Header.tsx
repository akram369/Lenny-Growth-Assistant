import React from 'react';
import { Sparkles, Cpu, Cloud, Activity, Plus, PanelLeftClose, PanelLeft, Layout } from 'lucide-react';
import { HealthStatus } from '../../types';

interface HeaderProps {
  currentProvider: string;
  onProviderChange: (provider: string) => void;
  health: HealthStatus | null;
  sidebarOpen: boolean;
  onToggleSidebar: () => void;
  onNewChat: () => void;
  hasArtifacts: boolean;
  artifactOpen: boolean;
  onToggleArtifact: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentProvider,
  onProviderChange,
  health,
  sidebarOpen,
  onToggleSidebar,
  onNewChat,
  hasArtifacts,
  artifactOpen,
  onToggleArtifact,
}) => {
  const isOllama = currentProvider === 'ollama';
  const dbChunks = health?.database?.indexed_chunks || 0;
  const isHealthy = health?.status === 'online';

  return (
    <header className="app-header">
      <div className="brand-section">
        <button
          onClick={onToggleSidebar}
          className="btn-icon"
          title={sidebarOpen ? 'Collapse Sidebar' : 'Expand Sidebar'}
        >
          {sidebarOpen ? <PanelLeftClose size={18} /> : <PanelLeft size={18} />}
        </button>

        <div className="brand-badge">
          <Sparkles size={20} />
        </div>

        <div>
          <div className="brand-title">
            The Lenny Growth Assistant
            <span className="brand-subtitle">Grounded PM AI</span>
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        {/* Model Selector Toggle */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          background: 'rgba(255, 255, 255, 0.05)',
          borderRadius: '999px',
          padding: '3px',
          border: '1px solid rgba(255, 255, 255, 0.1)',
        }}>
          <button
            onClick={() => onProviderChange('ollama')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '5px 12px',
              borderRadius: '999px',
              fontSize: '12px',
              fontWeight: 500,
              background: isOllama ? 'linear-gradient(135deg, #f59e0b, #d97706)' : 'transparent',
              color: isOllama ? '#fff' : 'var(--text-muted)',
              border: 'none',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
          >
            <Cpu size={14} />
            <span>Local: Ollama</span>
          </button>

          <button
            onClick={() => onProviderChange('cloud')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '5px 12px',
              borderRadius: '999px',
              fontSize: '12px',
              fontWeight: 500,
              background: !isOllama ? 'linear-gradient(135deg, #6366f1, #4f46e5)' : 'transparent',
              color: !isOllama ? '#fff' : 'var(--text-muted)',
              border: 'none',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
          >
            <Cloud size={14} />
            <span>Cloud: Claude/OpenAI</span>
          </button>
        </div>

        {/* Health & Knowledge Badge */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            background: 'rgba(16, 21, 34, 0.8)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            padding: '6px 12px',
            borderRadius: 'var(--radius-md)',
            fontSize: '12px',
            color: 'var(--text-muted)',
          }}
          title={`PostgreSQL pgvector: ${dbChunks} indexed transcript chunks`}
        >
          <span
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: isHealthy ? '#10b981' : '#f43f5e',
              display: 'inline-block',
              boxShadow: isHealthy ? '0 0 8px #10b981' : 'none',
            }}
          />
          <span>{dbChunks} Chunks</span>
        </div>

        {/* Artifact Toggle (if active session has artifacts) */}
        {hasArtifacts && (
          <button
            onClick={onToggleArtifact}
            className={`btn ${artifactOpen ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '6px 12px', fontSize: '12.5px' }}
            title="Toggle Side-by-Side Artifact Viewer"
          >
            <Layout size={14} />
            <span>{artifactOpen ? 'Hide Artifact' : 'View Artifact'}</span>
          </button>
        )}

        {/* New Chat CTA */}
        <button
          onClick={onNewChat}
          className="btn btn-primary"
          style={{ padding: '6px 14px', fontSize: '13px' }}
        >
          <Plus size={15} />
          <span>New Chat</span>
        </button>
      </div>
    </header>
  );
};
