import { NavLink } from 'react-router-dom';
import { Home, Library, MessageSquare, Briefcase, User, ArrowRight } from 'lucide-react';
import { cn } from '../ui/index';

const NAV_ITEMS = [
    { icon: Home, label: 'Home', path: '/home' },
    { icon: Library, label: 'Knowledge Base', path: '/library' },
    { icon: MessageSquare, label: 'WWMD', path: '/wwmd' },
    { icon: Briefcase, label: 'Toolkit', path: '/toolkit' },
    { icon: User, label: 'Profile', path: '/profile' },
];

export const GlobalSidebar = () => {
    return (
        <aside className="w-64 border-r border-border bg-zinc-100/90 dark:bg-card/50 backdrop-blur-xl hidden md:flex flex-col h-screen sticky top-0">
            {/* Status block at top */}
            <div className="p-4 border-b border-border shrink-0">
                <div className="bg-gradient-to-br from-black to-zinc-800 dark:from-red-950 dark:to-black p-4 rounded-xl text-white shadow-lg relative overflow-hidden group cursor-pointer">
                    <div className="absolute top-0 right-0 w-20 h-20 bg-green-500/20 rounded-full blur-2xl -mr-10 -mt-10 group-hover:bg-green-500/30 transition-all"></div>
                    <p className="text-xs font-mono text-green-400 mb-1">STATUS: ONLINE</p>
                    <p className="text-sm font-bold">Whirlwind KB</p>
                    <p className="text-[10px] opacity-70 mt-2">v2.0.6</p>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
                {NAV_ITEMS.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) => cn(
                            'flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all group',
                            isActive
                                ? 'bg-primary/10 text-primary border border-primary/20 shadow-sm'
                                : 'text-zinc-900 dark:text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                        )}
                    >
                        <item.icon className="w-5 h-5" />
                        <span>{item.label}</span>
                        <ArrowRight className="w-3 h-3 ml-auto opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
                    </NavLink>
                ))}
            </nav>
        </aside>
    );
};
