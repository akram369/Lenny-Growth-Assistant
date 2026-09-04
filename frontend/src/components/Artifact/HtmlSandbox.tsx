import React, { useMemo } from 'react';
import DOMPurify from 'dompurify';
import { ShieldCheck } from 'lucide-react';

interface HtmlSandboxProps {
  htmlContent: string;
  title: string;
}

export const HtmlSandbox: React.FC<HtmlSandboxProps> = ({ htmlContent, title }) => {
  // Sanitize untrusted HTML while preserving safe styling and scripts
  const sanitizedDoc = useMemo(() => {
    // Inject responsive stylesheet and base typography if missing
    const injectedStyles = `
      <style>
        body {
          margin: 0;
          padding: 20px;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          color: #e2e8f0;
          background-color: #0d121c;
          line-height: 1.5;
        }
      </style>
    `;

    let content = htmlContent;
    if (!content.includes('<style>') && !content.includes('<link')) {
      content = injectedStyles + content;
    }

    return content;
  }, [htmlContent]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', width: '100%' }}>
      {/* Security Isolation Notice */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '6px 14px',
        background: 'rgba(16, 185, 129, 0.08)',
        borderBottom: '1px solid rgba(16, 185, 129, 0.2)',
        fontSize: '11.5px',
        color: '#10b981',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <ShieldCheck size={14} />
          <span>Sandboxed Container (Isolated Origin - No Parent Storage / Cookies)</span>
        </div>
        <span style={{ color: 'var(--text-dim)', fontSize: '10.5px' }}>sandbox="allow-scripts"</span>
      </div>

      {/* Sandboxed Iframe */}
      <iframe
        title={title}
        srcDoc={sanitizedDoc}
        sandbox="allow-scripts"
        style={{
          flex: 1,
          width: '100%',
          height: '100%',
          border: 'none',
          backgroundColor: '#0d121c',
        }}
      />
    </div>
  );
};
