import React from 'react';
import { MessageSquare, Trash2, Plus, Podcast, ExternalLink } from 'lucide-react';
import { SessionSummary } from '../../types';

interface SidebarProps {
  sessions: SessionSummary[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onDeleteSession: (id: string, e: React.MouseEvent) => void;
  onNewChat: () => void;
  isOpen: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  activeSessionId,
  onSelectSession,
  onDeleteSession,
  onNewChat,
  isOpen,
}) => {
  if (!isOpen) return null;

  return (
    <aside className="app-sidebar">
      {/* Top Action */}
      <div style={{ padding: '16px', borderBottom: '1px solid var(--border-subtle)' }}>
        <button
          onClick={onNewChat}
          style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            padding: '10px 16px',
            borderRadius: 'var(--radius-md)',
            background: 'rgba(245, 158, 11, 0.12)',
            border: '1px solid rgba(245, 158, 11, 0.3)',
            color: 'var(--accent-lenny-light)',
            fontSize: '13.5px',
            fontWeight: 500,
            cursor: 'pointer',
            transition: 'all 0.2s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'rgba(245, 158, 11, 0.2)';
            e.currentTarget.style.borderColor = 'var(--accent-lenny)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'rgba(245, 158, 11, 0.12)';
            e.currentTarget.style.borderColor = 'rgba(245, 158, 11, 0.3)';
          }}
        >
          <Plus size={16} />
          <span>New Growth Session</span>
        </button>
      </div>

      {/* Session List */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '12px 10px' }}>
        <div style={{
          fontSize: '11px',
          fontWeight: 600,
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          color: 'var(--text-dim)',
          padding: '6px 10px 10px',
        }}>
          Recent Discussions ({sessions.length})
        </div>

        {sessions.length === 0 ? (
          <div style={{ padding: '24px 12px', textAlign: 'center', color: 'var(--text-dim)', fontSize: '13px' }}>
            No sessions yet.<br />Ask a PM growth question to begin!
          </div>
        ) : (
          sessions.map((s) => {
            const isActive = s.id === activeSessionId;
            return (
              <div
                key={s.id}
                onClick={() => onSelectSession(s.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '10px 12px',
                  borderRadius: 'var(--radius-md)',
                  marginBottom: '4px',
                  cursor: 'pointer',
                  background: isActive ? 'rgba(245, 158, 11, 0.14)' : 'transparent',
                  border: `1px solid ${isActive ? 'rgba(245, 158, 11, 0.35)' : 'transparent'}`,
                  color: isActive ? '#fff' : 'var(--text-secondary)',
                  transition: 'all 0.15s ease',
                }}
                onMouseEnter={(e) => {
                  if (!isActive) e.currentTarget.style.background = 'rgba(255, 255, 255, 0.04)';
                }}
                onMouseLeave={(e) => {
                  if (!isActive) e.currentTarget.style.background = 'transparent';
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', overflow: 'hidden' }}>
                  <MessageSquare size={15} style={{ color: isActive ? 'var(--accent-lenny)' : 'var(--text-dim)', flexShrink: 0 }} />
                  <span style={{
                    fontSize: '13px',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    fontWeight: isActive ? 600 : 400,
                  }}>
                    {s.title}
                  </span>
                </div>

                <button
                  onClick={(e) => onDeleteSession(s.id, e)}
                  className="btn-icon"
                  style={{ width: '26px', height: '26px', opacity: isActive ? 0.8 : 0.4 }}
                  title="Delete Session"
                >
                  <Trash2 size={13} />
                </button>
              </div>
            );
          })
        )}
      </div>

      {/* Footer Info */}
      <div style={{
        padding: '14px 16px',
        borderTop: '1px solid var(--border-subtle)',
        fontSize: '11.5px',
        color: 'var(--text-dim)',
        background: 'rgba(10, 13, 20, 0.5)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px', color: 'var(--text-muted)' }}>
          <Podcast size={14} style={{ color: 'var(--accent-lenny)' }} />
          <span style={{ fontWeight: 500 }}>Lenny's Archive</span>
        </div>
        <a
          href="https://github.com/ChatPRD/lennys-podcast-transcripts"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            color: 'var(--text-dim)',
            textDecoration: 'none',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            fontSize: '11px',
          }}
        >
          <span>ChatPRD Transcripts</span>
          <ExternalLink size={10} />
        </a>
      </div>
    </aside>
  );
};
