import { useState, useEffect } from 'react';
import { getToolkitTemplates } from '../services/api';
import { ToolkitTemplate } from '../types';
import { TemplateCard } from '../components/toolkit/TemplateCard';
import { Skeleton, Card } from '../components/ui/index';
import { Briefcase, Info } from 'lucide-react';

export const Toolkit = () => {
    const [templates, setTemplates] = useState<ToolkitTemplate[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchTemplates = async () => {
            try {
                const data = await getToolkitTemplates();
                setTemplates(data);
            } catch (error) {
                console.error("Failed to fetch templates", error);
            } finally {
                setLoading(false);
            }
        };
        fetchTemplates();
    }, []);

    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="mb-8">
                <h1 className="text-3xl font-display font-bold mb-2">Toolkit</h1>
                <p className="text-zinc-600 dark:text-zinc-400">
                    Practical templates and blueprints for building strong, self-reliant organizations.
                </p>
            </div>

            <Card className="bg-primary/5 dark:bg-primary/10 border-primary/20 flex gap-4 p-4">
                <Info className="w-5 h-5 text-primary dark:text-secondary flex-shrink-0" />
                <p className="text-xs text-zinc-600 dark:text-zinc-400 leading-relaxed">
                    These templates are based on historical UNIA organizational structures and general principles of effective community leadership.
                </p>
            </Card>

            <div className="space-y-4">
                {loading ? (
                    Array.from({ length: 3 }).map((_, i) => (
                        <Skeleton key={i} className="h-32 w-full" />
                    ))
                ) : (
                    templates.map((template) => (
                        <TemplateCard key={template.id} template={template} />
                    ))
                )}
            </div>

            <footer className="pt-10 pb-6 text-center">
                <p className="text-[10px] text-zinc-400 uppercase tracking-widest italic">
                    "The first duty of every man is to be true to himself."
                </p>
            </footer>
        </div>
    );
};
