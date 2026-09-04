import React, { useState, useEffect, useRef } from 'react';
import { Header } from './components/Layout/Header';
import { Sidebar } from './components/Layout/Sidebar';
import { ChatContainer } from './components/Chat/ChatContainer';
import { ArtifactDrawer } from './components/Artifact/ArtifactDrawer';
import {
  fetchHealth,
  fetchSessions,
  fetchSession,
  deleteSession,
  streamChat,
  streamShip30,
} from './api/client';
import { Artifact, HealthStatus, Message, SessionSummary, SourceCitation } from './types';

function parseArtifactFromContent(text: string, defaultTitle = 'Generated Artifact', defaultId?: string): Artifact | null {
  const match = text.match(/<artifact\s+([^>]*?)>([\s\S]*?)(?:<\/artifact>|$)/i);
  if (!match) return null;

  const attrStr = match[1];
  const body = match[2].trim();
  const titleMatch = attrStr.match(/title=["'](.*?)["']/i);
  const typeMatch = attrStr.match(/type=["'](.*?)["']/i);
  const idMatch = attrStr.match(/identifier=["'](.*?)["']/i);

  const artifactType: 'markdown' | 'html' = (typeMatch ? typeMatch[1] : 'markdown').toLowerCase() === 'html' ? 'html' : 'markdown';
  return {
    title: titleMatch ? titleMatch[1] : defaultTitle,
    artifact_type: artifactType,
    identifier: idMatch ? idMatch[1] : (defaultId || `art-${Date.now()}`),
    content: body,
  };
}

export const App: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [activeArtifactIndex, setActiveArtifactIndex] = useState<number>(0);

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [streamingContent, setStreamingContent] = useState<string>('');
  const [streamingSources, setStreamingSources] = useState<SourceCitation[]>([]);

  const [sidebarOpen, setSidebarOpen] = useState<boolean>(true);
  const [artifactOpen, setArtifactOpen] = useState<boolean>(false);
  const [currentProvider, setCurrentProvider] = useState<string>('ollama');

  const abortControllerRef = useRef<AbortController | null>(null);

  // Load initial health and sessions on mount
  useEffect(() => {
    loadHealth();
    loadSessions();
    const interval = setInterval(loadHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadHealth = async () => {
    try {
      const h = await fetchHealth();
      setHealth(h);
      if (h.llm?.default_provider && !currentProvider) {
        setCurrentProvider(h.llm.default_provider);
      }
    } catch (e) {
      console.warn('Health check probe warning:', e);
    }
  };

  const loadSessions = async () => {
    try {
      const list = await fetchSessions();
      setSessions(list);
    } catch (e) {
      console.error('Failed to load sessions:', e);
    }
  };

  const handleSelectSession = async (sessionId: string) => {
    try {
      const detail = await fetchSession(sessionId);
      setActiveSessionId(detail.id);
      setMessages(detail.messages);

      const loadedArtifacts: Artifact[] = [...(detail.artifacts || [])];
      for (const msg of detail.messages || []) {
        const parsed = parseArtifactFromContent(msg.content);
        if (parsed && !loadedArtifacts.some((a) => (parsed.identifier && a.identifier === parsed.identifier) || a.title === parsed.title)) {
          loadedArtifacts.push(parsed);
        }
      }

      setArtifacts(loadedArtifacts);
      if (loadedArtifacts.length > 0) {
        setActiveArtifactIndex(loadedArtifacts.length - 1);
        setArtifactOpen(true);
      } else {
        setArtifactOpen(false);
      }
    } catch (e) {
      console.error(`Failed to load session ${sessionId}:`, e);
    }
  };

  const handleOpenArtifact = (art?: Artifact) => {
    if (art && art.content) {
      setArtifacts((prev) => {
        const existingIdx = prev.findIndex(
          (a) => (art.identifier && a.identifier === art.identifier) || a.title === art.title
        );
        if (existingIdx >= 0) {
          const updated = [...prev];
          updated[existingIdx] = { ...updated[existingIdx], ...art };
          setActiveArtifactIndex(existingIdx);
          return updated;
        }
        const updated = [...prev, art];
        setActiveArtifactIndex(updated.length - 1);
        return updated;
      });
    } else if (artifacts.length > 0) {
      if (activeArtifactIndex < 0 || activeArtifactIndex >= artifacts.length) {
        setActiveArtifactIndex(artifacts.length - 1);
      }
    }
    setArtifactOpen(true);
  };

  const handleNewChat = () => {
    setActiveSessionId(null);
    setMessages([]);
    setArtifacts([]);
    setStreamingContent('');
    setStreamingSources([]);
    setArtifactOpen(false);
  };

  const handleDeleteSession = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await deleteSession(sessionId);
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
      if (activeSessionId === sessionId) {
        handleNewChat();
      }
    } catch (err) {
      console.error(`Failed to delete session ${sessionId}:`, err);
    }
  };

  const handleSendMessage = async (text: string) => {
    if (isLoading) return;
    setIsLoading(true);
    setStreamingContent('');
    setStreamingSources([]);

    // Add user message to UI immediately
    const userMsg: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);

    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    let accumulatedContent = '';
    let currentSources: SourceCitation[] = [];
    let sessionIdToUse = activeSessionId;

    try {
      await streamChat(
        text,
        sessionIdToUse || undefined,
        currentProvider,
        {
          onMetadata: (meta) => {
            if (meta.session_id) {
              sessionIdToUse = meta.session_id;
              setActiveSessionId(meta.session_id);
            }
            if (meta.sources) {
              currentSources = meta.sources;
              setStreamingSources(meta.sources);
            }
          },
          onToken: (tok) => {
            accumulatedContent += tok;
            setStreamingContent(accumulatedContent);
          },
          onArtifact: (art) => {
            setArtifacts((prev) => {
              const existingIdx = prev.findIndex((a) => a.identifier === art.identifier);
              if (existingIdx >= 0) {
                const updated = [...prev];
                updated[existingIdx] = art;
                return updated;
              }
              const newArtifacts = [...prev, art];
              setActiveArtifactIndex(newArtifacts.length - 1);
              return newArtifacts;
            });
            // Automatically open artifact viewer when artifact is detected!
            setArtifactOpen(true);
          },
          onDone: () => {
            const assistantMsg: Message = {
              id: `asst-${Date.now()}`,
              role: 'assistant',
              content: accumulatedContent,
              sources: currentSources,
              created_at: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, assistantMsg]);
            setStreamingContent('');
            setStreamingSources([]);

            // Parse any artifact in accumulatedContent if onArtifact was not received
            const parsed = parseArtifactFromContent(accumulatedContent);
            if (parsed) {
              setArtifacts((prev) => {
                const idx = prev.findIndex((a) => (parsed.identifier && a.identifier === parsed.identifier) || a.title === parsed.title);
                if (idx >= 0) {
                  const updated = [...prev];
                  updated[idx] = parsed;
                  setActiveArtifactIndex(idx);
                  return updated;
                }
                const updated = [...prev, parsed];
                setActiveArtifactIndex(updated.length - 1);
                return updated;
              });
              setArtifactOpen(true);
            }

            loadSessions();
          },
          onError: (err) => {
            console.error('Streaming error:', err);
          },
        },
        abortController.signal
      );
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        const errorMsg: Message = {
          id: `err-${Date.now()}`,
          role: 'assistant',
          content: `⚠️ Communication error: ${err.message}`,
          created_at: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, errorMsg]);
      }
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  const handleTriggerShip30 = async (topic: string) => {
    if (isLoading) return;
    setIsLoading(true);
    setStreamingContent('');
    setStreamingSources([]);

    const userMsg: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: `⚡ Generate Ship 30 for 30 Essay: "${topic}"`,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);

    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    let accumulatedContent = '';
    let currentSources: SourceCitation[] = [];
    let sessionIdToUse = activeSessionId;

    try {
      await streamShip30(
        topic,
        sessionIdToUse || undefined,
        currentProvider,
        {
          onMetadata: (meta) => {
            if (meta.session_id) {
              sessionIdToUse = meta.session_id;
              setActiveSessionId(meta.session_id);
            }
            if (meta.sources) {
              currentSources = meta.sources;
              setStreamingSources(meta.sources);
            }
          },
          onToken: (tok) => {
            accumulatedContent += tok;
            setStreamingContent(accumulatedContent);
          },
          onArtifact: (art) => {
            setArtifacts((prev) => {
              const newArtifacts = [...prev, art];
              setActiveArtifactIndex(newArtifacts.length - 1);
              return newArtifacts;
            });
            setArtifactOpen(true);
          },
          onDone: () => {
            const parsed = parseArtifactFromContent(accumulatedContent, `Ship 30: ${topic}`, 'ship30-essay');
            if (parsed) {
              setArtifacts((prev) => {
                const idx = prev.findIndex((a) => (parsed.identifier && a.identifier === parsed.identifier) || a.title === parsed.title);
                if (idx >= 0) {
                  const updated = [...prev];
                  updated[idx] = parsed;
                  setActiveArtifactIndex(idx);
                  return updated;
                }
                const updated = [...prev, parsed];
                setActiveArtifactIndex(updated.length - 1);
                return updated;
              });
              setArtifactOpen(true);
            }

            const assistantMsg: Message = {
              id: `asst-${Date.now()}`,
              role: 'assistant',
              content: accumulatedContent.includes('<artifact')
                ? accumulatedContent
                : `I have synthesized an atomic Ship 30 for 30 essay on **${topic}** grounded strictly in Lenny's podcast transcripts. The essay has been mounted in your side-by-side artifact viewer on the right.`,
              sources: currentSources,
              created_at: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, assistantMsg]);
            setStreamingContent('');
            setStreamingSources([]);
            loadSessions();
          },
        },
        abortController.signal
      );
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        const errorMsg: Message = {
          id: `err-${Date.now()}`,
          role: 'assistant',
          content: `⚠️ Ship 30 generation error: ${err.message}`,
          created_at: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, errorMsg]);
      }
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  const handleCancelStream = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container" style={{ display: 'flex', flexDirection: 'column' }}>
      {/* Top Navigation */}
      <Header
        currentProvider={currentProvider}
        onProviderChange={setCurrentProvider}
        health={health}
        sidebarOpen={sidebarOpen}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        onNewChat={handleNewChat}
        hasArtifacts={artifacts.length > 0}
        artifactOpen={artifactOpen}
        onToggleArtifact={() => setArtifactOpen(!artifactOpen)}
      />

      {/* Main Dual-Pane Layout */}
      <div className="main-layout">
        {/* Sidebar History */}
        <Sidebar
          sessions={sessions}
          activeSessionId={activeSessionId}
          onSelectSession={handleSelectSession}
          onDeleteSession={handleDeleteSession}
          onNewChat={handleNewChat}
          isOpen={sidebarOpen}
        />

        {/* Center Chat View */}
        <ChatContainer
          messages={messages}
          isLoading={isLoading}
          streamingContent={streamingContent}
          streamingSources={streamingSources}
          onSendMessage={handleSendMessage}
          onTriggerShip30={handleTriggerShip30}
          onCancelStream={handleCancelStream}
          onOpenArtifact={handleOpenArtifact}
          splitActive={artifactOpen}
        />

        {/* Right Claude-Style Artifact Viewer */}
        <ArtifactDrawer
          artifacts={artifacts}
          activeArtifactIndex={activeArtifactIndex}
          onSelectArtifact={setActiveArtifactIndex}
          onClose={() => setArtifactOpen(false)}
          isOpen={artifactOpen}
        />
      </div>
    </div>
  );
};
