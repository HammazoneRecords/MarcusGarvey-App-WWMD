import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ChevronLeft, Copy, Download, Edit3, Save, X, Check } from 'lucide-react';
import { getToolkitTemplateById } from '../services/api';
import { ToolkitTemplate } from '../types';
import { Button, Skeleton, Card } from '../components/ui/index';
import { MarkdownRenderer } from '../components/toolkit/MarkdownRenderer';
import { useStore } from '../store/useStore';
import { useAuth } from '../hooks/useAuth';
import { upsertToolkitEdit } from '../services/supabaseUserData';

export const TemplateDetail = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [template, setTemplate] = useState<ToolkitTemplate | null>(null);
    const [loading, setLoading] = useState(true);
    const [isEditing, setIsEditing] = useState(false);
    const [editContent, setEditContent] = useState('');
    const [copied, setCopied] = useState(false);

    const { user } = useAuth();
    const { toolkitEdits, saveToolkitEdit } = useStore();
    const persistedContent = id ? toolkitEdits[id] : null;

    useEffect(() => {
        const fetchTemplate = async () => {
            if (!id) return;
            setLoading(true);
            try {
                const data = await getToolkitTemplateById(id);
                if (data) {
                    setTemplate(data);
                    setEditContent(persistedContent || data.markdown);
                }
            } catch (error) {
                console.error("Failed to fetch template", error);
            } finally {
                setLoading(false);
            }
        };
        fetchTemplate();
    }, [id, persistedContent]);

    const handleCopy = () => {
        navigator.clipboard.writeText(editContent);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const handleSave = () => {
        if (id) {
            saveToolkitEdit(id, editContent);
            if (user?.id) upsertToolkitEdit(user.id, id, editContent);
            setIsEditing(false);
        }
    };

    if (loading) return <div className="space-y-6"><Skeleton className="h-10 w-32" /><Skeleton className="h-96 w-full" /></div>;
    if (!template) return <div className="text-center py-20">Template not found</div>;

    return (
        <div className="space-y-6 pb-10 animate-in fade-in slide-in-from-right-4 duration-500">
            {/* Header Actions */}
            <div className="flex items-center justify-between -mx-1">
                <button onClick={() => navigate(-1)} className="p-2 -ml-2 rounded-full hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors">
                    <ChevronLeft className="w-6 h-6" />
                </button>
                <div className="flex gap-1">
                    <button
                        onClick={handleCopy}
                        className="p-2 rounded-full hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors relative"
                        title="Copy to clipboard"
                    >
                        {copied ? <Check className="w-6 h-6 text-primary" /> : <Copy className="w-6 h-6" />}
                    </button>
                    <button className="p-2 rounded-full hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors">
                        <Download className="w-6 h-6" />
                    </button>
                </div>
            </div>

            <section className="space-y-2">
                <h1 className="text-2xl font-display font-bold">{template.title}</h1>
                <p className="text-sm text-zinc-500 dark:text-zinc-400">{template.description}</p>
            </section>

            <Card className="min-h-[400px] flex flex-col p-0 overflow-visible">
                {/* Editor Toolbar */}
                <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-800/50 rounded-t-2xl">
                    <span className="text-xs font-bold uppercase tracking-widest text-zinc-400">
                        {isEditing ? 'Editing Mode' : (persistedContent ? 'Customized' : 'Original Template')}
                    </span>
                    {isEditing ? (
                        <div className="flex gap-2">
                            <button onClick={() => setIsEditing(false)} className="p-1.5 text-zinc-400 hover:text-accent">
                                <X className="w-5 h-5" />
                            </button>
                            <button onClick={handleSave} className="p-1.5 text-primary dark:text-secondary">
                                <Save className="w-5 h-5" />
                            </button>
                        </div>
                    ) : (
                        <button onClick={() => setIsEditing(true)} className="flex items-center gap-1.5 text-xs font-bold text-primary dark:text-secondary uppercase tracking-widest">
                            <Edit3 className="w-4 h-4" />
                            Customize
                        </button>
                    )}
                </div>

                <div className="p-6 flex-1">
                    {isEditing ? (
                        <textarea
                            value={editContent}
                            onChange={(e) => setEditContent(e.target.value)}
                            className="w-full h-[350px] bg-transparent outline-none resize-none font-mono text-sm leading-relaxed"
                            spellCheck={false}
                        />
                    ) : (
                        <MarkdownRenderer content={editContent} />
                    )}
                </div>
            </Card>

            {!isEditing && (
                <div className="bg-zinc-100 dark:bg-zinc-800/50 border border-dashed border-zinc-300 dark:border-zinc-700 p-6 rounded-2xl">
                    <h4 className="text-xs font-bold uppercase tracking-widest text-zinc-500 mb-2">Usage Note</h4>
                    <p className="text-sm text-zinc-500 leading-relaxed">
                        Feel free to customize this template for your specific branch or organization. All changes are saved locally to your device. Be sure to copy or download your version before clearing your browser storage.
                    </p>
                </div>
            )}
        </div>
    );
};
