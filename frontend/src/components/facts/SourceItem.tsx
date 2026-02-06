import { useState } from 'react';
import { SourceRef } from '../../types';
import { ExternalLink, Book, FileText, Mic2, Archive } from 'lucide-react';
import { SourceViewerModal } from './SourceViewerModal';

const TYPE_ICONS = {
    book: Book,
    article: FileText,
    speech: Mic2,
    archive: Archive
};

export const SourceItem = ({ source }: { source: SourceRef }) => {
    const [modalOpen, setModalOpen] = useState(false);
    const Icon = TYPE_ICONS[source.type] || FileText;

    const hasExternalUrl = source.url && /^https?:\/\//i.test(source.url);
    const hasInternalSection = source.anchorId ?? source.locator;

    const handleAccessSource = () => {
        if (hasExternalUrl && !hasInternalSection) {
            window.open(source.url!, '_blank', 'noopener,noreferrer');
            return;
        }
        setModalOpen(true);
    };

    return (
        <>
            <div className="flex gap-4 p-4 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm">
                <div className="flex-shrink-0">
                    <div className="p-2 bg-zinc-100 dark:bg-zinc-800 rounded-lg">
                        <Icon className="w-5 h-5 text-zinc-500" />
                    </div>
                </div>
                <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-bold truncate">{source.title}</h4>
                    <p className="text-xs text-zinc-500 mt-0.5">
                        {source.author} • {source.year}
                        {source.page && ` • p. ${source.page}`}
                    </p>

                    {source.excerpt && (
                        <p className="mt-2 text-xs italic text-zinc-600 dark:text-zinc-400 border-l-2 border-zinc-200 dark:border-zinc-700 pl-3 leading-relaxed">
                            "{source.excerpt}"
                        </p>
                    )}

                    <button
                        type="button"
                        onClick={handleAccessSource}
                        className="mt-3 flex items-center gap-1.5 text-[10px] font-bold text-primary dark:text-secondary uppercase tracking-widest hover:underline"
                    >
                        <ExternalLink className="w-3 h-3" />
                        Access Source
                    </button>
                </div>
            </div>

            <SourceViewerModal
                source={source}
                open={modalOpen}
                onClose={() => setModalOpen(false)}
            />
        </>
    );
};
