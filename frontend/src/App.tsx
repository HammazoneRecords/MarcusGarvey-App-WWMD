import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { Home, Library, Profile, Browse, Workflow, Log, DevOps } from './pages';
import { useStore } from './store/useStore';
import { useEffect } from 'react';

const WWMD = lazy(() => import('./pages/WWMD').then(m => ({ default: m.WWMD })));
const Toolkit = lazy(() => import('./pages/Toolkit').then(m => ({ default: m.Toolkit })));
const FactDetail = lazy(() => import('./pages/FactDetail').then(m => ({ default: m.FactDetail })));
const TemplateDetail = lazy(() => import('./pages/TemplateDetail').then(m => ({ default: m.TemplateDetail })));
const Privacy = lazy(() => import('./pages/Privacy').then(m => ({ default: m.Privacy })));
const Terms = lazy(() => import('./pages/Terms').then(m => ({ default: m.Terms })));

function App() {
    const { theme } = useStore();

    useEffect(() => {
        const root = window.document.documentElement;
        if (theme === 'dark') {
            root.classList.add('dark');
        } else {
            root.classList.remove('dark');
        }
    }, [theme]);

    return (
        <BrowserRouter>
            <Suspense fallback={<Layout title="Whirlwind KB"><div className="flex items-center justify-center min-h-[40vh] text-zinc-500">Loading…</div></Layout>}>
                <Routes>
                    <Route path="/" element={<Layout title="Whirlwind KB"><Home /></Layout>} />
                    <Route path="/library" element={<Layout title="Knowledge Base"><Library /></Layout>} />
                    <Route path="/facts/:id" element={<Layout title="Fact Detail"><FactDetail /></Layout>} />
                    <Route path="/wwmd" element={<Layout title="Garvey Lens"><WWMD /></Layout>} />
                    <Route path="/toolkit" element={<Layout title="Toolkit"><Toolkit /></Layout>} />
                    <Route path="/toolkit/:id" element={<Layout title="Template Detail"><TemplateDetail /></Layout>} />
                    <Route path="/profile" element={<Layout title="Profile"><Profile /></Layout>} />
                    <Route path="/browse" element={<Layout title="Browse"><Browse /></Layout>} />
                    <Route path="/workflow" element={<Layout title="Workflow"><Workflow /></Layout>} />
                    <Route path="/log" element={<Layout title="Log"><Log /></Layout>} />
                    <Route path="/devops" element={<Layout title="DevOps"><DevOps /></Layout>} />
                    <Route path="/privacy" element={<Layout title="Privacy"><Privacy /></Layout>} />
                    <Route path="/terms" element={<Layout title="Terms of Use"><Terms /></Layout>} />
                </Routes>
            </Suspense>
        </BrowserRouter>
    );
}

export default App;
