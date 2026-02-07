import { Card } from '../components/ui/index';
import { Shield } from 'lucide-react';

export const Privacy = () => {
    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <h1 className="text-2xl font-display font-bold">Privacy Policy</h1>
            <Card className="p-6 space-y-4">
                <div className="flex items-center gap-2 text-primary">
                    <Shield className="w-5 h-5" />
                    <span className="text-sm font-bold uppercase tracking-widest">Summary</span>
                </div>
                <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed">
                    Whirlwind KB stores preferences and saved items (facts, toolkit edits, lens results) on your device only (localStorage). 
                    When you use the Garvey Lens, your input is sent to our backend and/or the AI provider you configure to generate responses. 
                    We do not sell your data or use it for advertising.
                </p>
                <p className="text-xs text-zinc-500">
                    For the full privacy policy, see the project documentation (docs/PRIVACY_POLICY.md) or contact the operator (Mindwave Jamaica).
                </p>
            </Card>
        </div>
    );
};
