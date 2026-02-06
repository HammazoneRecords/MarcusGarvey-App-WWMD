import { Fact } from '../../types';
import { Card, Chip } from '../ui/index';
import { ArrowRight, ShieldCheck, AlertCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

export const FactCard = ({ fact }: { fact: Fact }) => {
    return (
        <Link to={`/facts/${fact.id}`}>
            <Card className="hover:shadow-lg transition-all group border-b-4 border-b-transparent hover:border-b-secondary">
                <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                        {fact.confidence === 'high' ? (
                            <ShieldCheck className="w-4 h-4 text-primary" />
                        ) : (
                            <AlertCircle className="w-4 h-4 text-accent" />
                        )}
                        <span className={fact.confidence === 'high' ? 'text-[10px] font-bold text-primary uppercase' : 'text-[10px] font-bold text-accent uppercase'}>
                            {fact.confidence} Confidence
                        </span>
                    </div>
                    <span className="text-[10px] font-medium text-zinc-400">
                        {Math.ceil(fact.readingTimeSec / 60)}m read
                    </span>
                </div>

                <h3 className="text-base font-bold mb-2 group-hover:text-primary dark:group-hover:text-secondary transition-colors leading-tight">
                    {fact.claim}
                </h3>

                <p className="text-sm text-zinc-600 dark:text-zinc-400 line-clamp-2 mb-4">
                    {fact.context}
                </p>

                <div className="flex flex-wrap gap-2">
                    {fact.categories.slice(0, 2).map((cat) => (
                        <span key={cat} className="px-2 py-0.5 bg-zinc-100 dark:bg-zinc-800 text-[9px] font-bold text-zinc-500 rounded uppercase">
                            {cat}
                        </span>
                    ))}
                    {fact.categories.length > 2 && (
                        <span className="text-[9px] font-bold text-zinc-400">+{fact.categories.length - 2} more</span>
                    )}
                </div>
            </Card>
        </Link>
    );
};
