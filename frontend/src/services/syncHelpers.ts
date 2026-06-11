import { useToastStore } from '../store/useToastStore';

/**
 * Runs a server-sync call. On failure, surfaces a retryable toast (deduped by `id`)
 * so a failed save isn't silently lost when the local snapshot gets overwritten
 * by the server on next reload. On success, clears any pending toast for `id`.
 */
export function trackSync(id: string, message: string, run: () => Promise<{ error: Error | null }>) {
    run().then(({ error }) => {
        if (error) {
            useToastStore.getState().addToast({
                id,
                message,
                retry: () => trackSync(id, message, run),
            });
        } else {
            useToastStore.getState().removeToast(id);
        }
    });
}
