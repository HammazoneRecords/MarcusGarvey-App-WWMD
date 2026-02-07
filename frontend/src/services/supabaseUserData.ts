import { supabase, isSupabaseConfigured } from './supabase';
import type { WWMDResponse } from '../types';

export interface UserSavedFactRow {
  id: string;
  user_id: string;
  fact_id: string;
  created_at: string;
}

export interface UserLensResultRow {
  id: string;
  user_id: string;
  result_id: string;
  payload: WWMDResponse;
  checked_action_step_ids: string[];
  created_at: string;
}

export interface UserToolkitEditRow {
  id: string;
  user_id: string;
  template_id: string;
  markdown: string;
  updated_at: string;
}

// ---- Saved facts ----

export async function fetchUserSavedFacts(userId: string): Promise<{ data: string[]; error: Error | null }> {
  if (!supabase) return { data: [], error: new Error('Supabase not configured') };
  const { data, error } = await supabase
    .from('user_saved_facts')
    .select('fact_id')
    .eq('user_id', userId)
    .order('created_at', { ascending: true });
  if (error) return { data: [], error };
  const factIds = (data ?? []).map((r: { fact_id: string }) => r.fact_id);
  return { data: factIds, error: null };
}

export async function addSavedFact(userId: string, factId: string): Promise<{ error: Error | null }> {
  if (!supabase) return { error: new Error('Supabase not configured') };
  const { error } = await supabase.from('user_saved_facts').insert({ user_id: userId, fact_id: factId });
  return { error: error ?? null };
}

export async function removeSavedFact(userId: string, factId: string): Promise<{ error: Error | null }> {
  if (!supabase) return { error: new Error('Supabase not configured') };
  const { error } = await supabase
    .from('user_saved_facts')
    .delete()
    .eq('user_id', userId)
    .eq('fact_id', factId);
  return { error: error ?? null };
}

// ---- Lens results ----

export async function fetchUserLensResults(
  userId: string
): Promise<{ data: { resultId: string; payload: WWMDResponse; checkedActionStepIds: string[] }[]; error: Error | null }> {
  if (!supabase) return { data: [], error: new Error('Supabase not configured') };
  const { data, error } = await supabase
    .from('user_lens_results')
    .select('result_id, payload, checked_action_step_ids')
    .eq('user_id', userId)
    .order('created_at', { ascending: false });
  if (error) return { data: [], error };
  const rows = (data ?? []).map((r: { result_id: string; payload: WWMDResponse; checked_action_step_ids: string[] }) => ({
    resultId: r.result_id,
    payload: r.payload,
    checkedActionStepIds: r.checked_action_step_ids ?? [],
  }));
  return { data: rows, error: null };
}

export async function upsertLensResult(
  userId: string,
  resultId: string,
  payload: WWMDResponse,
  checkedActionStepIds: string[]
): Promise<{ error: Error | null }> {
  if (!supabase) return { error: new Error('Supabase not configured') };
  const { error } = await supabase.from('user_lens_results').upsert(
    {
      user_id: userId,
      result_id: resultId,
      payload,
      checked_action_step_ids: checkedActionStepIds,
    },
    { onConflict: 'user_id,result_id' }
  );
  return { error: error ?? null };
}

export async function updateLensResultCheckedSteps(
  userId: string,
  resultId: string,
  checkedActionStepIds: string[]
): Promise<{ error: Error | null }> {
  if (!supabase) return { error: new Error('Supabase not configured') };
  const { error } = await supabase
    .from('user_lens_results')
    .update({ checked_action_step_ids: checkedActionStepIds })
    .eq('user_id', userId)
    .eq('result_id', resultId);
  return { error: error ?? null };
}

// ---- Toolkit edits ----

export async function fetchUserToolkitEdits(
  userId: string
): Promise<{ data: Record<string, string>; error: Error | null }> {
  if (!supabase) return { data: {}, error: new Error('Supabase not configured') };
  const { data, error } = await supabase
    .from('user_toolkit_edits')
    .select('template_id, markdown')
    .eq('user_id', userId);
  if (error) return { data: {}, error };
  const edits: Record<string, string> = {};
  for (const r of data ?? []) {
    edits[(r as { template_id: string; markdown: string }).template_id] = (r as { template_id: string; markdown: string }).markdown;
  }
  return { data: edits, error: null };
}

export async function upsertToolkitEdit(
  userId: string,
  templateId: string,
  markdown: string
): Promise<{ error: Error | null }> {
  if (!supabase) return { error: new Error('Supabase not configured') };
  const { error } = await supabase.from('user_toolkit_edits').upsert(
    {
      user_id: userId,
      template_id: templateId,
      markdown,
      updated_at: new Date().toISOString(),
    },
    { onConflict: 'user_id,template_id' }
  );
  return { error: error ?? null };
}

// ---- Hydration: fetch all user data in one place ----

export interface UserDataSnapshot {
  savedFactIds: string[];
  savedLensResults: WWMDResponse[];
  savedActionSteps: Record<string, string[]>;
  toolkitEdits: Record<string, string>;
}

export async function fetchAllUserData(userId: string): Promise<{ data: UserDataSnapshot; error: Error | null }> {
  if (!isSupabaseConfigured()) {
    return {
      data: { savedFactIds: [], savedLensResults: [], savedActionSteps: {}, toolkitEdits: {} },
      error: new Error('Supabase not configured'),
    };
  }

  const [factsRes, lensRes, editsRes] = await Promise.all([
    fetchUserSavedFacts(userId),
    fetchUserLensResults(userId),
    fetchUserToolkitEdits(userId),
  ]);

  const empty: UserDataSnapshot = { savedFactIds: [], savedLensResults: [], savedActionSteps: {}, toolkitEdits: {} };
  if (factsRes.error) return { data: empty, error: factsRes.error };
  if (lensRes.error) return { data: empty, error: lensRes.error };
  if (editsRes.error) return { data: empty, error: editsRes.error };

  const savedLensResults: WWMDResponse[] = lensRes.data.map((r) => ({
    ...r.payload,
    id: r.resultId,
    query: r.payload.query ?? r.resultId,
  }));
  const savedActionSteps: Record<string, string[]> = {};
  for (const r of lensRes.data) {
    savedActionSteps[r.resultId] = r.checkedActionStepIds;
  }

  return {
    data: {
      savedFactIds: factsRes.data,
      savedLensResults,
      savedActionSteps,
      toolkitEdits: editsRes.data,
    },
    error: null,
  };
}
