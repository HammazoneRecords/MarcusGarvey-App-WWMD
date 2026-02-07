import { useState } from 'react';
import { ScrollText, RefreshCw } from 'lucide-react';
import { Card } from '../components/ui/index';

const PLACEHOLDER_LOGS = [
    { id: '1', ts: new Date().toISOString(), level: 'info', msg: 'App started' },
    { id: '2', ts: new Date(Date.now() - 60000).toISOString(), level: 'info', msg: 'API health check OK' },
    { id: '3', ts: new Date(Date.now() - 120000).toISOString(), level: 'warn', msg: 'Cache miss for key sessions/latest' },
];

export const Log = () => {
    const [levelFilter, setLevelFilter] = useState<string>('all');

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-xl font-bold text-zinc-900 dark:text-zinc-100">Log</h1>
                <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
                    System logging and monitoring — inspect events and health.
                </p>
            </div>

            <div className="flex flex-wrap items-center gap-2">
                {['all', 'info', 'warn', 'error'].map((level) => (
                    <button
                        key={level}
                        onClick={() => setLevelFilter(level)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-colors ${
                            levelFilter === level
                                ? 'bg-primary text-primary-foreground'
                                : 'bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 hover:bg-zinc-200 dark:hover:bg-zinc-700'
                        }`}
                    >
                        {level}
                    </button>
                ))}
                <button
                    type="button"
                    className="ml-auto p-2 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-500"
                    title="Refresh"
                >
                    <RefreshCw className="w-4 h-4" />
                </button>
            </div>

            <Card className="border border-zinc-200 dark:border-zinc-800 overflow-hidden">
                <div className="p-3 border-b border-zinc-200 dark:border-zinc-800 flex items-center gap-2 text-xs text-zinc-500">
                    <ScrollText className="w-4 h-4" />
                    <span>System log stream (concept — connect to your log backend)</span>
                </div>
                <div className="p-4 font-mono text-xs space-y-2 max-h-[50vh] overflow-y-auto bg-zinc-950 text-zinc-300">
                    {PLACEHOLDER_LOGS.map((log) => (
                        <div key={log.id} className="flex gap-3">
                            <span className="text-zinc-500 shrink-0">{new Date(log.ts).toLocaleTimeString()}</span>
                            <span className={log.level === 'warn' ? 'text-amber-400' : log.level === 'error' ? 'text-red-400' : ''}>
                                [{log.level}]
                            </span>
                            <span>{log.msg}</span>
                        </div>
                    ))}
                </div>
            </Card>
        </div>
    );
};
