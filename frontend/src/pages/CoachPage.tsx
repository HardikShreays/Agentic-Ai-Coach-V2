import React, { useState, useEffect } from 'react';

import { fetchSessionContext, sendCoachMessage } from '../api/client';
import { useSessionStore } from '../store/useSessionStore';
import { useAuthStore } from '../store/useAuthStore';

import ChatSidebar from '../components/coach/ChatSidebar';
import ChatWindow from '../components/coach/ChatWindow';

export default function CoachPage() {
  const user = useAuthStore((s) => s.user);
  const chatHistory = useSessionStore((s) => s.chatHistory);
  const addMessage = useSessionStore((s) => s.addMessage);
  const clearChat = useSessionStore((s) => s.clearChat);
  const activeTopic = useSessionStore((s) => s.activeTopic);
  const setActiveTopic = useSessionStore((s) => s.setActiveTopic);
  const getSessionContext = useSessionStore((s) => s.getSessionContext);
  const dbSessionContext = useSessionStore((s) => s.dbSessionContext);
  const setDbSessionContext = useSessionStore((s) => s.setDbSessionContext);

  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sessionContext = dbSessionContext ?? getSessionContext();

  useEffect(() => {
    if (!user) return;
    let alive = true;
    (async () => {
      try {
        const ctx = await fetchSessionContext();
        if (!alive) return;
        setDbSessionContext(ctx);
      } catch {
        // If context can’t be fetched, keep existing in-session context.
      }
    })();
    return () => {
      alive = false;
    };
  }, [user, setDbSessionContext]);

  const onSend = async (text: string, resumeText?: string) => {
    if (isTyping) return;
    const trimmed = text.trim();
    if (!trimmed) return;

    setError(null);
    addMessage({ role: 'user', content: trimmed });

    setIsTyping(true);
    try {
      const resp = await sendCoachMessage({
        message: trimmed,
        history: chatHistory,
        topic: activeTopic,
        sessionContext,
        resumeText: resumeText?.trim() || undefined,
      });

      addMessage({ role: 'assistant', content: resp.reply });
    } catch (e: any) {
      const detail = e?.response?.data?.detail || e?.message || 'Coach failed';
      addMessage({
        role: 'assistant',
        content: `Sorry — ${detail}`,
      });
      setError(detail);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="grid grid-cols-[255px_1fr] gap-6 max-[660px]:grid-cols-1">
      <ChatSidebar
        activeTopic={activeTopic}
        onSelectTopic={(t) => setActiveTopic(t)}
        sessionContext={sessionContext}
        onClearChat={clearChat}
      />
      <ChatWindow
        chatHistory={chatHistory}
        isTyping={isTyping}
        onSend={onSend}
        error={error}
      />
    </div>
  );
}

