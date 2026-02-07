import { GitBranch, Zap } from 'lucide-react';
import { Card } from '../components/ui/index';

export const Workflow = () => {
    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-xl font-bold text-zinc-900 dark:text-zinc-100">Workflow</h1>
                <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
                    Concept extraction with quick wins — run pipelines and see results fast.
                </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
                <Card className="p-5 border border-zinc-200 dark:border-zinc-800 hover:border-primary/30 transition-colors cursor-pointer">
                    <div className="flex items-start gap-3">
                        <div className="p-2 rounded-lg bg-primary/10">
                            <Zap className="w-5 h-5 text-primary" />
                        </div>
                        <div>
                            <p className="font-medium text-zinc-900 dark:text-zinc-100">Quick extraction</p>
                            <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
                                One-shot concept extraction from a single source.
                            </p>
                        </div>
                    </div>
                </Card>
                <Card className="p-5 border border-zinc-200 dark:border-zinc-800 hover:border-primary/30 transition-colors cursor-pointer">
                    <div className="flex items-start gap-3">
                        <div className="p-2 rounded-lg bg-primary/10">
                            <GitBranch className="w-5 h-5 text-primary" />
                        </div>
                        <div>
                            <p className="font-medium text-zinc-900 dark:text-zinc-100">Pipeline</p>
                            <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
                                Multi-step extraction and enrichment workflows.
                            </p>
                        </div>
                    </div>
                </Card>
            </div>

            <Card className="p-6 border border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-900/50">
                <p className="text-sm text-zinc-600 dark:text-zinc-400">
                    Workflow runs and quick wins will appear here when the extraction backend is connected.
                </p>
            </Card>
        </div>
    );
};
