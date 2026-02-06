import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { Home, Library, WWMD, Toolkit, Profile, FactDetail, TemplateDetail } from './pages';
import { useStore } from './store/useStore';
import { useEffect } from 'react';

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
            <Routes>
                <Route path="/" element={<Layout title="Garvey Compass"><Home /></Layout>} />
                <Route path="/library" element={<Layout title="Library"><Library /></Layout>} />
                <Route path="/facts/:id" element={<Layout title="Fact Detail"><FactDetail /></Layout>} />
                <Route path="/wwmd" element={<Layout title="Garvey Lens"><WWMD /></Layout>} />
                <Route path="/toolkit" element={<Layout title="Toolkit"><Toolkit /></Layout>} />
                <Route path="/toolkit/:id" element={<Layout title="Template Detail"><TemplateDetail /></Layout>} />
                <Route path="/profile" element={<Layout title="Profile"><Profile /></Layout>} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
