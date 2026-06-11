import { useUserDataSync } from '../hooks/useUserDataSync';

/** Renders nothing; runs sync effect to hydrate store from the backend when user signs in. */
export function UserDataSync() {
    useUserDataSync();
    return null;
}
