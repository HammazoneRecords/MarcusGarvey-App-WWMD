import { useStore } from '../store/useStore';
import { Card, Button, ThemeToggle } from '../components/ui/index';
import { Shield, Database, Info, Settings2, Moon, Sun, Download, History } from 'lucide-react';

export const Profile = () => {
    const { theme, savedFactIds, toolkitEdits, recentWWMDIds } = useStore();

    const toolkitEditsCount = Object.keys(toolkitEdits).length;

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="mb-8">
                <h1 className="text-3xl font-display font-bold mb-2">My Compass</h1>
                <p className="text-zinc-600 dark:text-zinc-400">
                    Manage your saved insights and app configuration.
                </p>
            </div>

            {/* Stats Section */}
            <section className="grid grid-cols-2 gap-4">
                <Card className="flex flex-col items-center justify-center p-6 text-center bg-zinc-50 dark:bg-zinc-800/50">
                    <span className="text-3xl font-display font-bold text-primary dark:text-secondary mb-1">
                        {savedFactIds.length}
                    </span>
                    <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-400">Saved Facts</span>
                </Card>
                <Card className="flex flex-col items-center justify-center p-6 text-center bg-zinc-50 dark:bg-zinc-800/50">
                    <span className="text-3xl font-display font-bold text-primary dark:text-secondary mb-1">
                        {toolkitEditsCount}
                    </span>
                    <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-400">Custom Templates</span>
                </Card>
            </section>

            {/* Settings Section */}
            <section className="space-y-4">
                <div className="flex items-center gap-2 text-zinc-500">
                    <Settings2 className="w-5 h-5" />
                    <h2 className="text-sm font-bold uppercase tracking-widest">Settings</h2>
                </div>

                <div className="space-y-3">
                    <Card className="p-4 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-zinc-100 dark:bg-zinc-800 rounded-lg text-zinc-500">
                                {theme === 'light' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
                            </div>
                            <div>
                                <p className="text-sm font-bold">Display Mode</p>
                                <p className="text-[10px] text-zinc-500 uppercase font-medium">{theme} mode active</p>
                            </div>
                        </div>
                        <ThemeToggle />
                    </Card>

                    <Card className="p-4 flex items-center justify-between opacity-60">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-zinc-100 dark:bg-zinc-800 rounded-lg text-zinc-500">
                                <Download className="w-5 h-5" />
                            </div>
                            <div>
                                <p className="text-sm font-bold">Offline Pack</p>
                                <p className="text-[10px] text-zinc-500 uppercase font-medium">Coming Soon</p>
                            </div>
                        </div>
                        <div className="w-12 h-6 bg-zinc-200 dark:bg-zinc-700 rounded-full relative cursor-not-allowed">
                            <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full" />
                        </div>
                    </Card>
                </div>
            </section>

            {/* WWMD History Mini */}
            <section className="space-y-4">
                <div className="flex items-center gap-2 text-zinc-500">
                    <History className="w-5 h-5" />
                    <h2 className="text-sm font-bold uppercase tracking-widest">Recent Lens Activity</h2>
                </div>
                {recentWWMDIds.length > 0 ? (
                    <div className="space-y-2">
                        {recentWWMDIds.slice().reverse().map((timestamp, i) => (
                            <div key={i} className="text-sm p-3 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl flex items-center justify-between">
                                <span className="text-zinc-500">{new Date(timestamp).toLocaleDateString()}</span>
                                <span className="font-bold text-[10px] text-primary dark:text-secondary uppercase">Analysis Session</span>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="text-sm text-zinc-400 italic">No recent sessions.</p>
                )}
            </section>

            {/* About Section */}
            <section className="space-y-4">
                <div className="flex items-center gap-2 text-zinc-500">
                    <Info className="w-5 h-5" />
                    <h2 className="text-sm font-bold uppercase tracking-widest">About Garvey Compass</h2>
                </div>
                <Card className="p-6 space-y-4">
                    <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed">
                        Garvey Compass is a tribute to the legacy of Marcus Mosiah Garvey. This tool is designed to provide accessible, source-grounded insights into organization building, economic self-reliance, and Pan-African philosophy.
                    </p>
                    <div className="flex items-start gap-3 p-4 bg-primary/5 dark:bg-primary/10 rounded-xl border border-primary/10">
                        <Shield className="w-5 h-5 text-primary dark:text-secondary flex-shrink-0 mt-0.5" />
                        <div>
                            <p className="text-xs font-bold text-primary dark:text-secondary mb-1">Data Disclaimer</p>
                            <p className="text-[11px] text-zinc-600 dark:text-zinc-400 leading-relaxed">
                                Garvey Lens is a source-grounded counsel assistant, not a personal impersonation. All responses are derived from documented speeches, books, and archival records.
                            </p>
                        </div>
                    </div>
                </Card>
            </section>

            <footer className="pt-4 pb-20 text-center space-y-2">
                <p className="text-[10px] text-zinc-400 uppercase tracking-widest">Project: Marcus Garvey Heritage</p>
                <p className="text-[9px] text-zinc-500">Built with respect for the archives.</p>
            </footer>
        </div>
    );
};
