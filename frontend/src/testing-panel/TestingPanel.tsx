import { useState, useEffect, useMemo } from 'react';
import { useLocation } from 'react-router-dom';
import { ClipboardCheck, ChevronLeft, ChevronRight, CheckCircle2, Circle, StickyNote } from 'lucide-react';
import { getTestingPanelState, saveTestingPanelState } from '../services/api';
import type { TestingPanelConfig, TestingPanelPageConfig } from './types';

const STORAGE_KEY_CHECKED = 'checked';
const STORAGE_KEY_NOTES = 'notes';

function loadCheckedSet(config: TestingPanelConfig): Set<string> {
  try {
    const raw = localStorage.getItem(`${config.storageKey}:${STORAGE_KEY_CHECKED}`);
    if (!raw) return new Set();
    const arr = JSON.parse(raw) as string[];
    return new Set(Array.isArray(arr) ? arr : []);
  } catch {
    return new Set();
  }
}

function saveCheckedSet(config: TestingPanelConfig, set: Set<string>): void {
  try {
    localStorage.setItem(`${config.storageKey}:${STORAGE_KEY_CHECKED}`, JSON.stringify([...set]));
  } catch (_) {}
}

function loadNotes(config: TestingPanelConfig): string[] {
  try {
    const raw = localStorage.getItem(`${config.storageKey}:${STORAGE_KEY_NOTES}`);
    if (!raw) return [];
    const arr = JSON.parse(raw) as string[];
    return Array.isArray(arr) ? arr : [];
  } catch {
    return [];
  }
}

function saveNotes(config: TestingPanelConfig, lines: string[]): void {
  try {
    localStorage.setItem(`${config.storageKey}:${STORAGE_KEY_NOTES}`, JSON.stringify(lines));
  } catch (_) {}
}

function findPageForPath(config: TestingPanelConfig, pathname: string): TestingPanelPageConfig | null {
  const exact = config.pages.find((p) => p.path === pathname);
  if (exact) return exact;
  const prefixMatches = config.pages.filter(
    (p) => p.path !== '/' && pathname.startsWith(p.path) && (pathname === p.path || pathname.length > p.path.length)
  );
  if (prefixMatches.length === 0) return null;
  prefixMatches.sort((a, b) => b.path.length - a.path.length);
  return prefixMatches[0];
}

interface TestingPanelProps {
  config: TestingPanelConfig;
  /** Optional: hide panel when false (e.g. only in dev or ?testing=1) */
  visible?: boolean;
  /** Called when panel expand/collapse state changes so layout can reserve space */
  onExpandChange?: (expanded: boolean) => void;
}

