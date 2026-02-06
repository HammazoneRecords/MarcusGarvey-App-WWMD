import { Moon, Sun } from 'lucide-react';
import { useStore } from '../../store/useStore';
import { useEffect } from 'react';

export const ThemeToggle = () => {
    const { theme, toggleTheme } = useStore();

    useEffect(() => {
        const root = window.document.documentElement;
        if (theme === 'dark') {
            root.classList.add('dark');
        } else {
            root.classList.remove('dark');
        }
    }, [theme]);

    return (
        <button
            onClick={toggleTheme}
            className="p-2 rounded-full hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors tap-target"
            aria-label="Toggle theme"
        >
            {theme === 'light' ? (
                <Moon className="w-5 h-5 text-primary" />
            ) : (
                <Sun className="w-5 h-5 text-secondary" />
            )}
        </button>
    );
};
