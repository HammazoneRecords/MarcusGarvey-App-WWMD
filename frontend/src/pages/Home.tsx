import { useEffect, useState } from 'react';
import { DailyCard } from '../components/home/DailyCard';
import { Gallery } from '../components/home/Gallery';
import { getDailyItem, getFacts, getGallery } from '../services/api';
import { DailyItem, Fact, GalleryItem } from '../types';
import { Button, Card, Skeleton } from '../components/ui';
import { LegalDisclaimer } from '../components/ui/LegalDisclaimer';
import { Search, MessageSquare, BookOpen, LayoutGrid, ArrowRight, Image as ImageIcon } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Home = () => {
    const [daily, setDaily] = useState<DailyItem | null>(null);
    const [featuredFact, setFeaturedFact] = useState<Fact | null>(null);
    const [gallery, setGallery] = useState<GalleryItem[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [dailyItem, allFacts, galleryItems] = await Promise.all([
                    getDailyItem(),
                    getFacts(),
                    getGallery()
                ]);
                setDaily(dailyItem);
                setFeaturedFact(allFacts[0]);
                setGallery(galleryItems);
            } catch (error) {
                console.error("Failed to fetch home data", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) {
        return (
            <div className="space-y-6">
                <Skeleton className="h-64 w-full" />
                <div className="grid grid-cols-2 gap-4">
                    <Skeleton className="h-24 w-full" />
                    <Skeleton className="h-24 w-full" />
                </div>
                <Skeleton className="h-40 w-full" />
            </div>
        );
    }

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <section>
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-sm font-bold uppercase tracking-widest text-zinc-500">Daily Reflection</h2>
                    <span className="text-xs font-medium text-zinc-400">{new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric' })}</span>
                </div>
                {daily && <DailyCard item={daily} />}
            </section>

            <section>
                <h2 className="text-sm font-bold uppercase tracking-widest text-zinc-500 mb-4">Quick Actions</h2>
                <div className="grid grid-cols-2 gap-4">
                    <Link to="/wwmd">
                        <Card className="hover:border-primary transition-colors cursor-pointer h-full flex flex-col items-center justify-center p-6 text-center">
                            <div className="p-3 bg-primary/10 rounded-full mb-3">
                                <MessageSquare className="w-6 h-6 text-primary" />
                            </div>
                            <span className="font-bold text-sm">Ask WWMD</span>
                        </Card>
                    </Link>
                    <Link to="/library">
                        <Card className="hover:border-primary transition-colors cursor-pointer h-full flex flex-col items-center justify-center p-6 text-center">
                            <div className="p-3 bg-primary/10 rounded-full mb-3">
                                <Search className="w-6 h-6 text-primary" />
                            </div>
                            <span className="font-bold text-sm">Browse Knowledge Base</span>
                        </Card>
                    </Link>
                    <Link to="/toolkit">
                        <Card className="hover:border-primary transition-colors cursor-pointer h-full flex flex-col items-center justify-center p-6 text-center">
                            <div className="p-3 bg-primary/10 rounded-full mb-3">
                                <BookOpen className="w-6 h-6 text-primary" />
                            </div>
                            <span className="font-bold text-sm">Open Toolkit</span>
                        </Card>
                    </Link>
                    <Card className="opacity-50 grayscale flex flex-col items-center justify-center p-6 text-center">
                        <div className="p-3 bg-zinc-100 rounded-full mb-3">
                            <LayoutGrid className="w-6 h-6 text-zinc-400" />
                        </div>
                        <span className="font-bold text-sm">Community</span>
                    </Card>
                </div>
            </section>

            {featuredFact && (
                <section>
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-sm font-bold uppercase tracking-widest text-zinc-500">Research Highlight</h2>
                        <Link to="/library" className="text-xs font-bold text-primary dark:text-secondary flex items-center gap-1">
                            Archives <ArrowRight className="w-3 h-3" />
                        </Link>
                    </div>
                    <Link to={`/facts/${featuredFact.id}`}>
                        <Card className="hover:shadow-lg transition-shadow">
                            <div className="flex items-center gap-2 mb-2">
                                <span className="px-2 py-0.5 bg-primary/10 text-primary dark:text-secondary text-[10px] font-bold rounded uppercase">
                                    {featuredFact.categories[0]}
                                </span>
                                <span className="text-[10px] text-zinc-400">• {Math.ceil(featuredFact.readingTimeSec / 60)}m read</span>
                            </div>
                            <h3 className="text-lg mb-2">{featuredFact.claim}</h3>
                            <p className="text-sm text-zinc-600 dark:text-zinc-400 line-clamp-2">
                                {featuredFact.context}
                            </p>
                        </Card>
                    </Link>
                </section>
            )}

            {gallery.length > 0 && (
                <section>
                    <Gallery items={gallery} />
                </section>
            )}

            <section>
                <LegalDisclaimer />
            </section>

            <footer className="pt-4 pb-10 text-center space-y-2">
                <p className="text-[10px] text-zinc-400 uppercase tracking-[0.2em]">Mindwave Jamaica • Whirlwind KB v2.0.6 • Grounded in History</p>
                <p className="text-[10px] text-zinc-500">
                    <Link to="/privacy" className="hover:text-primary underline">Privacy</Link>
                    {' · '}
                    <Link to="/terms" className="hover:text-primary underline">Terms</Link>
                </p>
            </footer>
        </div>
    );
};
