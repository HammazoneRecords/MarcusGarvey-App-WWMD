import { WwmdResponse } from '../types/wwmd';

const apiRoot = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '');
const API_BASE = `${apiRoot}/api`;
const withApi = (path: string) => `${API_BASE}${path}`;

export const ArkService = {
    getLatestAuth: async (): Promise<WwmdResponse | null> => {
        try {
            const response = await fetch(withApi('/latest'));
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            if (data.error) {
                console.warn('Vault Error:', data.error);
                return null;
            }
            return data as WwmdResponse;
        } catch (error) {
            console.error('Failed to fetch from ARK Vault:', error);
            return null;
        }
    },

    getHistory: async () => {
        try {
            const response = await fetch(withApi('/history'));
            return await response.json();
        } catch (error) {
            return [];
        }
    },

    getSession: async (filename: string): Promise<WwmdResponse | null> => {
        try {
            const response = await fetch(withApi(`/session?file=${filename}`));
            if (!response.ok) return null;
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch session:', error);
            return null;
        }
    },

    askQuestion: async (query: string): Promise<WwmdResponse | null> => {
        try {
            const response = await fetch(withApi('/chat'), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });
            if (!response.ok) throw new Error('Network response was not ok');
            return await response.json();
        } catch (error) {
            console.error('Failed to ask question:', error);
            return null;
        }
    }
};
