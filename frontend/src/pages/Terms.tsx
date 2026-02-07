import { Card } from '../components/ui/index';
import { FileText } from 'lucide-react';

export const Terms = () => {
    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <h1 className="text-2xl font-display font-bold">Terms of Use</h1>
            <Card className="p-6 space-y-4">
                <div className="flex items-center gap-2 text-primary">
                    <FileText className="w-5 h-5" />
                    <span className="text-sm font-bold uppercase tracking-widest">Summary</span>
                </div>
                <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed">
                    Whirlwind KB is for educational and organizational study. The Garvey Lens is source-grounded counsel, not impersonation or professional advice. 
                    Use the app responsibly; do not misuse or overload the service. Content is provided for study—verify important facts with primary sources.
                </p>
                <p className="text-xs text-zinc-500">
                    For the full terms of use, see the project documentation (docs/TERMS_OF_USE.md) or contact the operator (Mindwave Jamaica).
                </p>
            </Card>
        </div>
    );
};
