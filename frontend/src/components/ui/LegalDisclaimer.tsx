import { ShieldAlert, Info } from 'lucide-react';
import { Card } from './index';

export const LegalDisclaimer = () => {
    return (
        <Card className="bg-zinc-50 dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800 p-6 space-y-4">
            <div className="flex items-center gap-2 text-zinc-500">
                <ShieldAlert className="w-5 h-5" />
                <h2 className="text-xs font-bold uppercase tracking-[0.15em]">Architectural Boundary</h2>
            </div>
            <div className="space-y-3 text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed">
                <p>
                    <strong>Garvey Compass</strong> is a source-grounded research instrument. The "Garvey Lens" assistant provides analysis derived from documented historical principles and archival records.
                </p>
                <p>
                    This interface is not a roleplay environment, nor is it intended for identity commentary or political messaging. It is designed to facilitate the study of organizational structure and self-reliance philosophy through primary source evidence.
                </p>
            </div>
            <div className="pt-4 border-t border-zinc-200 dark:border-zinc-800 flex items-start gap-3">
                <Info className="w-4 h-4 text-zinc-400 mt-0.5" />
                <p className="text-[11px] text-zinc-500 uppercase font-medium tracking-wider">
                    Data integrity is prioritized via direct citations (Receipts).
                </p>
            </div>
        </Card>
    );
};
