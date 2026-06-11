import { useState } from 'react';
import { Volume2, Check } from 'lucide-react';
import { Card, Button } from '../ui';
import { submitTTSLead } from '../../services/userData';

export const TTSEarlyAccessBanner = () => {
    const [email, setEmail] = useState('');
    const [status, setStatus] = useState<'idle' | 'busy' | 'done' | 'error'>('idle');
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!email.trim()) return;
        setStatus('busy');
        setError(null);
        const { error } = await submitTTSLead(email.trim(), 'wwmd-response');
        if (error) {
            setError(error.message);
            setStatus('error');
            return;
        }
        setStatus('done');
    };

    return (
        <Card className="border border-secondary/30 bg-secondary/5 dark:bg-secondary/10 space-y-3">
            <div className="flex items-center gap-2 text-secondary">
                <Volume2 className="w-5 h-5" />
                <h3 className="text-sm font-bold uppercase tracking-widest">Coming Soon: Hear Marcus Speak</h3>
            </div>
            {status === 'done' ? (
                <p className="text-sm font-medium flex items-center gap-2 text-green-600 dark:text-green-400">
                    <Check className="w-4 h-4" /> You're on the list — we'll email you when voice is ready.
                </p>
            ) : (
                <>
                    <p className="text-sm text-zinc-600 dark:text-zinc-400">
                        Soon you'll be able to hear this answer read aloud in Marcus's voice. Sign up for early access.
                    </p>
                    <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-2">
                        <input
                            type="email"
                            required
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="you@email.com"
                            className="flex-1 px-4 py-2.5 rounded-xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 focus:ring-2 focus:ring-secondary/30 focus:border-secondary outline-none text-sm"
                        />
                        <Button type="submit" variant="secondary" disabled={status === 'busy'}>
                            {status === 'busy' ? 'Signing up…' : 'Get Early Access'}
                        </Button>
                    </form>
                    {error && <p className="text-xs text-accent font-medium">{error}</p>}
                </>
            )}
        </Card>
    );
};
