import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { UserDataSync } from './components/UserDataSync';
import { Home, Library, Profile, AuthVerify } from './pages';
import { useStore } from './store/useStore';
import { useEffect } from 'react';
import { useIdentity } from './hooks/useIdentity';
import { NameCaptureModal } from './components/ui/NameCaptureModal';
import { ToastContainer } from './components/ui';

const WWMD = lazy(() => import('./pages/WWMD').then(m => ({ default: m.WWMD })));
const Chat = lazy(() => import('./pages/Chat').then(m => ({ default: m.Chat })));
const Toolkit = lazy(() => import('./pages/Toolkit').then(m => ({ default: m.Toolkit })));
const FactDetail = lazy(() => import('./pages/FactDetail').then(m => ({ default: m.FactDetail })));
const TemplateDetail = lazy(() => import('./pages/TemplateDetail').then(m => ({ default: m.TemplateDetail })));
const Privacy = lazy(() => import('./pages/Privacy').then(m => ({ default: m.Privacy })));
const Terms = lazy(() => import('./pages/Terms').then(m => ({ default: m.Terms })));

function App() {
    const { theme } = useStore();
    const { needsName, setUserName } = useIdentity();

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
            {needsName && <NameCaptureModal onConfirm={setUserName} />}
            <UserDataSync />
            <ToastContainer />
            <Suspense fallback={<Layout title="Home"><div className="flex items-center justify-center min-h-[40vh] text-zinc-500">Loading…</div></Layout>}>
                <Routes>
                    <Route path="/" element={<Navigate to="/home" replace />} />
                    <Route path="/home" element={<Layout title="Home"><Home /></Layout>} />
                    <Route path="/login" element={<Navigate to="/profile" replace />} />
                    <Route path="/signup" element={<Navigate to="/profile" replace />} />
                    <Route path="/auth/verify" element={<Layout title="Sign In"><AuthVerify /></Layout>} />
                    <Route path="/library" element={<Layout title="Knowledge Base"><Library /></Layout>} />
                    <Route path="/facts/:id" element={<Layout title="Fact Detail"><FactDetail /></Layout>} />
                    <Route path="/wwmd" element={<Layout title="What Would Marcus Do?"><WWMD /></Layout>} />
                    <Route path="/chat" element={<Layout title="Ask Marcus"><Chat /></Layout>} />
                    <Route path="/toolkit" element={<Layout title="Toolkit"><Toolkit /></Layout>} />
                    <Route path="/toolkit/:id" element={<Layout title="Template Detail"><TemplateDetail /></Layout>} />
                    <Route path="/profile" element={<Layout title="Profile"><Profile /></Layout>} />
                    <Route path="/browse" element={<Navigate to="/home" replace />} />
                    <Route path="/workflow" element={<Navigate to="/home" replace />} />
                    <Route path="/log" element={<Navigate to="/home" replace />} />
                    <Route path="/devops" element={<Navigate to="/home" replace />} />
                    <Route path="/privacy" element={<Layout title="Privacy"><Privacy /></Layout>} />
                    <Route path="/terms" element={<Layout title="Terms of Use"><Terms /></Layout>} />
                </Routes>
            </Suspense>
        </BrowserRouter>
    );
}

export default App;