export function TestingPanel({ config, visible = true, onExpandChange }: TestingPanelProps) {
  const location = useLocation();
  const [expanded, setExpanded] = useState(true);
  const [checked, setChecked] = useState<Set<string>>(() => loadCheckedSet(config));
  const initialNotes = useMemo(() => loadNotes(config), []);
  const [notes, setNotes] = useState<string[]>(initialNotes);
  const [notesDraft, setNotesDraft] = useState(() => initialNotes.join('\n'));

  useEffect(() => {
    let cancelled = false;
    const fromLocal = { checked: loadCheckedSet(config), notes: loadNotes(config) };
    (async () => {
      const remote = await getTestingPanelState(config.storageKey);
      if (cancelled) return;
      const hasRemote = remote && (remote.checked.length > 0 || remote.notes.length > 0);
      if (hasRemote) {
        setChecked(new Set(remote!.checked));
        setNotes(remote!.notes);
        setNotesDraft(remote!.notes.join('\n'));
        saveCheckedSet(config, new Set(remote!.checked));
        saveNotes(config, remote!.notes);
      } else {
        setChecked(fromLocal.checked);
        setNotes(fromLocal.notes);
        setNotesDraft(fromLocal.notes.join('\n'));
        if (fromLocal.notes.length > 0 || fromLocal.checked.size > 0) {
          saveTestingPanelState(config.storageKey, {
            checked: [...fromLocal.checked],
            notes: fromLocal.notes,
          }).catch(() => {});
        }
      }
    })();
    return () => { cancelled = true; };
  }, [config.storageKey]);

  const setExpandedAndNotify = (value: boolean) => {
    setExpanded(value);
    onExpandChange?.(value);
  };

  const pathname = location.pathname;
  const currentPage = useMemo(() => findPageForPath(config, pathname), [config, pathname]);

  const allItemKeys = useMemo(() => {
    const keys: string[] = [];
    config.pages.forEach((p) => {
      p.items.forEach((i) => keys.push(`${p.path}:${i.id}`));
    });
    return keys;
  }, [config]);

  const totalItems = allItemKeys.length;
  const totalChecked = useMemo(() => allItemKeys.filter((k) => checked.has(k)).length, [allItemKeys, checked]);
  const overallProgress = totalItems ? Math.round((totalChecked / totalItems) * 100) : 0;

  const pageItems = currentPage?.items ?? [];
  const pageChecked = useMemo(() => {
    if (!currentPage) return 0;
    return currentPage.items.filter((i) => checked.has(`${currentPage.path}:${i.id}`)).length;
  }, [currentPage, checked]);
  const pageProgress = pageItems.length ? Math.round((pageChecked / pageItems.length) * 100) : 0;

  const toggle = (pagePath: string, itemId: string) => {
    const key = `${pagePath}:${itemId}`;
    setChecked((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      saveCheckedSet(config, next);
      saveTestingPanelState(config.storageKey, { checked: [...next], notes }).catch(() => {});
      return next;
    });
  };

  const saveNotesFromDraft = () => {
    const lines = notesDraft
      .split('\n')
      .map((s) => s.trim())
      .filter(Boolean);
    setNotes(lines);
    saveNotes(config, lines);
    saveTestingPanelState(config.storageKey, { checked: [...checked], notes: lines }).catch(() => {});
  };

  if (!visible) return null;

  return (
    <div
      className={`fixed top-0 bottom-0 z-40 flex flex-col bg-background border-l border-border shadow-xl transition-all duration-200 ${
        expanded ? 'w-72 right-0' : 'w-10 right-0'
      }`}
    >
      {expanded ? (
        <>
          <div className="flex items-center justify-between p-4 border-b border-border bg-muted/30">
            <div className="flex items-center gap-2 min-w-0">
              <ClipboardCheck className="w-5 h-5 text-primary shrink-0" />
              <span className="text-sm font-bold truncate">Test Panel</span>
            </div>
            <button
              type="button"
              onClick={() => setExpandedAndNotify(false)}
              className="p-2 rounded hover:bg-muted"
              aria-label="Collapse panel"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          <div className="p-4 border-b border-border space-y-2">
            <p className="text-sm font-medium text-muted-foreground">{config.siteName}</p>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Overall</span>
              <span className="font-bold">{totalChecked}/{totalItems} ({overallProgress}%)</span>
            </div>
            <div className="h-2 rounded-full bg-muted overflow-hidden">
              <div
                className="h-full bg-primary transition-all duration-300"
                style={{ width: `${overallProgress}%` }}
              />
            </div>
          </div>

          <div className="flex-1 overflow-y-auto min-h-0">
            {currentPage ? (
              <>
                <div className="px-4 py-3 border-b border-border flex items-center gap-2">
                  <span className="inline-block w-2 h-2 rounded-full bg-primary shrink-0" aria-hidden />
                  <span className="text-sm font-bold truncate">{currentPage.label}</span>
                  <span className="text-sm text-muted-foreground ml-auto">{pageChecked}/{pageItems.length}</span>
                </div>
                <div className="p-4 space-y-1">
                  {currentPage.items.map((item) => {
                    const key = `${currentPage.path}:${item.id}`;
                    const isChecked = checked.has(key);
                    return (
                      <label
                        key={item.id}
                        className={`flex items-center gap-3 py-3 px-2 rounded-lg cursor-pointer transition-colors min-h-[2.75rem] ${
                          isChecked ? 'bg-primary/10 text-muted-foreground' : 'hover:bg-muted/50'
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => toggle(currentPage.path, item.id)}
                          className="sr-only"
                        />
                        {isChecked ? (
                          <CheckCircle2 className="w-4 h-4 text-primary shrink-0" />
                        ) : (
                          <Circle className="w-4 h-4 text-muted-foreground shrink-0" />
                        )}
                        <span className="text-sm leading-snug truncate">{item.label}</span>
                      </label>
                    );
                  })}
                </div>
              </>
            ) : (
              <div className="flex items-center justify-center p-4 text-center text-sm text-muted-foreground leading-relaxed">
                No test list for this page. Add a matching path in your testing config.
              </div>
            )}

            <div className="border-t border-border p-4 bg-muted/20">
              <div className="flex items-center gap-2 mb-2">
                <StickyNote className="w-4 h-4 text-primary shrink-0" />
                <span className="text-sm font-bold">Notes</span>
              </div>
              <textarea
                value={notesDraft}
                onChange={(e) => setNotesDraft(e.target.value)}
                onBlur={saveNotesFromDraft}
                placeholder={'One bullet per line, e.g.\n• Info on /facts/fact-bsl to adjust\n• Copy on BSL page'}
                rows={4}
                className="w-full p-3 text-sm rounded-lg border border-border bg-background resize-y min-h-[5rem] focus:outline-none focus:ring-2 focus:ring-primary/50"
                aria-label="Testing notes (one bullet per line)"
              />
              {notes.length > 0 && (
                <ul className="mt-2 text-sm text-muted-foreground list-disc list-inside space-y-1">
                  {notes.map((line, i) => (
                    <li key={i} className="leading-snug">
                      {line}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </>
      ) : (
        <div className="flex flex-col items-center py-4 gap-2">
          <button
            type="button"
            onClick={() => setExpandedAndNotify(true)}
            className="p-2 rounded hover:bg-muted"
            aria-label="Expand panel"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <ClipboardCheck className="w-5 h-5 text-primary" />
          <span className="text-xs font-bold text-muted-foreground">{overallProgress}%</span>
        </div>
      )}
    </div>
  );
}
