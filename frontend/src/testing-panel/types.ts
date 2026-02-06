/**
 * Types for the reusable Testing Feature Panel.
 * Copy this file + TestingPanel.tsx + your config to any site.
 */

export interface TestingPanelItem {
  id: string;
  label: string;
}

export interface TestingPanelPageConfig {
  /** Route path (exact or prefix, e.g. "/" or "/facts") */
  path: string;
  /** Display name for the page */
  label: string;
  items: TestingPanelItem[];
}

export interface TestingPanelConfig {
  /** Site name (e.g. "WhirlwindDB") */
  siteName: string;
  /** localStorage key prefix so multiple sites don't clash */
  storageKey: string;
  pages: TestingPanelPageConfig[];
}
