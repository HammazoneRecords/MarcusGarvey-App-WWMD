import { useState } from 'react';
import { Bot, Check } from 'lucide-react';
import { Card, Button } from '../components/ui';
import { submitTTSLead } from '../services/userData';

export const Chat = () => {
    const [email, setEmail] = useState('');
    const [status, setStatus] = useState<'idle' | 'busy' | 'done' | 'error'>('idle');
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!email.trim()) return;
        setStatus('busy');
        setError(null);
        const { error } = await submitTTSLead(email.trim(), 'chatbot-coming-soon');
        if (error) {
            setError(error.message);
            setStatus('error');
            return;
        }
        setStatus('done');
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-[calc(100vh-12rem)] text-center px-6">
            <div className="text-6xl mb-4">✊🏾</div>
            <h1 className="text-2xl font-display font-bold mb-2">Ask Marcus — Coming Soon</h1>
            <p className="text-sm text-zinc-500 dark:text-zinc-400 max-w-sm leading-relaxed mb-6">
                A direct conversation with Marcus is on the way. In the meantime, use the{' '}
                <span className="font-semibold text-primary dark:text-secondary">Garvey Lens</span> to get his take on your situation.
            </p>

            <Card className="w-full max-w-sm border border-secondary/30 bg-secondary/5 dark:bg-secondary/10 space-y-3">
                <div className="flex items-center justify-center gap-2 text-secondary">
                    <Bot className="w-5 h-5" />
                    <h3 className="text-sm font-bold uppercase tracking-widest">Get Notified at Launch</h3>
                </div>
                {status === 'done' ? (
                    <p className="text-sm font-medium flex items-center justify-center gap-2 text-green-600 dark:text-green-400">
                        <Check className="w-4 h-4" /> You're on the list — we'll email you when chat is ready.
                    </p>
                ) : (
                    <>
                        <form onSubmit={handleSubmit} className="flex flex-col gap-2">
                            <input
                                type="email"
                                required
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="you@email.com"
                                className="px-4 py-2.5 rounded-xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 focus:ring-2 focus:ring-secondary/30 focus:border-secondary outline-none text-sm"
                            />
                            <Button type="submit" variant="secondary" disabled={status === 'busy'}>
                                {status === 'busy' ? 'Signing up…' : 'Notify Me'}
                            </Button>
                        </form>
                        {error && <p className="text-xs text-accent font-medium">{error}</p>}
                    </>
                )}
            </Card>
        </div>
    );
};
