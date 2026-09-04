import React, { useState } from 'react';
import { Eye, Code, Copy, Download, X, Check, FileText, Globe } from 'lucide-react';
import { Artifact } from '../../types';
import { MarkdownPreview } from './MarkdownPreview';
import { HtmlSandbox } from './HtmlSandbox';
import { CodeViewer } from './CodeViewer';

interface ArtifactDrawerProps {
  artifacts: Artifact[];
  activeArtifactIndex: number;
  onSelectArtifact: (index: number) => void;
  onClose: () => void;
  isOpen: boolean;
}

export const ArtifactDrawer: React.FC<ArtifactDrawerProps> = ({
  artifacts,
  activeArtifactIndex,
  onSelectArtifact,
  onClose,
  isOpen,
}) => {
  const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview');
  const [copied, setCopied] = useState(false);

  if (!isOpen || artifacts.length === 0) return null;

  const currentArtifact = artifacts[activeArtifactIndex] || artifacts[0];
  const isHtml = currentArtifact.artifact_type === 'html';

  const handleCopy = () => {
    navigator.clipboard.writeText(currentArtifact.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const ext = isHtml ? 'html' : 'md';
    const mime = isHtml ? 'text/html' : 'text/markdown';
    const blob = new Blob([currentArtifact.content], { type: `${mime};charset=utf-8` });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${currentArtifact.identifier || 'artifact'}.${ext}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="artifact-drawer">
      {/* Top Header & Tab Controls */}
      <div style={{
        padding: '12px 18px',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: 'rgba(10, 13, 20, 0.7)',
      }}>
        {/* Left: Artifact Title & Type */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', overflow: 'hidden' }}>
          <div style={{
            width: '28px',
            height: '28px',
            borderRadius: 'var(--radius-sm)',
            background: isHtml ? 'rgba(99, 102, 241, 0.2)' : 'rgba(245, 158, 11, 0.2)',
            color: isHtml ? '#818cf8' : 'var(--accent-lenny)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}>
            {isHtml ? <Globe size={15} /> : <FileText size={15} />}
          </div>

          <div style={{ overflow: 'hidden' }}>
            <div style={{
              fontSize: '13.5px',
              fontWeight: 600,
              color: '#fff',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}>
              {currentArtifact.title}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-dim)', textTransform: 'uppercase' }}>
              {currentArtifact.artifact_type} Artifact
            </div>
          </div>
        </div>

        {/* Right: Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          {/* Artifact Selector Dropdown (if multiple) */}
          {artifacts.length > 1 && (
            <select
              value={activeArtifactIndex}
              onChange={(e) => onSelectArtifact(Number(e.target.value))}
              style={{
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-secondary)',
                padding: '4px 8px',
                borderRadius: 'var(--radius-sm)',
                fontSize: '12px',
                outline: 'none',
              }}
            >
              {artifacts.map((a, i) => (
                <option key={i} value={i} style={{ background: '#111622', color: '#fff' }}>
                  {a.title}
                </option>
              ))}
            </select>
          )}

          {/* Tab Switcher */}
          <div style={{
            display: 'flex',
            background: 'rgba(255, 255, 255, 0.04)',
            borderRadius: 'var(--radius-sm)',
            padding: '2px',
            border: '1px solid var(--border-subtle)',
          }}>
            <button
              onClick={() => setActiveTab('preview')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '5px',
                padding: '4px 10px',
                borderRadius: 'var(--radius-sm)',
                fontSize: '12px',
                border: 'none',
                background: activeTab === 'preview' ? 'rgba(245, 158, 11, 0.2)' : 'transparent',
                color: activeTab === 'preview' ? 'var(--accent-lenny-light)' : 'var(--text-muted)',
                cursor: 'pointer',
              }}
            >
              <Eye size={13} />
              <span>Preview</span>
            </button>

            <button
              onClick={() => setActiveTab('code')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '5px',
                padding: '4px 10px',
                borderRadius: 'var(--radius-sm)',
                fontSize: '12px',
                border: 'none',
                background: activeTab === 'code' ? 'rgba(245, 158, 11, 0.2)' : 'transparent',
                color: activeTab === 'code' ? 'var(--accent-lenny-light)' : 'var(--text-muted)',
                cursor: 'pointer',
              }}
            >
              <Code size={13} />
              <span>Code</span>
            </button>
          </div>

          {/* Copy Button */}
          <button
            onClick={handleCopy}
            className="btn-icon"
            title="Copy artifact source code"
          >
            {copied ? <Check size={14} style={{ color: '#10b981' }} /> : <Copy size={14} />}
          </button>

          {/* Download Button */}
          <button
            onClick={handleDownload}
            className="btn-icon"
            title="Download artifact file"
          >
            <Download size={14} />
          </button>

          {/* Close Button */}
          <button
            onClick={onClose}
            className="btn-icon"
            title="Close Artifact Viewer"
          >
            <X size={15} />
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div style={{ flex: 1, overflow: 'hidden', position: 'relative' }}>
        {activeTab === 'preview' ? (
          isHtml ? (
            <HtmlSandbox htmlContent={currentArtifact.content} title={currentArtifact.title} />
          ) : (
            <MarkdownPreview content={currentArtifact.content} />
          )
        ) : (
          <CodeViewer code={currentArtifact.content} language={currentArtifact.artifact_type} />
        )}
      </div>
    </div>
  );
};
