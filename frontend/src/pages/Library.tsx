import { useState, useEffect } from 'react';
import { Search, SlidersHorizontal, Target, X } from 'lucide-react';
import { useStore } from '../store/useStore';
import { LensResultCard } from '../components/wwmd/LensResultCard';
import { ResponseView } from '../components/wwmd/ResponseView';
import { getFacts } from '../services/api';
import { Fact, WWMDResponse } from '../types';
import { FactCard } from '../components/facts/FactCard';
import { Chip, Skeleton, Card } from '../components/ui/index';

const CATEGORIES = ['All', 'Lens Results', 'Economics', 'Culture', 'History', 'Globalism', 'Education', 'Philosophy'];

export const Library = () => {
    const [facts, setFacts] = useState<Fact[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [activeCategory, setActiveCategory] = useState('All');
    const [isFilterOpen, setIsFilterOpen] = useState(false);
    const [selectedLensResult, setSelectedLensResult] = useState<WWMDResponse | null>(null);
    const savedLensResults = useStore((state) => state.savedLensResults);

    useEffect(() => {
        const fetchFacts = async () => {
            setLoading(true);
            try {
                const filters = {
                    search: searchQuery,
                    category: activeCategory === 'All' ? undefined : activeCategory,
                };
                const data = await getFacts(filters);
                setFacts(data);
            } catch (error) {
                console.error("Failed to fetch facts", error);
            } finally {
                setLoading(false);
            }
        };

        fetchFacts();
    }, [searchQuery, activeCategory]);

    return (
        <div className="space-y-6">
            {/* Search Bar */}
            <div className="relative group">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-400 group-focus-within:text-primary transition-colors" />
                <input
                    type="text"
                    placeholder="Search claims or events..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-12 pr-4 py-4 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all text-base"
                />
            </div>

            {/* Category Chips */}
            <div className="flex overflow-x-auto pb-2 gap-2 no-scrollbar">
                {CATEGORIES.map((cat) => (
                    <Chip
                        key={cat}
                        label={cat}
                        active={activeCategory === cat}
                        onClick={() => setActiveCategory(cat)}
                    />
                ))}
            </div>

            {/* Filter Stats/Actions */}
            <div className="flex items-center justify-between px-1">
                <p className="text-xs font-bold text-zinc-500 uppercase tracking-widest">
                    {loading ? 'Searching...' : `${facts.length} Verified Claims`}
                </p>
                <button
                    onClick={() => setIsFilterOpen(!isFilterOpen)}
                    className="flex items-center gap-2 text-xs font-bold text-primary dark:text-secondary uppercase tracking-widest"
                >
                    <SlidersHorizontal className="w-4 h-4" />
                    More Filters
                </button>
            </div>

            {/* More Filters Panel (Placeholder) */}
            {isFilterOpen && (
                <Card className="bg-zinc-50 dark:bg-zinc-800/50 border-dashed animate-in fade-in slide-in-from-top-2 duration-300">
                    <div className="grid grid-cols-2 gap-4">
                        <label className="flex items-center gap-3 cursor-pointer">
                            <input type="checkbox" className="w-5 h-5 rounded border-zinc-300 text-primary focus:ring-primary" checked readOnly />
                            <span className="text-sm font-medium">Verified Only</span>
                        </label>
                        <label className="flex items-center gap-3 cursor-pointer">
                            <input type="checkbox" className="w-5 h-5 rounded border-zinc-300 text-primary focus:ring-primary" readOnly />
                            <span className="text-sm font-medium">Primary Sources</span>
                        </label>
                        <label className="flex items-center gap-3 cursor-pointer">
                            <input type="checkbox" className="w-5 h-5 rounded border-zinc-300 text-primary focus:ring-primary" readOnly />
                            <span className="text-sm font-medium">Disputed</span>
                        </label>
                    </div>
                </Card>
            )}

            {/* Results */}
            <div className="space-y-4">
                {loading ? (
                    Array.from({ length: 4 }).map((_, i) => (
                        <Skeleton key={i} className="h-40 w-full" />
                    ))
                ) : activeCategory === 'Lens Results' ? (
                    savedLensResults.length > 0 ? (
                        savedLensResults.map((res, i) => (
                            <LensResultCard
                                key={i}
                                result={res}
                                onClick={() => setSelectedLensResult(res)}
                            />
                        ))
                    ) : (
                        <div className="text-center py-20 text-muted-foreground">
                            <Target className="w-12 h-12 mx-auto mb-3 opacity-20" />
                            <h3>No saved analyses yet</h3>
                            <p className="text-xs mt-1">Visit the WWMD page to generate one.</p>
                        </div>
                    )
                ) : facts.length > 0 ? (
                    facts.map((fact) => (
                        <FactCard key={fact.id} fact={fact} />
                    ))
                ) : (
                    <div className="text-center py-20">
                        <div className="inline-flex p-4 bg-zinc-100 dark:bg-zinc-800 rounded-full mb-4">
                            <Search className="w-8 h-8 text-zinc-400" />
                        </div>
                        <h3 className="text-lg">No findings match your search</h3>
                        <p className="text-sm text-zinc-500 max-w-[200px] mx-auto mt-2">
                            Try adjusting your filters or search terms.
                        </p>
                    </div>
                )}
            </div>

            {/* Lens result detail modal */}
            {selectedLensResult && (
                <div
                    className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-200"
                    onClick={() => setSelectedLensResult(null)}
                    role="dialog"
                    aria-modal="true"
                    aria-labelledby="lens-detail-title"
                >
                    <div
                        className="bg-background border border-border rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto animate-in zoom-in-95 duration-200"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div className="sticky top-0 z-10 flex items-center justify-between p-4 border-b border-border bg-background">
                            <h2 id="lens-detail-title" className="text-sm font-bold uppercase tracking-widest text-zinc-500">
                                Lens Analysis
                            </h2>
                            <button
                                type="button"
                                onClick={() => setSelectedLensResult(null)}
                                className="p-2 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
                                aria-label="Close"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <div className="p-4">
                            <ResponseView
                                response={selectedLensResult}
                                onReset={() => setSelectedLensResult(null)}
                            />
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
