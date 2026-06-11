import { useState } from 'react';
import { WWMDResponse } from '../../types';
import { Card, Button } from '../ui';
import { HelpCircle, CheckSquare, ScrollText, Sparkles, RefreshCw, Copy, Check, Share2 } from 'lucide-react';
import { SourceItem } from '../facts/SourceItem';
import { useStore } from '../../store/useStore';
import { useAuth } from '../../hooks/useAuth';
import { upsertLensResult } from '../../services/userData';
import { trackSync } from '../../services/syncHelpers';
import { TTSEarlyAccessBanner } from './TTSEarlyAccessBanner';

export const ResponseView = ({ response, onReset }: { response: WWMDResponse, onReset: () => void }) => {
    const resultId = response.id ?? (response.query ? `fallback-${response.query.slice(0, 40)}` : 'unknown');
    const { user } = useAuth();
    const savedActionSteps = useStore((s) => s.savedActionSteps);
    const toggleSavedActionStep = useStore((s) => s.toggleSavedActionStep);
    const checkedStepIds = savedActionSteps[resultId] ?? [];
    const [copied, setCopied] = useState(false);

    const handleToggleStep = (stepId: string) => {
        toggleSavedActionStep(resultId, stepId);
        if (user?.id) {
            const next = useStore.getState().savedActionSteps[resultId] ?? [];
            trackSync(`lens-${resultId}`, "Couldn't sync your progress — saved on this device only", () => upsertLensResult(resultId, response, next));
        }
    };

    const shareText = `"${response.principle}"\n\n— Marcus Garvey ARK\nmarcusgarvey876.com`;

    const handleCopy = () => {
        navigator.clipboard.writeText(shareText).then(() => {
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        });
    };

    const handleWhatsApp = () => {
        const url = `https://wa.me/?text=${encodeURIComponent(shareText)}`;
        window.open(url, '_blank', 'noopener');
    };

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-700">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-primary dark:text-secondary">
                    <Sparkles className="w-5 h-5" />
                    <h2 className="text-sm font-bold uppercase tracking-widest text-zinc-500">What Marcus Would Do</h2>
                </div>
                <div className="flex items-center gap-3">
                    <button type="button" onClick={handleCopy} className="text-xs font-bold text-zinc-400 hover:text-primary flex items-center gap-1 transition-colors" aria-label="Copy result to clipboard">
                        {copied ? <Check className="w-3 h-3 text-green-500" /> : <Copy className="w-3 h-3" />}
                        {copied ? 'COPIED' : 'COPY'}
                    </button>
                    <button type="button" onClick={handleWhatsApp} className="text-xs font-bold text-zinc-400 hover:text-green-500 flex items-center gap-1 transition-colors" aria-label="Share on WhatsApp">
                        <Share2 className="w-3 h-3" />
                        SHARE
                    </button>
                    <button type="button" onClick={onReset} className="text-xs font-bold text-zinc-400 hover:text-primary flex items-center gap-1 transition-colors" aria-label="Start over and clear this analysis">
                        <RefreshCw className="w-3 h-3" />
                        START OVER
                    </button>
                </div>
            </div>

            <section className="space-y-4">
                <Card className="border-l-4 border-l-primary bg-primary/5 dark:bg-primary/10">
                    <p className="text-xl font-display font-bold leading-relaxed">
                        {response.principle}
                    </p>
                </Card>

                <div className="p-6 bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm">
                    <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed italic">
                        {response.historicalAnalogy}
                    </p>
                </div>

                <TTSEarlyAccessBanner />
            </section>

            <section className="space-y-4">
                <div className="flex items-center gap-2 text-zinc-500">
                    <CheckSquare className="w-5 h-5" />
                    <h2 className="text-sm font-bold uppercase tracking-widest">What He'd Have You Do</h2>
                </div>
                <div className="space-y-3">
                    {response.actionSteps.map((step) => (
                        <div key={step.id} className="flex items-start gap-3 p-4 bg-zinc-50 dark:bg-zinc-800/50 rounded-xl border border-zinc-100 dark:border-zinc-800">
                            <input
                                type="checkbox"
                                className="mt-1 w-5 h-5 rounded border-zinc-300 text-primary focus:ring-primary"
                                checked={checkedStepIds.includes(step.id)}
                                onChange={() => handleToggleStep(step.id)}
                            />
                            <span className="text-sm font-medium">{step.text}</span>
                        </div>
                    ))}
                </div>
            </section>

            <section className="space-y-4">
                <div className="flex items-center gap-2 text-zinc-500">
                    <ScrollText className="w-5 h-5" />
                    <h2 className="text-sm font-bold uppercase tracking-widest">Grounded Receipts</h2>
                </div>
                <div className="space-y-3">
                    {response.receipts.map((source) => (
                        <SourceItem key={source.id} source={source} />
                    ))}
                </div>
            </section>

            <section className="p-6 bg-zinc-900 text-white rounded-2xl space-y-4 border border-zinc-800">
                <div className="flex items-center gap-2 text-secondary">
                    <HelpCircle className="w-5 h-5" />
                    <h2 className="text-sm font-bold uppercase tracking-widest">Marcus Asks You</h2>
                </div>
                <div className="space-y-4">
                    {response.mirrorQuestions.map((q, i) => (
                        <p key={i} className="text-lg font-medium border-l-2 border-secondary pl-4 py-1">
                            {q}
                        </p>
                    ))}
                </div>
            </section>

            <div className="pt-4 pb-10">
                <Button onClick={onReset} variant="outline" className="w-full">
                    New Analysis
                </Button>
            </div>
        </div>
    );
};
