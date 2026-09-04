import React from 'react';

interface CodeViewerProps {
  code: string;
  language: string;
}

export const CodeViewer: React.FC<CodeViewerProps> = ({ code, language }) => {
  const lines = code.split('\n');

  return (
    <div style={{
      height: '100%',
      overflowY: 'auto',
      backgroundColor: '#07090e',
      padding: '16px 20px',
      fontFamily: 'var(--font-mono)',
      fontSize: '13px',
      lineHeight: 1.6,
      color: '#e2e8f0',
    }}>
      <pre style={{ margin: 0, display: 'flex', flexDirection: 'column' }}>
        {lines.map((line, idx) => (
          <div key={idx} style={{ display: 'flex' }}>
            <span style={{
              width: '42px',
              textAlign: 'right',
              paddingRight: '16px',
              color: '#475569',
              userSelect: 'none',
              flexShrink: 0,
            }}>
              {idx + 1}
            </span>
            <span style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
              {line || ' '}
            </span>
          </div>
        ))}
      </pre>
    </div>
  );
};
