import type { TestingPanelConfig } from './types';

/**
 * Site-specific testing checklist. Edit this to match your routes and features.
 * On another site: copy types.ts + TestingPanel.tsx and replace this config.
 */
export const testingPanelConfig: TestingPanelConfig = {
  siteName: 'WhirlwindDB',
  storageKey: 'whirlwinddb-testing-panel',
  pages: [
    {
      path: '/',
      label: 'Home',
      items: [
        { id: 'daily-card', label: 'Daily reflection card' },
        { id: 'gallery', label: 'Gallery section' },
        { id: 'library-cta', label: 'Library call-to-action link' },
        { id: 'lens-cta', label: 'Garvey Lens / WWMD call-to-action' },
        { id: 'legal-disclaimer', label: 'Legal disclaimer' },
      ],
    },
    {
      path: '/library',
      label: 'Library',
      items: [
        { id: 'search', label: 'Search input' },
        { id: 'category-chips', label: 'Category filter chips' },
        { id: 'lens-results-category', label: 'Lens Results category' },
        { id: 'fact-cards', label: 'Fact cards (Verified Claims)' },
        { id: 'lens-result-cards', label: 'Lens result cards (when Lens Results selected)' },
        { id: 'lens-card-click', label: 'Click lens card opens detail modal' },
        { id: 'access-source', label: 'Access Source on receipt/source item' },
        { id: 'source-modal', label: 'Source viewer modal with section highlight' },
        { id: 'more-filters', label: 'More filters toggle' },
      ],
    },
    {
      path: '/wwmd',
      label: 'Garvey Lens (WWMD)',
      items: [
        { id: 'situation-input', label: 'Situation text area' },
        { id: 'mode-toggle', label: 'Mode (Personal / Community)' },
        { id: 'tone-select', label: 'Tone (Practical / Strict / Gentle)' },
        { id: 'submit-button', label: 'Submit / Apply Lens button' },
        { id: 'principle-card', label: 'Principle response card' },
        { id: 'historical-analogy', label: 'Historical analogy section' },
        { id: 'action-steps', label: 'Recommended action steps (checkboxes)' },
        { id: 'grounded-receipts', label: 'Grounded receipts / sources' },
        { id: 'access-source-wwmd', label: 'Access Source on receipt (opens section modal)' },
        { id: 'mirror-questions', label: 'Garvey Mirror questions' },
        { id: 'start-over', label: 'Start Over / New Analysis' },
      ],
    },
    {
      path: '/toolkit',
      label: 'Toolkit',
      items: [
        { id: 'template-cards', label: 'Template cards list' },
        { id: 'template-link', label: 'Open template detail' },
        { id: 'info-card', label: 'Toolkit info card' },
      ],
    },
    {
      path: '/toolkit/',
      label: 'Template Detail',
      items: [
        { id: 'back-nav', label: 'Back navigation' },
        { id: 'template-title', label: 'Template title' },
        { id: 'template-description', label: 'Template description' },
        { id: 'markdown-content', label: 'Markdown content / editor' },
        { id: 'edit-save', label: 'Edit and save template' },
      ],
    },
    {
      path: '/facts/',
      label: 'Fact Detail',
      items: [
        { id: 'back-nav', label: 'Back navigation' },
        { id: 'claim', label: 'Claim display' },
        { id: 'context', label: 'Context section' },
        { id: 'impact-trail', label: 'Impact trail' },
        { id: 'receipts', label: 'Receipts / sources list' },
        { id: 'access-source-fact', label: 'Access Source on receipt' },
      ],
    },
    {
      path: '/profile',
      label: 'Profile',
      items: [
        { id: 'stats-cards', label: 'Stats cards (saved facts, sessions)' },
        { id: 'about-whirlwinddb', label: 'About WhirlwindDB text' },
        { id: 'lens-disclaimer', label: 'Garvey Lens disclaimer' },
        { id: 'theme-toggle', label: 'Theme toggle (if on profile)' },
      ],
    },
  ],
};
