import { useForm, useWatch } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { WWMDRequest } from '../../types';
import { Button } from '../ui/index';
import { MessageSquare, Sparkles } from 'lucide-react';

const MAX_LEN = 4000;

const schema = z.object({
    situation: z.string()
        .min(10, 'Please provide more context (at least 10 characters)')
        .max(MAX_LEN, `Maximum ${MAX_LEN} characters`),
    mode: z.enum(['Personal', 'Strict', 'Gentle']).default('Personal'),
});

export const WWMDForm = ({ onSubmit, loading }: { onSubmit: (data: WWMDRequest) => void, loading: boolean }) => {
    const { register, handleSubmit, control, formState: { errors } } = useForm<WWMDRequest>({
        resolver: zodResolver(schema),
        defaultValues: { mode: 'Personal' }
    });

    const situation = useWatch({ control, name: 'situation', defaultValue: '' });
    const charCount = situation?.length ?? 0;

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
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

            <input type="hidden" {...register('mode')} value="Personal" />

            <Button type="submit" className="w-full h-14" disabled={loading}>
                {loading ? (
                    <span className="flex items-center gap-2">
                        <Sparkles className="w-5 h-5 animate-pulse" />
                        Grounding Response...
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
