import { useState } from 'react';

interface Props {
    onConfirm: (name: string) => void;
}

export function NameCaptureModal({ onConfirm }: Props) {
    const [name, setName] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        const trimmed = name.trim();
        if (!trimmed) return;
        onConfirm(trimmed);
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
            <div className="bg-zinc-900 border border-zinc-700 rounded-2xl p-8 max-w-sm w-full mx-4 shadow-2xl">
                <div className="text-center mb-6">
                    <div className="text-4xl mb-3">✊🏾</div>
                    <h2 className="text-xl font-bold text-white mb-2">
                        Hail, freedom fighter.
                    </h2>
                    <p className="text-zinc-400 text-sm leading-relaxed">
                        Before di ark speaks — what shall Marcus call you?
                    </p>
                </div>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <input
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="Your name"
                        autoFocus
                        className="w-full bg-zinc-800 border border-zinc-600 rounded-lg px-4 py-3 text-white placeholder-zinc-500 focus:outline-none focus:border-yellow-500 transition-colors"
                        maxLength={40}
                    />
                    <button
                        type="submit"
                        disabled={!name.trim()}
                        className="w-full bg-yellow-500 hover:bg-yellow-400 disabled:opacity-40 disabled:cursor-not-allowed text-black font-bold py-3 rounded-lg transition-colors"
                    >
                        Enter the ARK
                    </button>
                    <button
                        type="button"
                        onClick={() => onConfirm('friend')}
                        className="w-full text-zinc-500 hover:text-zinc-300 text-sm py-1 transition-colors"
                    >
                        Skip for now
                    </button>
                </form>
            </div>
        </div>
    );
}
