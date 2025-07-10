/**
 * MessageRenderer component for rendering chat messages with markdown support
 */

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MessageRendererProps {
  content: string;
  isUser: boolean;
}

export const MessageRenderer: React.FC<MessageRendererProps> = ({ content, isUser }) => {
  // Check if content contains markdown patterns
  const hasMarkdown = content.includes('**') || content.includes('*') || content.includes('#') || content.includes('`');

  if (!hasMarkdown || isUser) {
    // For user messages or plain text, render as is
    return <span className="text-sm">{content}</span>;
  }
 
  // For AI messages with markdown, render with ReactMarkdown
  return (
    <div className="text-sm">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Customize markdown elements to fit chat style
          h1: ({ children }) => <div className="text-base font-bold mb-2 text-gray-800">{children}</div>,
          h2: ({ children }) => <div className="text-sm font-bold mb-1 text-gray-800">{children}</div>,
          h3: ({ children }) => <div className="text-sm font-semibold mb-1 text-gray-700">{children}</div>,
          p: ({ children }) => <div className="mb-2 text-gray-700 leading-relaxed">{children}</div>,
          strong: ({ children }) => <span className="font-semibold text-gray-800">{children}</span>,
          em: ({ children }) => <span className="italic text-gray-600">{children}</span>,
          ul: ({ children }) => <ul className="list-disc ml-4 mb-2 space-y-1">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal ml-4 mb-2 space-y-1">{children}</ol>,
          li: ({ children }) => <li className="text-gray-700">{children}</li>,
          code: ({ children }) => (
            <code className="bg-blue-100 text-blue-800 px-1 py-0.5 rounded text-xs font-mono">{children}</code>
          ),
          blockquote: ({ children }) => (
            <blockquote className="border-l-2 border-blue-300 pl-2 ml-2 italic text-gray-600 bg-blue-50 py-1">{children}</blockquote>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default MessageRenderer;
