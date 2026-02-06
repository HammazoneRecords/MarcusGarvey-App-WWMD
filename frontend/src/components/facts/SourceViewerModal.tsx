import { useEffect, useState, useRef, type ReactNode, type RefObject } from 'react';
import { SourceRef, SourceSectionResponse } from '../../types';
import { getSourceSection } from '../../services/api';
import { X, ExternalLink, Book, FileText, Mic2, Archive } from 'lucide-react';

const TYPE_ICONS = {
    book: Book,
    article: FileText,
    speech: Mic2,
    archive: Archive
};

/**
 * Find excerpt (cited line) in page content and return React nodes: before + highlighted excerpt + after.
 * Uses exact match; if not found, returns content as-is (caller can show excerpt separately).
 */
function highlightExcerptInContent(
    content: string,
    excerpt: string,
    highlightRef: RefObject<HTMLElement>
): ReactNode {
    if (!excerpt.trim()) return content;
    const idx = content.indexOf(excerpt);
    if (idx >= 0) {
        return (
            <>
                {content.slice(0, idx)}
                <mark
                    ref={highlightRef}
                    className="bg-primary/25 dark:bg-primary/30 text-foreground rounded px-0.5 py-0.5 ring-1 ring-primary/40 scroll-mt-4"
                >
                    {excerpt}
                </mark>
                {content.slice(idx + excerpt.length)}
            </>
        );
    }
    return content;
}

interface SourceViewerModalProps {
    source: SourceRef | null;
    open: boolean;
    onClose: () => void;
}

export const SourceViewerModal = ({ source, open, onClose }: SourceViewerModalProps) => {
    const [section, setSection] = useState<SourceSectionResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const highlightRef = useRef<HTMLElement>(null);

    const anchorId = source?.anchorId ?? source?.id;
    const locator = source?.locator;
    const canFetchSection = open && source && anchorId && (locator ?? true);

    useEffect(() => {
        if (!open || !source) {
            setSection(null);
            setError(null);
            return;
        }
        if (!anchorId) {
            setSection(null);
            setError(null);
            return;
        }
        setLoading(true);
        setError(null);
        getSourceSection(anchorId, locator)
            .then((data) => {
                setSection(data);
                setError(null);
            })
            .catch((e) => {
                setSection(null);
                setError(e instanceof Error ? e.message : 'Failed to load section');
            })
            .finally(() => setLoading(false));
    }, [open, source?.id, anchorId, locator]);

    useEffect(() => {
        if (!section?.sectionContent || !source?.excerpt) return;
        const t = setTimeout(() => {
            highlightRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 100);
        return () => clearTimeout(t);
    }, [section?.sectionContent, source?.excerpt]);

    if (!open) return null;

    const Icon = source ? (TYPE_ICONS[source.type] || FileText) : FileText;
    const hasExternalUrl = source?.url && /^https?:\/\//i.test(source.url);

    return (
        <div
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200"
            onClick={onClose}
            role="dialog"
            aria-modal="true"
            aria-labelledby="source-modal-title"
        >
            <div
                className="bg-background border border-border rounded-xl shadow-xl max-w-2xl w-full max-h-[85vh] flex flex-col animate-in zoom-in-95 duration-200"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="flex items-start justify-between gap-4 p-4 border-b border-border">
                    <div className="flex gap-3 min-w-0">
                        <div className="p-2 bg-muted rounded-lg shrink-0">
                            <Icon className="w-5 h-5 text-muted-foreground" />
                        </div>
                        <div className="min-w-0">
                            <h2 id="source-modal-title" className="text-lg font-bold truncate">
                                {source?.title ?? 'Source'}
                            </h2>
                            <p className="text-sm text-muted-foreground mt-0.5">
                                {source?.author} • {source?.year}
                                {source?.page && ` • p. ${source.page}`}
                            </p>
                        </div>
                    </div>
                    <button
                        type="button"
                        onClick={onClose}
                        className="p-2 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-colors shrink-0"
                        aria-label="Close"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Body: loading / error / section content / excerpt */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {loading && (
                        <p className="text-sm text-muted-foreground">Loading section…</p>
                    )}
                    {error && (
                        <div className="space-y-2">
                            <p className="text-sm text-destructive">{error}</p>
                            {source?.excerpt && (
                                <p className="text-sm italic text-muted-foreground border-l-2 border-border pl-4">
                                    "{source.excerpt}"
                                </p>
                            )}
                        </div>
                    )}
                    {!loading && !error && section?.sectionContent && (
                        <div className="space-y-2">
                            {section.pageLabel && (
                                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                                    Page {section.pageLabel}
                                </p>
                            )}
                            {source?.excerpt && (
                                <p className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">
                                    Cited line highlighted below
                                </p>
                            )}
                            <div className="text-sm text-foreground leading-relaxed whitespace-pre-wrap border-l-2 border-primary/30 pl-4">
                                {source?.excerpt
                                    ? highlightExcerptInContent(section.sectionContent, source.excerpt, highlightRef)
                                    : section.sectionContent}
                            </div>
                        </div>
                    )}
                    {!loading && !error && !section?.sectionContent && source?.excerpt && (
                        <p className="text-sm italic text-muted-foreground border-l-2 border-border pl-4">
                            "{source.excerpt}"
                        </p>
                    )}
                    {!loading && !error && !section?.sectionContent && !source?.excerpt && (
                        <p className="text-sm text-muted-foreground">No section content available.</p>
                    )}
                </div>

                {/* Footer: Open full source link if external URL */}
                {hasExternalUrl && (
                    <div className="p-4 border-t border-border">
                        <a
                            href={source!.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
                        >
                            <ExternalLink className="w-4 h-4" />
                            Open full source
                        </a>
                    </div>
                )}
            </div>
        </div>
    );
};
