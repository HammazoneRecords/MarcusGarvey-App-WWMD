import { useState } from 'react';
import { WWMDForm } from '../components/wwmd/WWMDForm';
import { ResponseView } from '../components/wwmd/ResponseView';
import { submitWWMD } from '../services/api';
import { WWMDRequest, WWMDResponse } from '../types';
import { useStore } from '../store/useStore';
import { useAuth } from '../hooks/useAuth';
import { upsertLensResult } from '../services/supabaseUserData';

export const WWMD = () => {
    const [loading, setLoading] = useState(false);
    const [response, setResponse] = useState<WWMDResponse | null>(null);
    const { user } = useAuth();
    const { addWWMDSession } = useStore();

    const handleApplyLens = async (data: WWMDRequest) => {
        setLoading(true);
        try {
            const currentApiConfig = useStore.getState().apiConfig;
            const result = await submitWWMD({ ...data, mode: data.mode ?? 'Personal', apiConfig: currentApiConfig });
            // Ensure query and stable id for saved action steps
            const resultWithQuery = { ...result, query: data.situation, id: result.id || `lens-${Date.now()}` };

            setResponse(resultWithQuery);
            addWWMDSession();
            useStore.getState().saveLensResult(resultWithQuery);

            if (user?.id) {
                const resultId = resultWithQuery.id ?? resultWithQuery.query ?? `lens-${Date.now()}`;
                const checked = useStore.getState().savedActionSteps[resultId] ?? [];
                upsertLensResult(user.id, resultId, resultWithQuery, checked);
            }

            // Scroll to top to see response
            window.scrollTo({ top: 0, behavior: 'smooth' });
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
                        <h1 className="text-3xl font-display font-bold mb-2">Garvey Lens</h1>
                        <p className="text-zinc-600 dark:text-zinc-400">
                            Apply foundational principles of self-reliance and organization to your current challenges.
                        </p>
                    </div>

                    <WWMDForm onSubmit={handleApplyLens} loading={loading} />

                    <div className="mt-12 p-6 rounded-2xl bg-zinc-100 dark:bg-zinc-800/50 border border-zinc-200 dark:border-zinc-800">
                        <h3 className="text-xs font-bold uppercase tracking-widest text-zinc-500 mb-2">How it works</h3>
                        <p className="text-sm text-zinc-500 leading-relaxed">
                            The Garvey Lens uses a source-grounded model to analyze your situation through the framework of collective progress and institution building. It provides historical analogies and actionable steps derived from verified philosophy.
                        </p>
                    </div>
                </div>
            ) : (
                <ResponseView response={response} onReset={() => setResponse(null)} />
            )}
        </div>
    );
};
