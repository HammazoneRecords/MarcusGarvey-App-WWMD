import React from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

// Button Component
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
    size?: 'sm' | 'md' | 'lg';
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = 'primary', size = 'md', ...props }, ref) => {
        const variants = {
            primary: 'bg-primary text-white hover:bg-primary-light active:bg-primary-dark shadow-md',
            secondary: 'bg-secondary text-black hover:bg-secondary-light active:bg-secondary-dark shadow-md',
            outline: 'bg-transparent border-2 border-primary text-primary hover:bg-primary/10',
            ghost: 'bg-transparent text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800',
        };
        const sizes = {
            sm: 'px-3 py-1.5 text-sm',
            md: 'px-5 py-2.5 text-base',
            lg: 'px-8 py-3.5 text-lg font-bold',
        };

        return (
            <button
                ref={ref}
                className={cn(
                    'inline-flex items-center justify-center rounded-xl font-medium transition-all duration-200 active:scale-95 disabled:opacity-50 disabled:pointer-events-none tap-target',
                    variants[variant],
                    sizes[size],
                    className
                )}
                {...props}
            />
        );
    }
);

// Card Component
export const Card = ({ children, className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
    <div className={cn('premium-card p-5', className)} {...props}>
        {children}
    </div>
);

// Chip Component
export const Chip = ({ label, active, onClick }: { label: string; active?: boolean; onClick?: () => void }) => (
    <button
        onClick={onClick}
        className={cn(
            'px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap shrink-0 transition-colors tap-target',
            active
                ? 'bg-secondary text-black shadow-sm'
                : 'bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 border border-zinc-200 dark:border-zinc-700'
        )}
    >
        {label}
    </button>
);

// Skeleton Component
export const Skeleton = ({ className }: { className?: string }) => (
    <div className={cn('animate-pulse bg-zinc-200 dark:bg-zinc-800 rounded-lg', className)} />
);

export { ThemeToggle } from './ThemeToggle';
