import { ToolkitTemplate } from '../../types';
import { Card } from '../ui/index';
import { FileText, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const TemplateCard = ({ template }: { template: ToolkitTemplate }) => {
    return (
        <Link to={`/toolkit/${template.id}`}>
            <Card className="hover:border-primary transition-all group">
                <div className="flex items-start gap-4">
                    <div className="p-3 bg-zinc-100 dark:bg-zinc-800 rounded-xl group-hover:bg-primary/10 transition-colors">
                        <FileText className="w-6 h-6 text-zinc-500 group-hover:text-primary transition-colors" />
                    </div>
                    <div className="flex-1">
                        <h3 className="text-lg font-bold mb-1">{template.title}</h3>
                        <p className="text-sm text-zinc-500 dark:text-zinc-400 mb-3">
                            {template.description}
                        </p>
                        <div className="flex flex-wrap gap-2">
                            {template.tags.map(tag => (
                                <span key={tag} className="text-[10px] font-bold text-zinc-400 uppercase tracking-wider">
                                    #{tag}
                                </span>
                            ))}
                        </div>
                    </div>
                    <ArrowRight className="w-5 h-5 text-zinc-300 group-hover:text-primary mt-1" />
                </div>
            </Card>
        </Link>
    );
};
