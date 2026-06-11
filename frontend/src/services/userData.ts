import { getAuthToken } from '../hooks/useAuth';
import type { WWMDResponse } from '../types';

const apiRoot = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '');
const API_BASE = `${apiRoot}/api`;

export interface UserDataSnapshot {
  savedFactIds: string[];
  savedLensResults: WWMDResponse[];
  savedActionSteps: Record<string, string[]>;
  toolkitEdits: Record<string, string>;
}

function authHeaders(): Record<string, string> | null {
  const token = getAuthToken();
  if (!token) return null;
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  };
}

export async function addSavedFact(factId: string): Promise<{ error: Error | null }> {
  const headers = authHeaders();
  if (!headers) return { error: new Error('Not authenticated') };
  const res = await fetch(`${API_BASE}/user/saved-facts`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ fact_id: factId, action: 'add' }),
  });
  if (!res.ok) return { error: new Error('Failed to save fact') };
  return { error: null };
}

export async function removeSavedFact(factId: string): Promise<{ error: Error | null }> {
  const headers = authHeaders();
  if (!headers) return { error: new Error('Not authenticated') };
  const res = await fetch(`${API_BASE}/user/saved-facts`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ fact_id: factId, action: 'remove' }),
  });
  if (!res.ok) return { error: new Error('Failed to remove fact') };
  return { error: null };
}

export async function upsertLensResult(
  resultId: string,
  payload: WWMDResponse,
  checkedActionStepIds: string[]
): Promise<{ error: Error | null }> {
  const headers = authHeaders();
  if (!headers) return { error: new Error('Not authenticated') };
  const res = await fetch(`${API_BASE}/user/lens-results`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      result_id: resultId,
      payload,
      checked_action_step_ids: checkedActionStepIds,
    }),
  });
  if (!res.ok) return { error: new Error('Failed to save lens result') };
  return { error: null };
}

export async function upsertToolkitEdit(
  templateId: string,
  markdown: string
): Promise<{ error: Error | null }> {
  const headers = authHeaders();
  if (!headers) return { error: new Error('Not authenticated') };
  const res = await fetch(`${API_BASE}/user/toolkit-edits`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ template_id: templateId, markdown }),
  });
  if (!res.ok) return { error: new Error('Failed to save toolkit edit') };
  return { error: null };
}

export async function submitTTSLead(email: string, source?: string): Promise<{ error: Error | null }> {
  const res = await fetch(`${API_BASE}/leads/tts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, source }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    return { error: new Error(data.error || 'Failed to sign up') };
  }
  return { error: null };
}

export async function fetchAllUserData(): Promise<{ data: UserDataSnapshot; error: Error | null }> {
  const empty: UserDataSnapshot = { savedFactIds: [], savedLensResults: [], savedActionSteps: {}, toolkitEdits: {} };
  const headers = authHeaders();
  if (!headers) return { data: empty, error: new Error('Not authenticated') };

  const res = await fetch(`${API_BASE}/user/data`, { headers });
  if (!res.ok) return { data: empty, error: new Error('Failed to fetch user data') };
  const data = (await res.json()) as UserDataSnapshot;
  return { data, error: null };
}
