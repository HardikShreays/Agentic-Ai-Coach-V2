import React from 'react';
import ReactMarkdown from 'react-markdown';
import type { Components } from 'react-markdown';

const mdComponents: Components = {
  p: ({ children }) => (
    <p className="mb-3 last:mb-0 text-[14px] leading-[1.65] text-[#ede9f8]">{children}</p>
  ),
  ul: ({ children }) => (
    <ul className="my-3 pl-5 list-disc space-y-2 marker:text-[#f0177a] marker:text-[0.85em] last:mb-0">
      {children}
    </ul>
  ),
  ol: ({ children }) => (
    <ol className="my-3 pl-5 list-decimal space-y-2 marker:text-cyan marker:font-mono marker:text-[12px] last:mb-0">
      {children}
    </ol>
  ),
  li: ({ children }) => (
    <li className="text-[14px] leading-[1.65] text-[#e8e4f4] pl-1 [&>p]:mb-1 [&>p:last-child]:mb-0">{children}</li>
  ),
  strong: ({ children }) => (
    <strong className="font-semibold text-cyan">{children}</strong>
  ),
  em: ({ children }) => <em className="italic text-[#d4c8f0]">{children}</em>,
  a: ({ href, children }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-cyan underline decoration-cyan/40 underline-offset-2 hover:decoration-cyan"
    >
      {children}
    </a>
  ),
  h1: ({ children }) => (
    <h3 className="font-syne font-bold text-[15px] text-[#f0177a] mt-4 mb-2 first:mt-0 tracking-tight">
      {children}
    </h3>
  ),
  h2: ({ children }) => (
    <h3 className="font-syne font-bold text-[14px] text-[#f0177a] mt-4 mb-2 first:mt-0 tracking-tight">
      {children}
    </h3>
  ),
  h3: ({ children }) => (
    <h3 className="font-syne font-bold text-[13px] text-[#c4b5fd] mt-3 mb-2 first:mt-0 uppercase tracking-wider">
      {children}
    </h3>
  ),
  code: ({ className, children, ...props }) => {
    const isBlock = className?.includes('language-');
    if (isBlock) {
      return (
        <code
          className="block my-3 p-3 rounded-lg text-[13px] font-mono bg-black/35 border border-violet-500/20 overflow-x-auto text-[#e8e4f4]"
          {...props}
        >
          {children}
        </code>
      );
    }
    return (
      <code
        className="px-1.5 py-0.5 rounded-md text-[13px] font-mono bg-black/40 text-[#f9a8d4] border border-pink-500/25"
        {...props}
      >
        {children}
      </code>
    );
  },
  pre: ({ children }) => <pre className="my-0">{children}</pre>,
  blockquote: ({ children }) => (
    <blockquote className="my-3 pl-3 border-l-2 border-violet-500/50 text-[13px] text-muted italic">
      {children}
    </blockquote>
  ),
  hr: () => <hr className="my-4 border-0 h-px bg-gradient-to-r from-transparent via-pink-500/40 to-transparent" />,
};

export default function CoachMarkdown({ content }: { content: string }) {
  return (
    <div className="coach-markdown">
      <ReactMarkdown components={mdComponents}>{content}</ReactMarkdown>
    </div>
  );
}
