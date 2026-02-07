import { Settings, Server, Database, Key } from 'lucide-react';
import { Card } from '../components/ui/index';

export const DevOps = () => {
    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-xl font-bold text-zinc-900 dark:text-zinc-100">DevOps</h1>
                <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
                    System administration — configuration, deployments, and access.
                </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
                <Card className="p-5 border border-zinc-200 dark:border-zinc-800 hover:border-primary/30 transition-colors cursor-pointer">
                    <div className="flex items-start gap-3">
                        <div className="p-2 rounded-lg bg-primary/10">
                            <Settings className="w-5 h-5 text-primary" />
                        </div>
                        <div>
                            <p className="font-medium text-zinc-900 dark:text-zinc-100">Configuration</p>
                            <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
                                Environment and feature flags.
                            </p>
                        </div>
                    </div>
                </Card>
                <Card className="p-5 border border-zinc-200 dark:border-zinc-800 hover:border-primary/30 transition-colors cursor-pointer">
                    <div className="flex items-start gap-3">
                        <div className="p-2 rounded-lg bg-primary/10">
                            <Server className="w-5 h-5 text-primary" />
                        </div>
                        <div>
                            <p className="font-medium text-zinc-900 dark:text-zinc-100">Deployments</p>
                            <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
                                Build history and rollbacks.
                            </p>
                        </div>
                    </div>
                </Card>
                <Card className="p-5 border border-zinc-200 dark:border-zinc-800 hover:border-primary/30 transition-colors cursor-pointer">
                    <div className="flex items-start gap-3">
                        <div className="p-2 rounded-lg bg-primary/10">
                            <Database className="w-5 h-5 text-primary" />
                        </div>
                        <div>
                            <p className="font-medium text-zinc-900 dark:text-zinc-100">Data</p>
                            <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
                                Migrations and backups.
                            </p>
                        </div>
                    </div>
                </Card>
                <Card className="p-5 border border-zinc-200 dark:border-zinc-800 hover:border-primary/30 transition-colors cursor-pointer">
                    <div className="flex items-start gap-3">
                        <div className="p-2 rounded-lg bg-primary/10">
                            <Key className="w-5 h-5 text-primary" />
                        </div>
                        <div>
                            <p className="font-medium text-zinc-900 dark:text-zinc-100">Access</p>
                            <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
                                API keys and permissions.
                            </p>
                        </div>
                    </div>
                </Card>
            </div>

            <Card className="p-6 border border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-900/50">
                <p className="text-sm text-zinc-600 dark:text-zinc-400">
                    Admin actions and status will appear here when the platform is connected (e.g. Digital Ocean App Platform).
                </p>
            </Card>
        </div>
    );
};
