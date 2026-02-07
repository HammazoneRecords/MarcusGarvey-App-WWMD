import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { WWMDRequest } from '../../types';
import { Button, Card } from '../ui/index';
import { MessageSquare, Sparkles } from 'lucide-react';

const schema = z.object({
    situation: z.string().min(10, 'Please provide more context (at least 10 characters)'),
    tone: z.enum(['Practical', 'Strict', 'Gentle']),
});

export const WWMDForm = ({ onSubmit, loading }: { onSubmit: (data: WWMDRequest) => void, loading: boolean }) => {
    const { register, handleSubmit, formState: { errors } } = useForm<WWMDRequest>({
        resolver: zodResolver(schema),
        defaultValues: {
            tone: 'Practical',
        }
    });

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="space-y-2">
                <label className="text-sm font-bold uppercase tracking-widest text-zinc-500">The Situation</label>
                <textarea
                    {...register('situation')}
                    placeholder="e.g., I am considering starting a community cooperative but I am worried about funding..."
                    className={`w-full h-32 p-4 rounded-2xl bg-white dark:bg-zinc-900 border ${errors.situation ? 'border-accent' : 'border-zinc-200 dark:border-zinc-800'} focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all resize-none text-base`}
                />
                {errors.situation && <p className="text-xs text-accent font-medium">{errors.situation.message}</p>}
            </div>

            <div className="space-y-4">
                <label className="text-sm font-bold uppercase tracking-widest text-zinc-500">Tone</label>
                <select
                    {...register('tone')}
                    className="w-full p-4 rounded-xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 outline-none focus:ring-2 focus:ring-primary/20"
                >
                    <option value="Practical">Practical (Balanced)</option>
                    <option value="Strict">Strict (Direct Philosophy)</option>
                    <option value="Gentle">Gentle (Encouraging)</option>
                </select>
            </div>

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
