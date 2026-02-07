import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, FolderOpen, Filter, GitBranch, ScrollText, Settings } from 'lucide-react';
import { Card } from '../components/ui/index';

export const Browse = () => {
    const [query, setQuery] = useState('');

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-xl font-bold text-zinc-900 dark:text-zinc-100">Browse</h1>
                <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
                    Concept viewing and searching — explore and search the knowledge base.
                </p>
            </div>

            <div className="relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-400" />
                <input
                    type="text"
                    placeholder="Search concepts..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="w-full pl-12 pr-4 py-3 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20"
                />
                <button
                    type="button"
                    className="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-500"
                    title="Filters"
                >
                    <Filter className="w-5 h-5" />
                </button>
            </div>

            <div className="grid grid-cols-3 gap-2 md:hidden">
                <Link to="/workflow" className="flex flex-col items-center gap-1 p-3 rounded-xl bg-zinc-100 dark:bg-zinc-800/50 border border-zinc-200 dark:border-zinc-700 text-zinc-700 dark:text-zinc-300">
                    <GitBranch className="w-5 h-5" />
                    <span className="text-[10px] font-medium">Workflow</span>
                </Link>
                <Link to="/log" className="flex flex-col items-center gap-1 p-3 rounded-xl bg-zinc-100 dark:bg-zinc-800/50 border border-zinc-200 dark:border-zinc-700 text-zinc-700 dark:text-zinc-300">
                    <ScrollText className="w-5 h-5" />
                    <span className="text-[10px] font-medium">Log</span>
                </Link>
                <Link to="/devops" className="flex flex-col items-center gap-1 p-3 rounded-xl bg-zinc-100 dark:bg-zinc-800/50 border border-zinc-200 dark:border-zinc-700 text-zinc-700 dark:text-zinc-300">
                    <Settings className="w-5 h-5" />
                    <span className="text-[10px] font-medium">DevOps</span>
                </Link>
            </div>

            <Card className="p-6 border border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-900/50">
                <div className="flex flex-col items-center justify-center py-12 text-center">
                    <FolderOpen className="w-12 h-12 text-zinc-300 dark:text-zinc-600 mb-4" />
                    <p className="text-sm font-medium text-zinc-700 dark:text-zinc-300">Concept browser</p>
                    <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1 max-w-sm">
                        Search and filter concepts. Results will appear here when the backend is connected.
                    </p>
                </div>
            </Card>
        </div>
    );
};
