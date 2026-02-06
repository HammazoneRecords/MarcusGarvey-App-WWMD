import { MOCK_FACTS, MOCK_DAILY, MOCK_TEMPLATES, MOCK_GALLERY } from '../mock/data';
import { Fact, DailyItem, ToolkitTemplate, WWMDRequest, WWMDResponse, GalleryItem, SourceSectionResponse } from '../types';

const LATENCY = 800;
const API_BASE = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '');
const withBase = (path: string) => `${API_BASE}${path}`;

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const getFacts = async (filters?: {
    search?: string;
    category?: string;
    confidence?: string;
}): Promise<Fact[]> => {
    if (API_BASE) {
        try {
            const params = new URLSearchParams();
            if (filters?.search) params.set('search', filters.search);
            if (filters?.category) params.set('category', filters.category);
            if (filters?.confidence) params.set('confidence', filters.confidence);
            const qs = params.toString();
            const url = withBase(`/api/library${qs ? `?${qs}` : ''}`);
            const response = await fetch(url);
            if (response.ok) {
                const data = await response.json();
                return (data.facts ?? []) as Fact[];
            }
        } catch (_) { /* fallback to mock */ }
    }
    await sleep(LATENCY);
    let results = [...MOCK_FACTS];
    if (filters?.search) {
        const q = filters.search.toLowerCase();
        results = results.filter(f => f.claim.toLowerCase().includes(q) || f.context.toLowerCase().includes(q));
    }
    if (filters?.category) {
        results = results.filter(f => f.categories.includes(filters.category!));
    }
    if (filters?.confidence) {
        results = results.filter(f => f.confidence === filters.confidence);
    }
    return results;
};

export const getFactById = async (id: string): Promise<Fact | undefined> => {
    if (API_BASE) {
        try {
            const response = await fetch(withBase(`/api/library/facts/${encodeURIComponent(id)}`));
            if (response.ok) return (await response.json()) as Fact;
        } catch (_) { /* fallback to mock */ }
    }
    await sleep(LATENCY);
    return MOCK_FACTS.find(f => f.id === id);
};

export const getDailyItem = async (): Promise<DailyItem> => {
    await sleep(LATENCY);
    // Pick a random one or based on date
    const day = new Date().getDate();
    return MOCK_DAILY[day % MOCK_DAILY.length];
};

export const getToolkitTemplates = async (): Promise<ToolkitTemplate[]> => {
    await sleep(LATENCY);
    return MOCK_TEMPLATES;
};

export const getToolkitTemplateById = async (id: string): Promise<ToolkitTemplate | undefined> => {
    await sleep(LATENCY);
    return MOCK_TEMPLATES.find(t => t.id === id);
};

export const submitWWMD = async (request: WWMDRequest): Promise<WWMDResponse> => {
    try {
        const response = await fetch(withBase('/api/wwmd'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request)
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        return await response.json();
    } catch (error) {
        console.error("Failed to submit WWMD lens:", error);
        // Fallback mock if server is down (optional, but good for stability)
        return {
            principle: "Connection Error (Fallback)",
            historicalAnalogy: "Could not connect to the ARK. Please ensure the backend server is running.",
            receipts: [],
            actionSteps: [{ id: "1", text: "Check server connection", completed: false }],
            mirrorQuestions: []
        };
    }
};

export const getGallery = async (): Promise<GalleryItem[]> => {
    await sleep(LATENCY);
    return MOCK_GALLERY;
};

/** Fetch section content for an internal source (anchor + optional locator). */
export const getSourceSection = async (
    anchorId: string,
    locator?: string
): Promise<SourceSectionResponse> => {
    const params = new URLSearchParams();
    if (locator) params.set('locator', locator);
    const qs = params.toString();
    const url = withBase(`/api/source/${encodeURIComponent(anchorId)}${qs ? `?${qs}` : ''}`);
    const response = await fetch(url);
    if (!response.ok) {
        const err = await response.json().catch(() => ({ error: response.statusText }));
        throw new Error(err.error || 'Failed to load source section');
    }
    return response.json();
};

/** Testing panel state from backend DB (fallback to undefined if backend unavailable). */
export interface TestingPanelState {
    checked: string[];
    notes: string[];
}

export const getTestingPanelState = async (storageKey: string): Promise<TestingPanelState | undefined> => {
    if (!API_BASE) return undefined;
    try {
        const url = withBase(`/api/testing-panel?storage_key=${encodeURIComponent(storageKey)}`);
        const response = await fetch(url);
        if (!response.ok) return undefined;
        return await response.json();
    } catch {
        return undefined;
    }
};

export const saveTestingPanelState = async (
    storageKey: string,
    payload: { checked?: string[]; notes?: string[] }
): Promise<boolean> => {
    if (!API_BASE) return false;
    try {
        const response = await fetch(withBase('/api/testing-panel'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ storage_key: storageKey, ...payload })
        });
        return response.ok;
    } catch {
        return false;
    }
};
