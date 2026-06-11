import { create } from 'zustand';

export interface ToastItem {
    id: string;
    message: string;
    retry?: () => void;
}

interface ToastState {
    toasts: ToastItem[];
    addToast: (toast: ToastItem) => void;
    removeToast: (id: string) => void;
}

/** Transient, non-persisted notifications — used for sync-failure warnings with retry. */
export const useToastStore = create<ToastState>()((set) => ({
    toasts: [],
    addToast: (toast) => set((state) => ({
        toasts: [...state.toasts.filter((t) => t.id !== toast.id), toast],
    })),
    removeToast: (id) => set((state) => ({
        toasts: state.toasts.filter((t) => t.id !== id),
    })),
}));
