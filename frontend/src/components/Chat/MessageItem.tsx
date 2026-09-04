import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Copy, Check, Sparkles, User, FileText, Code } from 'lucide-react';
import { Message } from '../../types';
import { SourceBadge } from './SourceBadge';

interface MessageItemProps {
  message: Message;
  onOpenArtifact?: () => void;
}

export const MessageItem: React.FC<MessageItemProps> = ({ message, onOpenArtifact }) => {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Clean raw artifact tags from chat view if they appear in text
  const cleanDisplayContent = (content: string) => {
    return content.replace(/<artifact\s+[^>]*>[\s\S]*?(?:<\/artifact>|$)/gi, '');
  };

  const hasArtifactTag = /<artifact\s+[^>]*>/i.test(message.content);
  const displayContent = cleanDisplayContent(message.content).trim();

  return (
    <div
      className={`message-bubble ${message.role}`}
      style={{
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
      }}
    >
      {/* Sender Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', fontWeight: 600 }}>
          {isUser ? (
            <>
              <User size={13} style={{ color: 'var(--accent-lenny)' }} />
              <span style={{ color: '#fff' }}>You</span>
            </>
          ) : (
            <>
              <Sparkles size={13} style={{ color: 'var(--accent-lenny)' }} />
              <span style={{ color: 'var(--accent-lenny-light)' }}>Lenny Growth Assistant</span>
            </>
          )}
        </div>

        <button
          onClick={handleCopy}
          className="btn-icon"
          style={{ width: '24px', height: '24px', opacity: 0.5 }}
          title="Copy message"
        >
          {copied ? <Check size={12} style={{ color: '#10b981' }} /> : <Copy size={12} />}
        </button>
      </div>

      {/* Sources Citations (if assistant and has sources) */}
      {!isUser && message.sources && message.sources.length > 0 && (
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          gap: '4px',
          padding: '6px 0',
          borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
          marginBottom: '6px',
        }}>
          <span style={{ fontSize: '11px', color: 'var(--text-dim)', marginRight: '4px' }}>
            Sources Cited:
          </span>
          {message.sources.map((s, idx) => (
            <SourceBadge key={idx} source={s} index={idx} />
          ))}
        </div>
      )}

      {/* Message Body */}
      {displayContent ? (
        <div className="markdown-body">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {displayContent}
          </ReactMarkdown>
        </div>
      ) : hasArtifactTag ? (
        <div style={{ color: 'var(--text-muted)', fontSize: '13.5px', fontStyle: 'italic' }}>
          Generated artifact deliverable available in the side-by-side viewer.
        </div>
      ) : null}

      {/* Artifact Callout Card */}
      {hasArtifactTag && (
        <div
          onClick={onOpenArtifact}
          style={{
            marginTop: '8px',
            background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.12), rgba(99, 102, 241, 0.08))',
            border: '1px solid rgba(245, 158, 11, 0.35)',
            borderRadius: 'var(--radius-md)',
            padding: '12px 16px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = 'var(--accent-lenny)';
            e.currentTarget.style.transform = 'translateY(-1px)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = 'rgba(245, 158, 11, 0.35)';
            e.currentTarget.style.transform = 'translateY(0)';
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: 'var(--radius-sm)',
              background: 'rgba(245, 158, 11, 0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--accent-lenny)',
            }}>
              {message.content.includes('type="html"') ? <Code size={16} /> : <FileText size={16} />}
            </div>
            <div>
              <div style={{ fontSize: '13px', fontWeight: 600, color: '#fff' }}>
                Generated Artifact Ready
              </div>
              <div style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>
                Click to open interactive side-by-side preview & export options
              </div>
            </div>
          </div>
          <button className="btn btn-primary" style={{ padding: '5px 12px', fontSize: '12px' }}>
            Open Viewer
          </button>
        </div>
      )}
    </div>
  );
};
