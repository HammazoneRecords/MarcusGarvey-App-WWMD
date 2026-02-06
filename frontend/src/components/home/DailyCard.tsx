import { Quote, HelpCircle } from 'lucide-react';
import { DailyItem } from '../../types';
import { Card } from '../ui/index';

export const DailyCard = ({ item }: { item: DailyItem }) => {
    return (
        <Card className="border-l-4 border-l-secondary">
            <div className="flex items-start gap-4">
                <div className="p-2 bg-secondary/10 rounded-lg">
                    <Quote className="w-6 h-6 text-secondary" />
                </div>
                <div className="flex-1">
                    <p className="text-lg font-medium leading-relaxed italic mb-4">
                        "{item.quote}"
                    </p>
                    <div className="space-y-3">
                        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-zinc-500">
                            <span>Context</span>
                        </div>
                        <p className="text-sm text-zinc-600 dark:text-zinc-400">
                            {item.context}
                        </p>

                        <div className="p-4 bg-zinc-50 dark:bg-zinc-800/50 rounded-xl border border-dashed border-zinc-200 dark:border-zinc-700">
                            <div className="flex items-center gap-2 mb-2 text-primary dark:text-secondary">
                                <HelpCircle className="w-4 h-4" />
                                <span className="text-xs font-bold uppercase tracking-wider">Reflection</span>
                            </div>
                            <p className="text-sm font-medium">
                                {item.reflectionQuestion}
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </Card>
    );
};
