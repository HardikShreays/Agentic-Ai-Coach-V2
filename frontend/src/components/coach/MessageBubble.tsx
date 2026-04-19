import React, { useMemo } from 'react';

import type { ChatMessage } from '../../types';
import CoachMarkdown from './CoachMarkdown';

function formatTime(d: Date) {
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

export default function MessageBubble({ msg }: { msg: ChatMessage }) {
  const nowLabel = useMemo(() => formatTime(new Date()), [msg.content]);

  const isUser = msg.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className="max-w-[85%]">
        <div
          className="px-4 py-3 border"
          style={{
            background: isUser ? 'rgba(240,23,122,1)' : 'rgba(255,255,255,0.06)',
            color: isUser ? '#fff' : '#ede9f8',
            borderColor: isUser ? 'rgba(240,23,122,0.5)' : 'rgba(139,92,246,0.28)',
            borderTopLeftRadius: isUser ? 12 : 3,
            borderTopRightRadius: isUser ? 3 : 12,
            boxShadow: isUser ? undefined : 'inset 0 1px 0 rgba(255,255,255,0.04)',
          }}
        >
          {isUser ? (
            <div className="whitespace-pre-wrap text-[14px] leading-relaxed">{msg.content}</div>
          ) : (
            <CoachMarkdown content={msg.content} />
          )}
        </div>
        <div className="font-mono text-muted text-[11px] mt-1 text-right">{nowLabel}</div>
      </div>
    </div>
  );
}

