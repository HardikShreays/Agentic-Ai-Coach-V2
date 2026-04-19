import React, { useEffect, useMemo, useRef, useState } from 'react';
import { FileText, Send } from 'lucide-react';

import type { ChatMessage } from '../../types';

import MessageBubble from './MessageBubble';
import QuickPrompts from './QuickPrompts';

const MAX_RESUME_CHARS = 12000;

export default function ChatWindow({
  chatHistory,
  isTyping,
  onSend,
  error,
}: {
  chatHistory: ChatMessage[];
  isTyping: boolean;
  onSend: (message: string, resumeText?: string) => Promise<void>;
  error: string | null;
}) {
  const [draft, setDraft] = useState('');
  const [resumeOpen, setResumeOpen] = useState(false);
  const [resumeBody, setResumeBody] = useState('');
  const [resumeFileName, setResumeFileName] = useState<string | null>(null);
  const [resumeNote, setResumeNote] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const listRef = useRef<HTMLDivElement | null>(null);

  const canSend = useMemo(() => draft.trim().length > 0 && !isTyping, [draft, isTyping]);
  const resumeChars = resumeBody.trim().length;

  useEffect(() => {
    if (!listRef.current) return;
    listRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [chatHistory.length, isTyping]);

  const applyResumeText = (text: string, fileLabel: string | null) => {
    const t = text.replace(/\r\n/g, '\n');
    if (t.length > MAX_RESUME_CHARS) {
      setResumeBody(t.slice(0, MAX_RESUME_CHARS));
      setResumeNote(`Trimmed to ${MAX_RESUME_CHARS.toLocaleString()} characters (API limit).`);
    } else {
      setResumeBody(t);
      setResumeNote(null);
    }
    setResumeFileName(fileLabel);
  };

  const clearResume = () => {
    setResumeBody('');
    setResumeFileName(null);
    setResumeNote(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const onResumeFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    e.target.value = '';
    if (!f) return;
    const nameOk = f.name.toLowerCase().endsWith('.txt');
    const typeOk = f.type === 'text/plain' || f.type === '';
    if (!nameOk && !typeOk) {
      setResumeNote('Use a .txt file, or paste resume text from a PDF/DOC.');
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      applyResumeText(String(reader.result ?? ''), f.name);
    };
    reader.readAsText(f);
  };

  const send = async (text: string) => {
    const t = text.trim();
    if (!t) return;
    setDraft('');
    const resumePayload = resumeBody.trim() ? resumeBody.trim() : undefined;
    await onSend(t, resumePayload);
  };

  const handleKeyDown: React.KeyboardEventHandler<HTMLTextAreaElement> = async (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (canSend) await send(draft);
    }
  };

  return (
    <section className="flex flex-col gap-4 acad-card" style={{ minHeight: 560 }}>
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-full flex items-center justify-center"
            style={{
              background: 'linear-gradient(135deg, rgba(240,23,122,1), rgba(139,92,246,1))',
              boxShadow: '0 0 22px rgba(240,23,122,0.35)',
            }}
          >
            <span className="font-syne font-bold text-[14px]">A</span>
          </div>
          <div className="leading-tight">
            <div className="font-syne font-bold text-[18px]">AcadCoach</div>
            <div className="font-mono text-[12px] uppercase tracking-widest text-cyan flex items-center gap-2">
              <span
                className="w-2.5 h-2.5 rounded-full"
                style={{
                  background: '#22c55e',
                  boxShadow: '0 0 12px rgba(34,197,94,0.55)',
                }}
              />
              Online · AI coach
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto pr-2">
        {chatHistory.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center gap-3 text-center py-10">
            <div className="text-muted font-mono text-[12px] uppercase tracking-widest">
              Ask your coach anything
            </div>
            <div className="text-text font-syne font-bold text-[20px]">
              Career guidance, not generic advice.
            </div>
            <div className="text-muted text-[13px] max-w-md">
              Use Predict/Roadmap context and get focused, India-market ready answers.
            </div>
          </div>
        ) : null}

        <div className="flex flex-col gap-4">
          {chatHistory.map((m, i) => (
            <MessageBubble msg={m} key={`${m.role}-${i}-${m.content.slice(0, 10)}`} />
          ))}

          {isTyping ? (
            <div className="flex justify-start">
              <div className="max-w-[70%]">
                <div
                  className="px-4 py-3 border"
                  style={{
                    background: 'rgba(255,255,255,0.05)',
                    borderColor: 'rgba(139,92,246,0.2)',
                    borderTopLeftRadius: 3,
                    borderTopRightRadius: 12,
                  }}
                >
                  <div className="flex gap-1 items-center">
                    {[0, 1, 2].map((idx) => (
                      <span
                        key={idx}
                        className="inline-block w-2 h-2 rounded-full animate-bounce"
                        style={{
                          background: '#f0177a',
                          animationDelay: `${idx * 0.2}s`,
                        }}
                      />
                    ))}
                  </div>
                </div>
                <div className="font-mono text-muted text-[11px] mt-1 text-right" />
              </div>
            </div>
          ) : null}

          <div ref={listRef} />
        </div>
      </div>

      {chatHistory.length === 0 ? (
        <div>
          <QuickPrompts onPick={(p) => send(p)} />
        </div>
      ) : null}

      {error ? <div className="text-pink font-mono text-[12px]">{error}</div> : null}

      <div className="flex flex-col gap-2 border-t border-violet-500/15 pt-3">
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => setResumeOpen((o) => !o)}
            className="inline-flex items-center gap-2 rounded-full px-3 py-1.5 font-mono text-[10px] uppercase tracking-widest transition-colors"
            style={{
              background: resumeChars ? 'rgba(240,23,122,0.15)' : 'rgba(255,255,255,0.06)',
              border: '1px solid rgba(139,92,246,0.25)',
              color: resumeChars ? '#fda4cf' : '#a8a0c0',
            }}
          >
            <FileText size={14} className="opacity-90" />
            Resume {resumeChars ? `· ${resumeChars.toLocaleString()} chars` : 'optional'}
          </button>
          {resumeChars > 0 ? (
            <button
              type="button"
              onClick={clearResume}
              className="font-mono text-[10px] uppercase tracking-widest text-muted hover:text-pink transition-colors"
            >
              Clear resume
            </button>
          ) : null}
        </div>
        {resumeOpen ? (
          <div
            className="rounded-xl p-3 flex flex-col gap-2"
            style={{
              background: 'rgba(0,0,0,0.2)',
              border: '1px solid rgba(139,92,246,0.2)',
            }}
          >
            <p className="text-muted text-[11px] leading-relaxed m-0">
              Paste plain text or upload a <span className="text-cyan">.txt</span> file. For PDF/DOC, copy the text
              here first. Your resume is sent with <strong className="text-text">each message</strong> until you clear
              it—it does not appear in the chat thread.
            </p>
            <textarea
              className="acad-textarea min-h-[100px] text-[13px]"
              placeholder="Paste your resume text…"
              value={resumeBody}
              onChange={(e) => applyResumeText(e.target.value, resumeFileName)}
              maxLength={MAX_RESUME_CHARS}
            />
            <div className="flex flex-wrap items-center gap-2">
              <input ref={fileInputRef} type="file" accept=".txt,text/plain" className="hidden" onChange={onResumeFile} />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="acad-btn acad-btn-ghost !py-2 !px-3 !text-[10px]"
              >
                Upload .txt
              </button>
              {resumeFileName ? (
                <span className="font-mono text-[10px] text-cyan truncate max-w-[200px]">{resumeFileName}</span>
              ) : null}
              <span className="font-mono text-[10px] text-muted ml-auto">
                {resumeChars.toLocaleString()} / {MAX_RESUME_CHARS.toLocaleString()}
              </span>
            </div>
            {resumeNote ? <div className="text-pink font-mono text-[11px]">{resumeNote}</div> : null}
          </div>
        ) : null}
      </div>

      <div className="flex items-end gap-3">
        <textarea
          className="acad-textarea flex-1"
          value={draft}
          placeholder="Type your question... (Enter to send, Shift+Enter for newline)"
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button
          type="button"
          disabled={!canSend}
          onClick={() => send(draft)}
          className="w-[40px] h-[40px] rounded-full flex items-center justify-center disabled:opacity-40"
          style={{
            background: '#f0177a',
            border: '1px solid rgba(240,23,122,0.6)',
            boxShadow: '0 4px 20px rgba(240,23,122,0.4)',
          }}
        >
          <Send size={18} color="#fff" />
        </button>
      </div>
    </section>
  );
}

