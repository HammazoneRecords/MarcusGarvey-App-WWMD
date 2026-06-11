import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ChevronLeft, Share2, Bookmark, ShieldCheck, AlertCircle, Clock, History, ScrollText } from 'lucide-react';
import { getFactById } from '../services/api';
import { Fact } from '../types';
import { Button, Skeleton, Card } from '../components/ui/index';
import { SourceItem } from '../components/facts/SourceItem';
import { useStore } from '../store/useStore';
import { useAuth } from '../hooks/useAuth';
import { addSavedFact, removeSavedFact } from '../services/userData';
import { trackSync } from '../services/syncHelpers';

export const FactDetail = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [fact, setFact] = useState<Fact | null>(null);
    const [loading, setLoading] = useState(true);
    const { user } = useAuth();
    const { savedFactIds, toggleSavedFact } = useStore();

    const isSaved = id ? savedFactIds.includes(id) : false;

    const handleToggleSaved = () => {
        if (!id) return;
        const willBeSaved = !isSaved;
        toggleSavedFact(id);
        if (user?.id) {
            if (willBeSaved) trackSync(`fact-${id}`, "Couldn't sync this bookmark — saved on this device only", () => addSavedFact(id));
            else trackSync(`fact-${id}`, "Couldn't sync this bookmark — saved on this device only", () => removeSavedFact(id));
        }
    };

    useEffect(() => {
        const fetchFact = async () => {
            if (!id) return;
            setLoading(true);
            try {
                const data = await getFactById(id);
                if (data) setFact(data);
            } catch (error) {
                console.error("Failed to fetch fact", error);
            } finally {
                setLoading(false);
            }
        };
        fetchFact();
    }, [id]);

    if (loading) return <div className="space-y-6"><Skeleton className="h-10 w-32" /><Skeleton className="h-64 w-full" /><Skeleton className="h-40 w-full" /></div>;
    if (!fact) return <div className="text-center py-20">Fact not found</div>;

    return (
        <div className="space-y-8 pb-10 animate-in fade-in slide-in-from-right-4 duration-500">
            {/* Header Actions */}
            <div className="flex items-center justify-between -mx-1">
                <button type="button" onClick={() => navigate(-1)} className="p-2 -ml-2 rounded-full hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors" aria-label="Go back">
                    <ChevronLeft className="w-6 h-6" />
                </button>
                <div className="flex gap-1">
                    <button
                        type="button"
                        onClick={handleToggleSaved}
                        className={`p-2 rounded-full transition-colors ${isSaved ? 'text-primary dark:text-secondary' : 'hover:bg-zinc-100 dark:hover:bg-zinc-800'}`}
                        aria-label={isSaved ? 'Remove from saved facts' : 'Save fact'}
                    >
                        <Bookmark className={`w-6 h-6 ${isSaved ? 'fill-current' : ''}`} />
                    </button>
                    <button type="button" className="p-2 rounded-full hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors" aria-label="Share">
                        <Share2 className="w-6 h-6" />
                    </button>
                </div>
            </div>

            {/* Hero Section */}
            <section className="space-y-4">
                <div className="flex items-center gap-3">
                    <div className={`px-3 py-1 rounded-full flex items-center gap-1.5 ${fact.confidence === 'high' ? 'bg-primary/10 text-primary dark:text-secondary' : 'bg-accent/10 text-accent'
                        }`}>
                        {fact.confidence === 'high' ? <ShieldCheck className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
                        <span className="text-xs font-bold uppercase tracking-wider">{fact.confidence} Confidence</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-zinc-500 text-xs font-bold uppercase tracking-wider">
                        <Clock className="w-4 h-4" />
                        <span>{Math.ceil(fact.readingTimeSec / 60)} min read</span>
                    </div>
                </div>

                <h1 className="text-2xl md:text-3xl font-display font-bold leading-tight">
                    {fact.claim}
                </h1>

                <div className="p-6 bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm leading-relaxed">
                    <p className="text-lg text-zinc-700 dark:text-zinc-300">
                        {fact.context}
                    </p>
                </div>
            </section>

            {/* Impact Trail */}
            <section className="space-y-4">
                <div className="flex items-center gap-2 text-zinc-500">
                    <History className="w-5 h-5" />
                    <h2 className="text-sm font-bold uppercase tracking-widest">Impact Trail</h2>
                </div>
                <div className="space-y-4 relative pl-6 before:absolute before:left-[11px] before:top-2 before:bottom-2 before:w-0.5 before:bg-zinc-200 dark:before:bg-zinc-800">
                    {fact.impactTrail.map((point, i) => (
                        <div key={i} className="relative">
                            <div className="absolute -left-[21px] top-1.5 w-3 h-3 rounded-full bg-primary border-2 border-white dark:border-zinc-900" />
                            <p className="text-sm font-medium text-zinc-600 dark:text-zinc-400">
                                {point}
                            </p>
                        </div>
                    ))}
                </div>
            </section>

            {/* Receipts (Sources) */}
            <section className="space-y-4">
                <div className="flex items-center gap-2 text-zinc-500">
                    <ScrollText className="w-5 h-5" />
                    <h2 className="text-sm font-bold uppercase tracking-widest">Receipts & Evidence</h2>
                </div>
                <div className="space-y-3">
                    {fact.receipts.map((source) => (
                        <SourceItem key={source.id} source={source} />
                    ))}
                </div>
            </section>

            {/* Categories */}
            <footer className="pt-6 border-t border-zinc-100 dark:border-zinc-800">
                <div className="flex flex-wrap gap-2">
                    {fact.categories.map(cat => (
                        <span key={cat} className="px-3 py-1 bg-zinc-100 dark:bg-zinc-800 rounded-full text-xs font-bold text-zinc-500 uppercase tracking-wider">
                            {cat}
                        </span>
                    ))}
                </div>
            </footer>
        </div>
    );
};
