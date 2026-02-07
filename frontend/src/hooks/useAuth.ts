import { useState, useEffect } from 'react';
import type { User, Session } from '@supabase/supabase-js';
import { supabase, isSupabaseConfigured } from '../services/supabase';

export interface AuthState {
    user: User | null;
    session: Session | null;
    loading: boolean;
    isConfigured: boolean;
    signIn: (email: string, password: string) => Promise<{ error: Error | null }>;
    signUp: (email: string, password: string) => Promise<{ error: Error | null }>;
    signOut: () => Promise<void>;
}

export function useAuth(): AuthState {
    const [user, setUser] = useState<User | null>(null);
    const [session, setSession] = useState<Session | null>(null);
    const [loading, setLoading] = useState(true);

    const configured = isSupabaseConfigured();

    useEffect(() => {
        if (!supabase) {
            setLoading(false);
            return;
        }

        supabase.auth.getSession().then(({ data: { session: s } }) => {
            setSession(s);
            setUser(s?.user ?? null);
            setLoading(false);
        });

        const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, s) => {
            setSession(s);
            setUser(s?.user ?? null);
        });

        return () => subscription.unsubscribe();
    }, []);

    const signIn = async (email: string, password: string) => {
        if (!supabase) return { error: new Error('Supabase not configured') };
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        return { error: error ?? null };
    };

    const signUp = async (email: string, password: string) => {
        if (!supabase) return { error: new Error('Supabase not configured') };
        const { error } = await supabase.auth.signUp({ email, password });
        return { error: error ?? null };
    };

    const signOut = async () => {
        if (supabase) await supabase.auth.signOut();
    };

    return {
        user,
        session,
        loading: configured ? loading : false,
        isConfigured: configured,
        signIn,
        signUp,
        signOut,
    };
}
