import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { WWMDResponse } from '../types';

export type AIProvider = 'ollama' | 'openrouter' | 'openai' | 'gemini';

export interface ApiConfig {
    provider: AIProvider;
    useOwnAI: boolean;
    ollamaBaseUrl: string;
    openRouterApiKey: string;
    openAiBaseUrl: string;
    openAiApiKey: string;
    geminiApiKey: string;
}

interface AppState {
    theme: 'light' | 'dark';
    savedFactIds: string[];
    toolkitEdits: Record<string, string>; // templateId -> customMarkdown
    savedLensResults: WWMDResponse[];
    /** resultId -> array of action step ids the user checked */
    savedActionSteps: Record<string, string[]>;
    recentWWMDIds: string[]; // for now just keeping track of count/history
    apiConfig: ApiConfig;

    // Actions
    setTheme: (theme: 'light' | 'dark') => void;
    toggleTheme: () => void;
    toggleSavedFact: (id: string) => void;
    saveToolkitEdit: (id: string, markdown: string) => void;
    saveLensResult: (result: WWMDResponse) => void;
    toggleSavedActionStep: (resultId: string, stepId: string) => void;
    addWWMDSession: () => void;
    setApiConfig: (config: Partial<ApiConfig>) => void;
    /** Replace user-data from server (used by sync layer on login). */
    setUserDataSnapshot: (data: {
        savedFactIds: string[];
        savedLensResults: WWMDResponse[];
        savedActionSteps: Record<string, string[]>;
        toolkitEdits: Record<string, string>;
    }) => void;
    /** Clear all user data (called on sign out) */
    clearUserData: () => void;
}

export const useStore = create<AppState>()(
    persist(
        (set) => ({
            theme: 'light',
            savedFactIds: [],
            toolkitEdits: {},
            savedLensResults: [],
            savedActionSteps: {},
            recentWWMDIds: [],
            apiConfig: {
                provider: 'openai',
                useOwnAI: false,
                ollamaBaseUrl: 'http://localhost:11434',
                openRouterApiKey: '',
                openAiBaseUrl: '',
                openAiApiKey: '',
                geminiApiKey: '',
            },

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
            toggleSavedActionStep: (resultId, stepId) => set((state) => {
                const current = state.savedActionSteps[resultId] ?? [];
                const next = current.includes(stepId)
                    ? current.filter((id) => id !== stepId)
                    : [...current, stepId];
                return {
                    savedActionSteps: { ...state.savedActionSteps, [resultId]: next }
                };
            }),
            addWWMDSession: () => set((state) => ({
                recentWWMDIds: [...state.recentWWMDIds, new Date().toISOString()].slice(-10)
            })),
            setApiConfig: (config) => set((state) => ({
                apiConfig: { ...state.apiConfig, ...config }
            })),
            setUserDataSnapshot: (data) => set({
                savedFactIds: data.savedFactIds,
                savedLensResults: data.savedLensResults,
                savedActionSteps: data.savedActionSteps,
                toolkitEdits: data.toolkitEdits,
            }),
            clearUserData: () => set({
                savedFactIds: [],
                toolkitEdits: {},
                savedLensResults: [],
                savedActionSteps: {},
                recentWWMDIds: [],
                apiConfig: {
                    provider: 'openai',
                    useOwnAI: false,
                    ollamaBaseUrl: 'http://localhost:11434',
                    openRouterApiKey: '',
                    openAiBaseUrl: '',
                    openAiApiKey: '',
                    geminiApiKey: '',
                },
            }),
        }),
        {
            name: 'whirlwind-kb-storage',
            storage: createJSONStorage(() => localStorage),
        }
    )
);
