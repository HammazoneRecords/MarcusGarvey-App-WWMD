import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useStore } from '../store/useStore';
import { useAuth } from '../hooks/useAuth';
import { Card, Button, ThemeToggle } from '../components/ui/index';
import { LegalDisclaimer } from '../components/ui/LegalDisclaimer';
import { Shield, Info, Settings2, Moon, Sun, Download, History, Server, ExternalLink, CheckSquare, Bookmark, Briefcase, LogIn, LogOut, User, Settings } from 'lucide-react';

export const Profile = () => {
    const [authEmail, setAuthEmail] = useState('');
    const [authPassword, setAuthPassword] = useState('');
    const [authMode, setAuthMode] = useState<'signin' | 'signup'>('signin');
    const [authError, setAuthError] = useState<string | null>(null);
    const [authBusy, setAuthBusy] = useState(false);

    const { user, loading: authLoading, isConfigured: authConfigured, signIn, signUp, signOut } = useAuth();
    const theme = useStore((s) => s.theme);
    const savedFactIds = useStore((s) => s.savedFactIds) ?? [];
    const toolkitEdits = useStore((s) => s.toolkitEdits) ?? {};
    const recentWWMDIds = useStore((s) => s.recentWWMDIds) ?? [];
    const savedLensResults = useStore((s) => s.savedLensResults) ?? [];
    const savedActionSteps = useStore((s) => s.savedActionSteps) ?? {};
    const apiConfig = useStore((s) => s.apiConfig) ?? {
        provider: 'openai',
        ollamaBaseUrl: 'http://localhost:11434',
        openRouterApiKey: '',
        openAiBaseUrl: '',
        openAiApiKey: '',
        geminiApiKey: '',
    };
    const setApiConfig = useStore((s) => s.setApiConfig);
    const clearUserData = useStore((s) => s.clearUserData);

    const toolkitEditsCount = Object.keys(toolkitEdits).length;
    const resultsWithCheckedActions = savedLensResults.filter((r) => {
        const resultId = r.id ?? (r.query ? `fallback-${String(r.query).slice(0, 40)}` : '');
        return (savedActionSteps[resultId]?.length ?? 0) > 0;
    });

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="mb-8">
                <h1 className="text-3xl font-display font-bold mb-2">My Profile</h1>
                <p className="text-zinc-600 dark:text-zinc-400">
                    Manage your saved insights and app configuration.
                </p>
            </div>

            {/* Stats Section — wait for persisted store so counts are correct */}
            <section className="grid grid-cols-2 gap-4">
                <Link to="/library">
                    <Card className="flex flex-col items-center justify-center p-6 text-center bg-zinc-50 dark:bg-zinc-800/50 hover:border-primary/30 transition-colors cursor-pointer">
                        <Bookmark className="w-6 h-6 text-primary dark:text-secondary mb-2" />
                        <span className="text-3xl font-display font-bold text-primary dark:text-secondary mb-1">
                            {savedFactIds.length}
                        </span>
                        <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-400">Saved Facts</span>
                        {savedFactIds.length > 0 && <span className="text-[9px] text-zinc-500 mt-1">View in Knowledge Base</span>}
                    </Card>
                </Link>
                <Card className="flex flex-col items-center justify-center p-6 text-center bg-zinc-50 dark:bg-zinc-800/50">
                    <Briefcase className="w-6 h-6 text-primary dark:text-secondary mb-2" />
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

                    <Link to="/devops">
                        <Card className="p-4 flex items-center justify-between hover:border-primary/30 transition-colors cursor-pointer">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-zinc-100 dark:bg-zinc-800 rounded-lg text-zinc-500">
                                    <Settings className="w-5 h-5" />
                                </div>
                                <div>
                                    <p className="text-sm font-bold">DevOps</p>
                                    <p className="text-[10px] text-zinc-500 uppercase font-medium">System administration</p>
                                </div>
                            </div>
                            <ExternalLink className="w-4 h-4 text-zinc-400" />
                        </Card>
                    </Link>
                </div>
            </section>

            {/* Account (Supabase) */}
            <section className="space-y-4">
                <div className="flex items-center gap-2 text-zinc-500">
                    <User className="w-5 h-5" />
                    <h2 className="text-sm font-bold uppercase tracking-widest">Account</h2>
                </div>
                {!authConfigured ? (
                    <Card className="p-4">
                        <p className="text-sm text-zinc-500 dark:text-zinc-400">Sign-in is not configured. Add Supabase URL and key to .env to enable.</p>
                    </Card>
                ) : authLoading ? (
                    <Card className="p-4">
                        <p className="text-sm text-zinc-500">Loading…</p>
                    </Card>
                ) : user ? (
                    <Card className="p-4 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-primary/10 rounded-lg">
                                <LogIn className="w-5 h-5 text-primary dark:text-secondary" />
                            </div>
                            <div>
                                <p className="text-sm font-bold">Signed in</p>
                                <p className="text-[10px] text-zinc-500 truncate max-w-[200px]" title={user.email ?? ''}>{user.email ?? 'Unknown'}</p>
                            </div>
                        </div>
                        <Button variant="outline" size="sm" onClick={async () => {
                            clearUserData();
                            await signOut();
                        }}>
                            <LogOut className="w-4 h-4 mr-1 inline" /> Sign out
                        </Button>
                    </Card>
                ) : (
                    <Card className="p-4 space-y-3">
                        <p className="text-[11px] text-zinc-500 uppercase font-medium">{authMode === 'signin' ? 'Sign in' : 'Create account'}</p>
                        {authError && <p className="text-xs text-red-600 dark:text-red-400">{authError}</p>}
                        <input
                            type="email"
                            placeholder="Email"
                            value={authEmail}
                            onChange={(e) => { setAuthEmail(e.target.value); setAuthError(null); }}
                            className="w-full px-3 py-2 text-sm rounded-lg border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900"
                            autoComplete="email"
                        />
                        <input
                            type="password"
                            placeholder="Password"
                            value={authPassword}
                            onChange={(e) => { setAuthPassword(e.target.value); setAuthError(null); }}
                            className="w-full px-3 py-2 text-sm rounded-lg border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900"
                            autoComplete={authMode === 'signin' ? 'current-password' : 'new-password'}
                        />
                        <div className="flex gap-2">
                            <Button
                                size="sm"
                                disabled={authBusy || !authEmail || !authPassword}
                                onClick={async () => {
                                    setAuthBusy(true);
                                    setAuthError(null);
                                    const { error } = authMode === 'signin' ? await signIn(authEmail, authPassword) : await signUp(authEmail, authPassword);
                                    setAuthBusy(false);
                                    if (error) setAuthError(error.message);
                                }}
                            >
                                {authBusy ? '…' : authMode === 'signin' ? 'Sign in' : 'Sign up'}
                            </Button>
                            <button
                                type="button"
                                className="text-xs text-primary dark:text-secondary hover:underline"
                                onClick={() => { setAuthMode((m) => m === 'signin' ? 'signup' : 'signin'); setAuthError(null); }}
                            >
                                {authMode === 'signin' ? 'Create account' : 'Already have an account?'}
                            </button>
                        </div>
                    </Card>
                )}
            </section>

            {/* AI Configuration */}
            <section className="space-y-4">
                <div className="flex items-center gap-2 text-zinc-500">
                    <Server className="w-5 h-5" />
                    <h2 className="text-sm font-bold uppercase tracking-widest">AI Engine</h2>
                </div>

                <div className="grid grid-cols-2 gap-3">
                    <button
                        type="button"
                        onClick={() => setApiConfig({ useOwnAI: false })}
                        className={`p-4 rounded-xl border text-left transition-all ${
                            !apiConfig.useOwnAI
                                ? 'border-primary bg-primary/5 dark:bg-primary/10'
                                : 'border-zinc-200 dark:border-zinc-800 hover:border-zinc-300'
                        }`}
                    >
                        <p className="text-sm font-bold mb-1">MindWave AI</p>
                        <p className="text-[11px] text-zinc-500">Powered by MindWave — no setup needed</p>
                        {!apiConfig.useOwnAI && (
                            <span className="inline-block mt-2 text-[9px] font-bold uppercase tracking-widest text-primary dark:text-secondary">Active</span>
                        )}
                    </button>

                    <button
                        type="button"
                        onClick={() => setApiConfig({ useOwnAI: true })}
                        className={`p-4 rounded-xl border text-left transition-all ${
                            apiConfig.useOwnAI
                                ? 'border-primary bg-primary/5 dark:bg-primary/10'
                                : 'border-zinc-200 dark:border-zinc-800 hover:border-zinc-300'
                        }`}
                    >
                        <p className="text-sm font-bold mb-1">My Own AI</p>
                        <p className="text-[11px] text-zinc-500">Connect your own AI instance</p>
                        {apiConfig.useOwnAI && (
                            <span className="inline-block mt-2 text-[9px] font-bold uppercase tracking-widest text-primary dark:text-secondary">Active</span>
                        )}
                    </button>
                </div>

                {apiConfig.useOwnAI && (
                    <Card className="p-4 space-y-3">
                        <p className="text-[11px] text-zinc-500 uppercase font-medium">Your Ollama endpoint URL</p>
                        <input
                            type="url"
                            placeholder="http://localhost:11434"
                            value={apiConfig.ollamaBaseUrl}
                            onChange={(e) => setApiConfig({ ollamaBaseUrl: e.target.value })}
                            className="w-full px-3 py-2 text-sm rounded-lg border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900"
                        />
                        <p className="text-[10px] text-zinc-400">Enter the base URL of your Ollama instance. Requests will be routed there instead of MindWave AI.</p>
                    </Card>
                )}
            </section>

            {/* Saved Recommended Actions */}
            <section className="space-y-4">
                <div className="flex items-center gap-2 text-zinc-500">
                    <CheckSquare className="w-5 h-5" />
                    <h2 className="text-sm font-bold uppercase tracking-widest">Saved Recommended Actions</h2>
                </div>
                {resultsWithCheckedActions.length > 0 ? (
                    <div className="space-y-3">
                        {resultsWithCheckedActions.map((result) => {
                            const resultId = result.id ?? (result.query ? `fallback-${result.query.slice(0, 40)}` : '');
                            const checkedIds = savedActionSteps[resultId] ?? [];
                            const checkedSteps = result.actionSteps.filter((s) => checkedIds.includes(s.id));
                            return (
                                <Card key={resultId} className="p-4 space-y-2 border-zinc-200 dark:border-zinc-800">
                                    <p className="text-sm font-bold line-clamp-2">{result.query || 'Lens Analysis'}</p>
                                    <ul className="list-disc list-inside text-xs text-zinc-600 dark:text-zinc-400 space-y-1">
                                        {checkedSteps.map((step) => (
                                            <li key={step.id}>{step.text}</li>
                                        ))}
                                    </ul>
                                </Card>
                            );
                        })}
                    </div>
                ) : (
                    <p className="text-sm text-zinc-400 italic">No saved action steps yet. Use Garvey Lens and check the actions you plan to take.</p>
                )}
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
                    <h2 className="text-sm font-bold uppercase tracking-widest">About Whirlwind KB</h2>
                </div>
                <Card className="p-6 space-y-4">
                    <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed">
                        Whirlwind KB is a source-grounded knowledge base inspired by the legacy of Marcus Mosiah Garvey. It provides accessible, citation-backed insights into organization building, economic self-reliance, and Pan-African philosophy.
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

            <LegalDisclaimer />

            <footer className="pt-4 pb-20 text-center space-y-3">
                <img src="/mindwave-logo-02.jpg" alt="MindWave Jamaica" className="h-12 mx-auto opacity-70" />
                <p className="text-[10px] text-zinc-400 uppercase tracking-widest">Project: Marcus Garvey Heritage</p>
                <p className="text-[9px] text-zinc-500">Built with respect for the archives.</p>
            </footer>
        </div>
    );
};
