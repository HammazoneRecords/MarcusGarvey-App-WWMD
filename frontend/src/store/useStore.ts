import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { WWMDResponse } from '../types';

interface AppState {
    theme: 'light' | 'dark';
    savedFactIds: string[];
    toolkitEdits: Record<string, string>; // templateId -> customMarkdown
    savedLensResults: WWMDResponse[];
    recentWWMDIds: string[]; // for now just keeping track of count/history

    // Actions
    setTheme: (theme: 'light' | 'dark') => void;
    toggleTheme: () => void;
    toggleSavedFact: (id: string) => void;
    saveToolkitEdit: (id: string, markdown: string) => void;
    saveLensResult: (result: WWMDResponse) => void;
    addWWMDSession: () => void;
}

export const useStore = create<AppState>()(
    persist(
        (set) => ({
            theme: 'light',
            savedFactIds: [],
            toolkitEdits: {},
            savedLensResults: [],
            recentWWMDIds: [],

            setTheme: (theme) => set({ theme }),
            toggleTheme: () => set((state) => ({
                theme: state.theme === 'light' ? 'dark' : 'light'
            })),
            toggleSavedFact: (id) => set((state) => ({
                savedFactIds: state.savedFactIds.includes(id)
                    ? state.savedFactIds.filter(fid => fid !== id)
                    : [...state.savedFactIds, id]
            })),
            saveToolkitEdit: (id, markdown) => set((state) => ({
                toolkitEdits: { ...state.toolkitEdits, [id]: markdown }
            })),
            saveLensResult: (result) => set((state) => {
                // Prevent duplicates based on query/situation
                const exists = state.savedLensResults.some(r => r.query === result.query);
                if (exists) return state;
                return { savedLensResults: [result, ...state.savedLensResults] };
            }),
            addWWMDSession: () => set((state) => ({
                recentWWMDIds: [...state.recentWWMDIds, new Date().toISOString()].slice(-10)
            })),
        }),
        {
            name: 'garvey-compass-storage',
            storage: createJSONStorage(() => localStorage),
        }
    )
);
