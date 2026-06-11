import { useState } from 'react';
import { WWMDForm } from '../components/wwmd/WWMDForm';
import { ResponseView } from '../components/wwmd/ResponseView';
import { submitWWMD } from '../services/api';
import { WWMDRequest, WWMDResponse } from '../types';
import { useStore } from '../store/useStore';
import { useAuth } from '../hooks/useAuth';
import { upsertLensResult } from '../services/userData';
import { trackSync } from '../services/syncHelpers';
import { useIdentity } from '../hooks/useIdentity';

const API_BASE = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '');

export const WWMD = () => {
    const [loading, setLoading] = useState(false);
    const [response, setResponse] = useState<WWMDResponse | null>(null);
    const { user } = useAuth();
    const { addWWMDSession } = useStore();
    const { userName, sessionId } = useIdentity();

    const commitResult = (result: WWMDResponse, situation: string) => {
        const resultWithQuery = { ...result, query: situation, id: result.id || `lens-${Date.now()}` };
        setResponse(resultWithQuery);
        addWWMDSession();
        useStore.getState().saveLensResult(resultWithQuery);
        if (user?.id) {
            const resultId = resultWithQuery.id ?? resultWithQuery.query ?? `lens-${Date.now()}`;
            const checked = useStore.getState().savedActionSteps[resultId] ?? [];
            trackSync(`lens-${resultId}`, "Couldn't sync this result — saved on this device only", () => upsertLensResult(resultId, resultWithQuery, checked));
        }
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleApplyLens = async (data: WWMDRequest) => {
        setLoading(true);
        const apiConfig = useStore.getState().apiConfig;

        // Try streaming endpoint first — keeps connection alive during generation
        try {
            const res = await fetch(`${API_BASE}/api/wwmd/stream`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    situation: data.situation,
                    mode: data.mode ?? 'Personal',
                    apiConfig,
                    user_name: userName || 'friend',
                    session_id: sessionId,
                }),
            });

            if (res.ok && res.body) {
                const reader = res.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });
                    const parts = buffer.split('\n\n');
                    buffer = parts.pop() ?? '';

                    for (const part of parts) {
                        if (!part.startsWith('data: ')) continue;
                        try {
                            const event = JSON.parse(part.slice(6));
                            if (event.type === 'done' && event.data) {
                                commitResult(event.data as WWMDResponse, data.situation);
                            } else if (event.type === 'error') {
                                console.error('Stream error:', event.message);
                            }
                        } catch (_) { /* skip malformed SSE line */ }
                    }
                }
                setLoading(false);
                return; // streaming succeeded
            }
        } catch (streamErr) {
            console.warn('Streaming endpoint unavailable, falling back:', streamErr);
        }

        // Fallback: original non-streaming call
        try {
            const result = await submitWWMD({ ...data, mode: data.mode ?? 'Personal', apiConfig, user_name: userName || 'friend', session_id: sessionId } as any);
            commitResult(result, data.situation);
        } catch (error) {
            console.error("Failed to apply lens", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            {!response ? (
                <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                    <div className="mb-8">
                        <h1 className="text-3xl font-display font-bold mb-2">What Would Marcus Do?</h1>
                        <p className="text-zinc-600 dark:text-zinc-400">
                            {userName
                                ? `Welcome back, ${userName}. Tell Marcus what you're facing, and he'll tell you — in his own words — exactly what he would do.`
                                : "Tell Marcus what you're facing, and he'll tell you — in his own words — exactly what he would do."}
                        </p>
                    </div>

                    <WWMDForm onSubmit={handleApplyLens} loading={loading} />

                    <div className="mt-12 p-6 rounded-2xl bg-zinc-100 dark:bg-zinc-800/50 border border-zinc-200 dark:border-zinc-800">
                        <h3 className="text-xs font-bold uppercase tracking-widest text-zinc-500 mb-2">How it works</h3>
                        <p className="text-sm text-zinc-500 leading-relaxed">
                            Describe your situation and Marcus answers as himself — first person, grounded in his own writings and the history of the U.N.I.A. — telling you plainly what he would do, why, and what he'd have you do next.
                        </p>
                    </div>
                </div>
            ) : (
                <ResponseView response={response} onReset={() => setResponse(null)} />
            )}
        </div>
    );
};
