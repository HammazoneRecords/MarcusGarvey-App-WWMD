import { NavLink } from 'react-router-dom';
import { Home, Library, MessageSquare, Bot, User } from 'lucide-react';
import { cn } from '../ui/index';

const NAV_ITEMS = [
    { icon: Home, label: 'Home', path: '/home' },
    { icon: Bot, label: 'Chat', path: '/chat' },
    { icon: MessageSquare, label: 'Lens', path: '/wwmd' },
    { icon: Library, label: 'Library', path: '/library' },
    { icon: User, label: 'Profile', path: '/profile' },
];

export const BottomNav = () => {
    return (
        <nav className="fixed bottom-0 left-0 right-0 glass-nav z-50">
            <div className="flex justify-around items-center h-16 max-w-lg mx-auto">
                {NAV_ITEMS.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) => cn(
                            'flex flex-col items-center justify-center flex-1 h-full transition-colors',
                            isActive ? 'text-primary dark:text-secondary' : 'text-zinc-400 dark:text-zinc-600'
                        )}
                    >
                        <item.icon className="w-6 h-6" />
                        <span className="text-[10px] mt-1 font-medium truncate w-full text-center px-0.5">{item.label}</span>
                    </NavLink>
                ))}
            </div>
        </nav>
    );
};
