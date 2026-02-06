import ReactMarkdown from 'react-markdown';

export const MarkdownRenderer = ({ content }: { content: string }) => {
    return (
        <div className="prose dark:prose-invert max-w-none prose-sm sm:prose-base 
      prose-headings:font-display prose-headings:font-bold prose-headings:text-primary dark:prose-headings:text-secondary
      prose-p:text-zinc-600 dark:prose-p:text-zinc-400 prose-p:leading-relaxed
      prose-li:text-zinc-600 dark:prose-li:text-zinc-400
      prose-strong:text-zinc-900 dark:prose-strong:text-zinc-100">
            <ReactMarkdown>{content}</ReactMarkdown>
        </div>
    );
};
