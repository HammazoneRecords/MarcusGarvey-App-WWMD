import { NavLink, Link } from 'react-router-dom';
import { Home, Library, MessageSquare, Briefcase, User, ArrowRight, Bot } from 'lucide-react';
import { cn } from '../ui/index';

const NAV_ITEMS = [
    { icon: Home, label: 'Home', path: '/home' },
    { icon: Bot, label: 'Ask Marcus', path: '/chat' },
    { icon: MessageSquare, label: 'What Would Marcus Do?', path: '/wwmd' },
    { icon: Library, label: 'Knowledge Base', path: '/library' },
    { icon: Briefcase, label: 'Toolkit', path: '/toolkit' },
    { icon: User, label: 'Profile', path: '/profile' },
];

export const GlobalSidebar = () => {
    return (
        <aside className="w-64 border-r border-border bg-zinc-100/90 dark:bg-card/50 backdrop-blur-xl hidden md:flex flex-col h-screen sticky top-0">
            {/* Status block at top */}
            <div className="p-4 border-b border-border shrink-0">
                <div onClick={() => window.location.reload()} className="bg-gradient-to-br from-black to-zinc-800 dark:from-red-950 dark:to-black p-4 rounded-xl text-white shadow-lg relative overflow-hidden group cursor-pointer">
                    <div className="absolute top-0 right-0 w-20 h-20 bg-green-500/20 rounded-full blur-2xl -mr-10 -mt-10 group-hover:bg-green-500/30 transition-all"></div>
                    <p className="text-xs font-mono text-green-400 mb-1">STATUS: ONLINE</p>
                    <p className="text-[10px] font-bold uppercase tracking-widest opacity-90 mt-2">MARCUSGARVEY876.COM</p>
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

            {/* Legal footer */}
            <div className="p-4 border-t border-border shrink-0 flex gap-4">
                <Link to="/privacy" className="text-[10px] text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300 transition-colors">Privacy</Link>
                <Link to="/terms" className="text-[10px] text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300 transition-colors">Terms</Link>
                <span className="text-[10px] text-zinc-400 ml-auto">v2.0.6</span>
            </div>
        </aside>
    );
};
