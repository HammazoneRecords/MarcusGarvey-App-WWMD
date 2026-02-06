import { WWMDResponse } from '../../types';
import { Card } from '../ui/index';
import { Target, Calendar } from 'lucide-react';

interface LensResultCardProps {
    result: WWMDResponse;
    onClick?: () => void;
}

export const LensResultCard = ({ result, onClick }: LensResultCardProps) => {
    return (
        <Card className="hover:border-primary/50 transition-all cursor-pointer group" onClick={onClick}>
            <div className="p-6 space-y-4">
                <div className="flex items-start justify-between">
                    <div className="space-y-1">
                        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-primary">
                            <Target className="w-4 h-4" />
                            <span>Garvey Lens Analysis</span>
                        </div>
                        <h3 className="font-bold text-lg line-clamp-2">
                            {result.query || "Situation Analysis"}
                        </h3>
                    </div>
                </div>

                <div className="pl-4 border-l-2 border-zinc-200 dark:border-zinc-800 space-y-2">
                    <p className="text-sm font-medium text-zinc-900 dark:text-zinc-100">
                        {result.principle}
                    </p>
                    <p className="text-xs text-zinc-500 line-clamp-2">
                        {result.historicalAnalogy}
                    </p>
                </div>

                <div className="flex items-center gap-4 text-xs text-zinc-400 pt-2 border-t border-zinc-100 dark:border-zinc-800/50">
                    <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        Saved Session
                    </span>
                    <span>•</span>
                    <span>{result.actionSteps.length} Action Steps</span>
                </div>
            </div>
        </Card>
    );
};
