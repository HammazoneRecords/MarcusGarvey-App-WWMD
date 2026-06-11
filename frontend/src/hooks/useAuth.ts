import { useState, useEffect, useCallback } from 'react';

const apiRoot = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '');
const API_BASE = `${apiRoot}/api`;

const TOKEN_KEY = 'marcus_auth_token';

export interface AuthUser {
    id: number;
    email: string;
}

export interface AuthState {
    user: AuthUser | null;
    loading: boolean;
    isConfigured: boolean;
    requestMagicLink: (email: string) => Promise<{ error: Error | null }>;
    verifyMagicLink: (token: string) => Promise<{ error: Error | null }>;
    signOut: () => void;
}

export function getAuthToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
}

function setAuthToken(token: string | null) {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
}

export function useAuth(): AuthState {
    const [user, setUser] = useState<AuthUser | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = getAuthToken();
        if (!token) {
            setLoading(false);
            return;
        }
        fetch(`${API_BASE}/auth/me`, {
            headers: { Authorization: `Bearer ${token}` },
        })
            .then((res) => (res.ok ? res.json() : null))
            .then((data) => {
                if (data?.user) setUser(data.user);
                else setAuthToken(null);
            })
            .catch(() => setAuthToken(null))
            .finally(() => setLoading(false));
    }, []);

    const requestMagicLink = useCallback(async (email: string) => {
        try {
            const res = await fetch(`${API_BASE}/auth/request`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email }),
            });
            const data = await res.json();
            if (!res.ok) return { error: new Error(data.error || 'Failed to send magic link') };
            return { error: null };
        } catch (e) {
            return { error: e instanceof Error ? e : new Error('Failed to send magic link') };
        }
    }, []);

    const verifyMagicLink = useCallback(async (token: string) => {
        try {
            const res = await fetch(`${API_BASE}/auth/verify?token=${encodeURIComponent(token)}`);
            const data = await res.json();
            if (!res.ok) return { error: new Error(data.error || 'Invalid or expired link') };
            setAuthToken(data.token);
            setUser(data.user);
            return { error: null };
        } catch (e) {
            return { error: e instanceof Error ? e : new Error('Invalid or expired link') };
        }
    }, []);

    const signOut = useCallback(() => {
        setAuthToken(null);
        setUser(null);
    }, []);

    return {
        user,
        loading,
        isConfigured: true,
        requestMagicLink,
        verifyMagicLink,
        signOut,
    };
}
