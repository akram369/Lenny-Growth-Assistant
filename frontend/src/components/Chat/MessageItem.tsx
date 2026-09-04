import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Copy, Check, Sparkles, User, FileText, Code } from 'lucide-react';
import { Message, Artifact } from '../../types';
import { SourceBadge } from './SourceBadge';

interface MessageItemProps {
  message: Message;
  onOpenArtifact?: (artifact?: Artifact) => void;
}

export const MessageItem: React.FC<MessageItemProps> = ({ message, onOpenArtifact }) => {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Extract artifact if present in message content
  const parsedArtifact: Artifact | null = React.useMemo(() => {
    const match = message.content.match(/<artifact\s+([^>]*?)>([\s\S]*?)(?:<\/artifact>|$)/i);
    if (!match) return null;

    const attrStr = match[1];
    const body = match[2].trim();

    const titleMatch = attrStr.match(/title=["'](.*?)["']/i);
    const typeMatch = attrStr.match(/type=["'](.*?)["']/i);
    const idMatch = attrStr.match(/identifier=["'](.*?)["']/i);

    const artifactType = (typeMatch ? typeMatch[1] : 'markdown').toLowerCase();
    return {
      title: titleMatch ? titleMatch[1] : 'Generated Artifact',
      artifact_type: artifactType === 'html' ? 'html' : 'markdown',
      identifier: idMatch ? idMatch[1] : `art-${Date.now()}`,
      content: body,
    };
  }, [message.content]);

  // Clean raw artifact tags from chat view if they appear in text
  const cleanDisplayContent = (content: string) => {
    return content.replace(/<artifact\s+[^>]*>[\s\S]*?(?:<\/artifact>|$)/gi, '');
  };

  const hasArtifactTag = parsedArtifact !== null || /<artifact\s+[^>]*>/i.test(message.content);
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
          onClick={(e) => {
            e.stopPropagation();
            if (onOpenArtifact) onOpenArtifact(parsedArtifact || undefined);
          }}
          style={{
            marginTop: '8px',
            background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.14), rgba(99, 102, 241, 0.09))',
            border: '1px solid rgba(245, 158, 11, 0.4)',
            borderRadius: 'var(--radius-md)',
            padding: '14px 18px',
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
            e.currentTarget.style.borderColor = 'rgba(245, 158, 11, 0.4)';
            e.currentTarget.style.transform = 'translateY(0)';
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: '36px',
              height: '36px',
              borderRadius: 'var(--radius-sm)',
              background: 'rgba(245, 158, 11, 0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--accent-lenny)',
              flexShrink: 0,
            }}>
              {(parsedArtifact?.artifact_type === 'html' || message.content.includes('type="html"')) ? <Code size={18} /> : <FileText size={18} />}
            </div>
            <div>
              <div style={{ fontSize: '13.5px', fontWeight: 600, color: '#fff' }}>
                {parsedArtifact?.title || 'Generated Artifact Ready'}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                Click to open interactive side-by-side preview & export options
              </div>
            </div>
          </div>
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              if (onOpenArtifact) onOpenArtifact(parsedArtifact || undefined);
            }}
            className="btn btn-primary"
            style={{ padding: '6px 14px', fontSize: '12.5px', pointerEvents: 'auto' }}
          >
            Open Viewer
          </button>
        </div>
      )}
    </div>
  );
};
