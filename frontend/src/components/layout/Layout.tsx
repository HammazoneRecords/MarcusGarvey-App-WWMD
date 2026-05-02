import React, { useState } from 'react';
import { BottomNav } from './BottomNav';
import { GlobalSidebar } from './GlobalSidebar';
import { ThemeToggle } from '../ui/ThemeToggle';
import { TestingPanel } from '../../testing-panel';
import { testingPanelConfig } from '../../testing-panel/testingPanelConfig';

const TESTING_PANEL_EXPANDED_WIDTH = '18rem'; /* w-72 */
const TESTING_PANEL_COLLAPSED_WIDTH = '2.5rem'; /* w-10 */
const TESTING_PANEL_VISIBLE = false;

export const Layout = ({ children, title }: { children: React.ReactNode; title?: string }) => {
    const [testingPanelExpanded, setTestingPanelExpanded] = useState(true);

    return (
        <div className="min-h-screen bg-background text-foreground flex transition-colors duration-300 font-sans selection:bg-primary/20">
            {/* Desktop Sidebar (Left Rail) */}
            <GlobalSidebar />

            <div
                className="flex-1 flex flex-col min-w-0 relative transition-[margin-right] duration-200"
                style={{
                    marginRight: TESTING_PANEL_VISIBLE ? (testingPanelExpanded ? TESTING_PANEL_EXPANDED_WIDTH : TESTING_PANEL_COLLAPSED_WIDTH) : 0,
                }}
            >
                {/* Header - Sticky on Mobile/Desktop */}
                <header className="sticky top-0 z-40 w-full bg-zinc-100/90 dark:bg-background/80 backdrop-blur-md h-16 flex items-center justify-between px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center gap-3">
                        <h1 className="text-lg font-bold truncate">
                            {title || 'Home'}
                        </h1>
                    </div>
                    <div className="flex items-center gap-2">
                        <ThemeToggle />
                    </div>
                </header>

                {/* Main Content Area - Full Width, No Constraints */}
                <main className="flex-1 w-full max-w-[1920px] mx-auto p-4 sm:p-6 lg:p-8 pb-24 md:pb-8">
                    <div className="animate-in fade-in duration-500 slide-in-from-bottom-2">
                        {children}
                    </div>
                </main>

                {/* Mobile Bottom Nav (Hidden on Desktop) */}
                <div className="md:hidden">
                    <BottomNav />
                </div>
            </div>

            {/* Right-side Testing Feature Panel (collapsible); layout reserves space when expanded */}
            <TestingPanel
                config={testingPanelConfig}
                visible={TESTING_PANEL_VISIBLE}
                onExpandChange={setTestingPanelExpanded}
            />
        </div>
    );
};
