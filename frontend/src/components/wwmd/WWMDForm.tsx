import { useForm, useWatch } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useEffect, useRef, useState } from 'react';
import { WWMDRequest } from '../../types';
import { Button } from '../ui/index';
import { MessageSquare, Sparkles } from 'lucide-react';

const MAX_LEN = 4000;

const schema = z.object({
    situation: z.string()
        .min(10, 'Please provide more context (at least 10 characters)')
        .max(MAX_LEN, `Maximum ${MAX_LEN} characters`),
    mode: z.enum(['Personal', 'Community']).default('Personal'),
});

type FormValues = z.infer<typeof schema>;

export const WWMDForm = ({ onSubmit, loading }: { onSubmit: (data: WWMDRequest) => void, loading: boolean }) => {
    const { register, handleSubmit, control, setValue, watch, formState: { errors } } = useForm<FormValues>({
        resolver: zodResolver(schema),
        defaultValues: { mode: 'Personal' }
    });

    const situation = useWatch({ control, name: 'situation', defaultValue: '' });
    const mode = watch('mode');
    const charCount = situation?.length ?? 0;

    // Elapsed timer
    const [elapsed, setElapsed] = useState(0);
    const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

    useEffect(() => {
        if (loading) {
            setElapsed(0);
            timerRef.current = setInterval(() => setElapsed(s => s + 1), 1000);
        } else {
            if (timerRef.current) clearInterval(timerRef.current);
            setElapsed(0);
        }
        return () => { if (timerRef.current) clearInterval(timerRef.current); };
    }, [loading]);

    const loadingStage = elapsed < 5 ? 'Searching archives...' : elapsed < 15 ? 'Building context...' : 'Generating response...';

    return (
        <form onSubmit={handleSubmit((data) => onSubmit({ ...data, tone: 'Practical' }))} className="space-y-6">
            <div className="space-y-2">
                <div className="flex items-center justify-between">
                    <label className="text-sm font-bold uppercase tracking-widest text-zinc-500">The Situation</label>
                    <span className={`text-[10px] font-mono ${charCount > MAX_LEN * 0.9 ? 'text-red-500' : 'text-zinc-400'}`}>
                        {charCount}/{MAX_LEN}
                    </span>
                </div>
                <textarea
                    {...register('situation')}
                    placeholder="e.g., I am considering starting a community cooperative but I am worried about funding..."
                    className={`w-full h-32 p-4 rounded-2xl bg-white dark:bg-zinc-900 border ${errors.situation ? 'border-accent' : 'border-zinc-200 dark:border-zinc-800'} focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all resize-none text-base`}
                    maxLength={MAX_LEN}
                />
                {errors.situation && <p className="text-xs text-accent font-medium">{errors.situation.message}</p>}
            </div>

            {/* Mode selector */}
            <div className="space-y-2">
                <label className="text-sm font-bold uppercase tracking-widest text-zinc-500">Lens Mode</label>
                <div className="grid grid-cols-2 gap-3">
                    {(['Personal', 'Community'] as const).map((m) => (
                        <button
                            key={m}
                            type="button"
                            onClick={() => setValue('mode', m)}
                            className={`p-3 rounded-xl border text-left transition-all ${
                                mode === m
                                    ? 'border-primary bg-primary/5 dark:bg-primary/10'
                                    : 'border-zinc-200 dark:border-zinc-800 hover:border-zinc-300'
                            }`}
                        >
                            <p className="text-sm font-bold">{m}</p>
                            <p className="text-[10px] text-zinc-500 mt-0.5">
                                {m === 'Personal' ? 'Individual decisions & growth' : 'Organisation & collective action'}
                            </p>
                            {mode === m && (
                                <span className="inline-block mt-1 text-[9px] font-bold uppercase tracking-widest text-primary dark:text-secondary">Active</span>
                            )}
                        </button>
                    ))}
                </div>
            </div>

            <Button type="submit" className="w-full h-14" disabled={loading}>
                {loading ? (
                    <span className="flex items-center gap-2">
                        <Sparkles className="w-5 h-5 animate-pulse" />
                        <span>{loadingStage}</span>
                        <span className="font-mono text-xs opacity-70">{elapsed}s</span>
                    </span>
                ) : (
                    <span className="flex items-center gap-2">
                        <MessageSquare className="w-5 h-5" />
                        Analyze with Garvey Lens
                    </span>
                )}
            </Button>
        </form>
    );
};
