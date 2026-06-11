import { useEffect, useRef } from 'react';
import { useAuth } from './useAuth';
import { fetchAllUserData, addSavedFact, upsertLensResult, upsertToolkitEdit } from '../services/userData';
import { trackSync } from '../services/syncHelpers';
import { useStore } from '../store/useStore';

/**
 * Hydrates the store with the signed-in user's data from the backend.
 * Mount once inside the app (e.g. in App.tsx inside BrowserRouter).
 *
 * Before adopting the server snapshot, pushes up anything saved on this device
 * that the server doesn't have yet (saved while signed out, or left over from a
 * sync that previously failed) — local storage is a sync point, not a second
 * source of truth, so nothing on-device should be silently dropped on overwrite.
 */
export function useUserDataSync() {
    const { user } = useAuth();
    const setUserDataSnapshot = useStore((s) => s.setUserDataSnapshot);
    const lastUserIdRef = useRef<number | null>(null);

    useEffect(() => {
        if (!user?.id) {
            lastUserIdRef.current = null;
            return;
        }
        if (lastUserIdRef.current === user.id) return;
        lastUserIdRef.current = user.id;

        let cancelled = false;

        (async () => {
            const { data: serverData, error } = await fetchAllUserData();
            if (cancelled || error) return;

            const local = useStore.getState();

            const localOnlyFactIds = local.savedFactIds.filter((id) => !serverData.savedFactIds.includes(id));
            localOnlyFactIds.forEach((id) =>
                trackSync(`fact-${id}`, "Couldn't sync a saved item from this device", () => addSavedFact(id))
            );

            const serverResultIds = new Set(serverData.savedLensResults.map((r) => r.id));
            const localOnlyResults = local.savedLensResults.filter((r) => r.id && !serverResultIds.has(r.id));

            // Results that exist on both but whose checked action steps differ on this
            // device (e.g. an earlier toggle's sync failed) — re-push those too.
            const unsyncedExistingResults = local.savedLensResults.filter((r) => {
                if (!r.id || !serverResultIds.has(r.id)) return false;
                const localSteps = [...(local.savedActionSteps[r.id] ?? [])].sort();
                const serverSteps = [...(serverData.savedActionSteps[r.id] ?? [])].sort();
                return JSON.stringify(localSteps) !== JSON.stringify(serverSteps);
            });

            [...localOnlyResults, ...unsyncedExistingResults].forEach((r) => {
                const checked = local.savedActionSteps[r.id!] ?? [];
                trackSync(`lens-${r.id}`, "Couldn't sync a saved result from this device", () => upsertLensResult(r.id!, r, checked));
            });

            const localOnlyToolkitIds = Object.keys(local.toolkitEdits).filter((id) => !(id in serverData.toolkitEdits));
            localOnlyToolkitIds.forEach((id) =>
                trackSync(`toolkit-${id}`, "Couldn't sync a toolkit edit from this device", () => upsertToolkitEdit(id, local.toolkitEdits[id]))
            );

            const merged = {
                savedFactIds: Array.from(new Set([...serverData.savedFactIds, ...localOnlyFactIds])),
                savedLensResults: [...serverData.savedLensResults, ...localOnlyResults],
                savedActionSteps: { ...serverData.savedActionSteps, ...local.savedActionSteps },
                toolkitEdits: { ...serverData.toolkitEdits, ...local.toolkitEdits },
            };

            if (!cancelled) setUserDataSnapshot(merged);
        })();

        return () => {
            cancelled = true;
        };
    }, [user?.id, setUserDataSnapshot]);
}
