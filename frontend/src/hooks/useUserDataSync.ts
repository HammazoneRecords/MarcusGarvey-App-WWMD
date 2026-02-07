import { useEffect, useRef } from 'react';
import { useAuth } from './useAuth';
import { fetchAllUserData } from '../services/supabaseUserData';
import { useStore } from '../store/useStore';

/**
 * Hydrates the store with the signed-in user's data from Supabase.
 * Mount once inside the app (e.g. in App.tsx inside BrowserRouter).
 * When user signs in, fetches saved facts, lens results, toolkit edits and sets the store.
 */
export function useUserDataSync() {
    const { user } = useAuth();
    const setUserDataSnapshot = useStore((s) => s.setUserDataSnapshot);
    const lastUserIdRef = useRef<string | null>(null);

    useEffect(() => {
        if (!user?.id) {
            lastUserIdRef.current = null;
            return;
        }
        if (lastUserIdRef.current === user.id) return;
        lastUserIdRef.current = user.id;

        let cancelled = false;
        fetchAllUserData(user.id).then(({ data, error }) => {
            if (cancelled || error) return;
            setUserDataSnapshot(data);
        });
        return () => {
            cancelled = true;
        };
    }, [user?.id, setUserDataSnapshot]);
}
