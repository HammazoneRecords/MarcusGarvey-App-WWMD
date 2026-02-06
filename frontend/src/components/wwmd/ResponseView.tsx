import { WWMDResponse } from '../../types';
import { Card, Button } from '../ui';
import { HelpCircle, CheckSquare, ScrollText, Sparkles, RefreshCw } from 'lucide-react';
import { SourceItem } from '../facts/SourceItem';

export const ResponseView = ({ response, onReset }: { response: WWMDResponse, onReset: () => void }) => {
    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-700">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-primary dark:text-secondary">
                    <Sparkles className="w-5 h-5" />
                    <h2 className="text-sm font-bold uppercase tracking-widest text-zinc-500">Lens Analysis</h2>
                </div>
                <button onClick={onReset} className="text-xs font-bold text-zinc-400 hover:text-primary flex items-center gap-1 transition-colors">
                    <RefreshCw className="w-3 h-3" />
                    START OVER
                </button>
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
            </section>

            <section className="space-y-4">
                <div className="flex items-center gap-2 text-zinc-500">
                    <CheckSquare className="w-5 h-5" />
                    <h2 className="text-sm font-bold uppercase tracking-widest">Recommended Actions</h2>
                </div>
                <div className="space-y-3">
                    {response.actionSteps.map((step) => (
                        <div key={step.id} className="flex items-start gap-3 p-4 bg-zinc-50 dark:bg-zinc-800/50 rounded-xl border border-zinc-100 dark:border-zinc-800">
                            <input type="checkbox" className="mt-1 w-5 h-5 rounded border-zinc-300 text-primary focus:ring-primary" />
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
                    <h2 className="text-sm font-bold uppercase tracking-widest">Garvey Mirror</h2>
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
