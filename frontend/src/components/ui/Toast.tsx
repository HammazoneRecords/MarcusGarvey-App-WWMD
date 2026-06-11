import { X, RotateCw } from 'lucide-react';
import { useToastStore } from '../../store/useToastStore';

/** Fixed-position stack of sync-failure toasts with retry/dismiss. */
export const ToastContainer = () => {
    const toasts = useToastStore((s) => s.toasts);
    const removeToast = useToastStore((s) => s.removeToast);

    if (toasts.length === 0) return null;

    return (
        <div className="fixed bottom-20 md:bottom-6 left-1/2 -translate-x-1/2 z-[100] flex flex-col gap-2 w-[calc(100%-2rem)] max-w-sm">
            {toasts.map((toast) => (
                <div
                    key={toast.id}
                    className="flex items-center gap-3 px-4 py-3 rounded-xl bg-zinc-900 dark:bg-zinc-800 text-white text-sm shadow-lg border border-zinc-700"
                >
                    <span className="flex-1">{toast.message}</span>
                    {toast.retry && (
                        <button
                            onClick={toast.retry}
                            className="flex items-center gap-1 text-xs font-bold uppercase tracking-wide text-secondary hover:opacity-80 shrink-0"
                        >
                            <RotateCw className="w-3.5 h-3.5" />
                            Retry
                        </button>
                    )}
                    <button onClick={() => removeToast(toast.id)} className="text-zinc-400 hover:text-white shrink-0">
                        <X className="w-4 h-4" />
                    </button>
                </div>
            ))}
        </div>
    );
};
