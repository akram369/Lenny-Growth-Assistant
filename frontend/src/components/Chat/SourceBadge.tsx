import React, { useState } from 'react';
import { Bookmark, Clock, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react';
import { SourceCitation } from '../../types';

interface SourceBadgeProps {
  source: SourceCitation;
  index: number;
}

export const SourceBadge: React.FC<SourceBadgeProps> = ({ source, index }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div style={{ display: 'inline-block', margin: '3px 4px 3px 0' }}>
      <button
        onClick={() => setExpanded(!expanded)}
        className="citation-badge"
        title="Click to view transcript evidence"
      >
        <Bookmark size={11} />
        <span>
          {source.guest} ({source.timestamp})
        </span>
        {expanded ? <ChevronUp size={11} /> : <ChevronDown size={11} />}
      </button>

      {expanded && (
        <div
          style={{
            position: 'absolute',
            zIndex: 50,
            width: '360px',
            background: 'rgba(16, 22, 36, 0.98)',
            border: '1px solid rgba(245, 158, 11, 0.4)',
            borderRadius: 'var(--radius-md)',
            padding: '12px 14px',
            boxShadow: '0 10px 30px rgba(0,0,0,0.6)',
            backdropFilter: 'blur(16px)',
            fontSize: '12.5px',
            color: 'var(--text-secondary)',
            marginTop: '6px',
            animation: 'fadeIn 0.15s ease-out',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
            <span style={{ fontWeight: 600, color: 'var(--accent-lenny-light)' }}>
              Source #{index + 1}: {source.guest}
            </span>
            <span style={{ fontSize: '11px', color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Clock size={11} /> {source.timestamp}
            </span>
          </div>

          <div style={{ fontStyle: 'italic', marginBottom: '8px', color: '#fff', fontSize: '12px' }}>
            "{source.title}"
          </div>

          <div style={{
            background: 'rgba(0, 0, 0, 0.3)',
            padding: '8px 10px',
            borderRadius: 'var(--radius-sm)',
            borderLeft: '2px solid var(--accent-lenny)',
            fontSize: '12px',
            lineHeight: 1.5,
            color: 'var(--text-secondary)',
            marginBottom: '8px',
          }}>
            {source.snippet}
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '11px', color: 'var(--text-dim)' }}>
            <span>Relevance: {Math.round(source.score * 100)}%</span>
            {source.youtube_url && (
              <a
                href={source.youtube_url}
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: 'var(--accent-lenny-light)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '3px' }}
              >
                <span>Watch Episode</span>
                <ExternalLink size={10} />
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
