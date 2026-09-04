import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownPreviewProps {
  content: string;
}

export const MarkdownPreview: React.FC<MarkdownPreviewProps> = ({ content }) => {
  return (
    <div style={{
      padding: '28px 36px',
      overflowY: 'auto',
      height: '100%',
      backgroundColor: 'rgba(13, 18, 28, 0.7)',
    }}>
      <div className="markdown-body" style={{ maxWidth: '820px', margin: '0 auto', fontSize: '15px', lineHeight: 1.75 }}>
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {content}
        </ReactMarkdown>
      </div>
    </div>
  );
};
