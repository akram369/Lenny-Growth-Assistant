import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Feather, Layers, ArrowRight, Loader2, StopCircle } from 'lucide-react';
import { Message, SourceCitation } from '../../types';
import { MessageItem } from './MessageItem';

interface ChatContainerProps {
  messages: Message[];
  isLoading: boolean;
  streamingContent: string;
  streamingSources: SourceCitation[];
  onSendMessage: (text: string) => void;
  onTriggerShip30: (topic: string) => void;
  onCancelStream?: () => void;
  onOpenArtifact: () => void;
  splitActive: boolean;
}

export const ChatContainer: React.FC<ChatContainerProps> = ({
  messages,
  isLoading,
  streamingContent,
  streamingSources,
  onSendMessage,
  onTriggerShip30,
  onCancelStream,
  onOpenArtifact,
  splitActive,
}) => {
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingContent]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputText.trim() || isLoading) return;
    onSendMessage(inputText.trim());
    setInputText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = '48px';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputText(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 180)}px`;
  };

  const samplePrompts = [
    {
      title: "Engineering Mindset",
      desc: "What did Will Larson say about coddling engineers vs. treating them as adults?",
      prompt: "What did Will Larson say about treating engineers like adult peers instead of coddling them?",
    },
    {
      title: "B2B Product-Led Growth",
      desc: "Elena Verna on PQLs vs MQLs and free-tier paywall positioning.",
      prompt: "How does Elena Verna define Product-Qualified Leads (PQLs) and where should teams place their paywall?",
    },
    {
      title: "Compounding Growth Loops",
      desc: "Brian Balfour on why funnels fail and loops compound.",
      prompt: "Explain Brian Balfour's philosophy on why funnels fail and how compounding growth loops work.",
    },
    {
      title: "Interactive Pricing Calculator",
      desc: "Generate an interactive HTML artifact for evaluating SaaS tiers.",
      prompt: "Build an interactive HTML/CSS pricing calculator artifact for evaluating SaaS tiers.",
    },
  ];

  return (
    <div className={`chat-pane ${splitActive ? 'split-active' : ''}`}>
      {/* Messages Scroll Area */}
      <div className="messages-container">
        {messages.length === 0 && !streamingContent ? (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            maxWidth: '680px',
            margin: '0 auto',
            textAlign: 'center',
            gap: '24px',
          }}>
            <div style={{
              width: '56px',
              height: '56px',
              borderRadius: 'var(--radius-lg)',
              background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(217, 119, 6, 0.1))',
              border: '1px solid rgba(245, 158, 11, 0.3)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--accent-lenny)',
              boxShadow: '0 0 30px rgba(245, 158, 11, 0.15)',
            }}>
              <Sparkles size={28} />
            </div>

            <div>
              <h2 style={{ fontSize: '24px', fontWeight: 700, color: '#fff', marginBottom: '8px' }}>
                The Lenny Growth Assistant
              </h2>
              <p style={{ fontSize: '14.5px', color: 'var(--text-secondary)', lineHeight: 1.6, maxWidth: '520px' }}>
                Ask complex product management and growth questions strictly grounded in transcripts from <strong>Lenny's Podcast</strong>.
              </p>
            </div>

            {/* Prompt Cards Grid */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: '12px',
              width: '100%',
              textAlign: 'left',
            }}>
              {samplePrompts.map((sp, idx) => (
                <div
                  key={idx}
                  onClick={() => onSendMessage(sp.prompt)}
                  style={{
                    background: 'rgba(18, 24, 38, 0.7)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-md)',
                    padding: '14px 16px',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = 'rgba(245, 158, 11, 0.4)';
                    e.currentTarget.style.background = 'rgba(26, 34, 52, 0.9)';
                    e.currentTarget.style.transform = 'translateY(-2px)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = 'var(--border-subtle)';
                    e.currentTarget.style.background = 'rgba(18, 24, 38, 0.7)';
                    e.currentTarget.style.transform = 'translateY(0)';
                  }}
                >
                  <div>
                    <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--accent-lenny-light)', marginBottom: '4px' }}>
                      {sp.title}
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                      {sp.desc}
                    </div>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '10px' }}>
                    <ArrowRight size={13} style={{ color: 'var(--text-dim)' }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((m) => (
              <MessageItem key={m.id} message={m} onOpenArtifact={onOpenArtifact} />
            ))}

            {/* Live Streaming Bubble */}
            {streamingContent && (
              <MessageItem
                message={{
                  id: 'streaming-active',
                  role: 'assistant',
                  content: streamingContent,
                  sources: streamingSources,
                  created_at: new Date().toISOString(),
                }}
                onOpenArtifact={onOpenArtifact}
              />
            )}

            {/* Loading Skeleton */}
            {isLoading && !streamingContent && (
              <div
                className="message-bubble assistant"
                style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '14px 18px' }}
              >
                <Loader2 size={16} className="animate-spin" style={{ color: 'var(--accent-lenny)' }} />
                <span style={{ fontSize: '13.5px', color: 'var(--text-muted)' }}>
                  Searching Lenny's Podcast archive & preparing grounded answer...
                </span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input & Action Bar */}
      <div className="input-container">
        {/* Quick-Action Chips */}
        <div className="quick-chips-bar">
          <button
            onClick={() => onTriggerShip30(inputText || "B2B Product-Led Sales & Monetization")}
            className="chip-btn special"
            title="Generate a 1,250-word atomic essay using Ship 30 for 30 framework"
          >
            <Feather size={13} />
            <span>Generate Ship 30 Essay</span>
          </button>

          <button
            onClick={() => onSendMessage("What did Will Larson say about treating engineers like adults vs coddling them?")}
            className="chip-btn"
          >
            <Layers size={13} />
            <span>Will Larson: Engineering Mindset</span>
          </button>

          <button
            onClick={() => onSendMessage("How does Elena Verna define Product-Qualified Leads (PQLs) vs MQLs?")}
            className="chip-btn"
          >
            <span>Elena Verna: PQLs</span>
          </button>

          <button
            onClick={() => onSendMessage("What is Brian Balfour's Four Fits framework for product growth?")}
            className="chip-btn"
          >
            <span>Brian Balfour: Four Fits</span>
          </button>
        </div>

        {/* Text Input Box */}
        <form onSubmit={handleSubmit} className="input-box">
          <textarea
            ref={textareaRef}
            className="chat-textarea"
            placeholder="Ask anything about product management, growth loops, or request a Ship 30 essay... (Shift+Enter for newline)"
            value={inputText}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            rows={1}
            disabled={isLoading}
          />

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span>Press <strong>Enter</strong> to send</span>
            </div>

            {isLoading ? (
              <button
                type="button"
                onClick={onCancelStream}
                className="btn btn-secondary"
                style={{ padding: '6px 12px', fontSize: '12px', color: '#f43f5e' }}
              >
                <StopCircle size={14} />
                <span>Stop</span>
              </button>
            ) : (
              <button
                type="submit"
                disabled={!inputText.trim()}
                className="btn btn-primary"
                style={{ padding: '7px 16px', fontSize: '13px' }}
              >
                <span>Send</span>
                <Send size={13} />
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};
