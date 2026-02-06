import React from 'react';
import { WwmdResponse } from '../../types/wwmd';
import { motion } from 'framer-motion';

interface Props {
    data: WwmdResponse;
}

export const WwmdCardPanAfrican: React.FC<Props> = ({ data }) => {
    return (
        <div className="w-[95%] max-w-[1800px] mx-auto p-8 bg-black text-white rounded-none border-t-8 border-red-600 shadow-[0_20px_50px_rgba(220,38,38,0.1)] relative overflow-hidden">
            {/* Decorative Background Flags */}
            <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-red-900/10 via-black to-green-900/10 blur-3xl rounded-full pointer-events-none"></div>

            {/* Header */}
            <div className="mb-8 border-b-2 border-red-900/30 pb-4 flex justify-between items-end">
                <div>
                    <span className="text-xs font-black text-red-600 uppercase tracking-[0.3em] block mb-1">UNIA ARCHIVES</span>
                    <h2 className="text-xl font-bold text-white uppercase tracking-tighter">
                        W.W.M.D.
                    </h2>
                </div>
                <div className="text-right">
                    <span className="block text-[10px] text-green-600 font-mono tracking-widest">AUTHENTICATED</span>
                </div>
            </div>

            {/* Layout: Query left, Answer Right on desktop if needed, but standard stacked is better for reading */}

            <div className="mb-10">
                <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-red-500 via-white to-green-500 uppercase italic leading-tight">
                    "{data.query}"
                </h1>
            </div>

            {/* Answer - High Contrast */}
            <div className="prose prose-invert prose-lg max-w-none mb-10 text-gray-100 font-medium leading-relaxed border-l-4 border-green-700 pl-6">
                <div className="whitespace-pre-wrap">{data.answer}</div>
            </div>

            {/* Citations */}
            {data.citations && data.citations.length > 0 && (
                <div className="bg-zinc-900/50 p-6 border-b-4 border-green-700">
                    <h3 className="text-sm font-black uppercase text-green-600 mb-4 flex items-center gap-2">
                        Evidence Base
                        <span className="text-xs font-normal text-zinc-500 bg-black px-2 py-0.5 rounded-full border border-zinc-800">{data.citations.length}</span>
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                        {data.citations.map((cite, idx) => (
                            <motion.div
                                initial={{ x: -20, opacity: 0 }}
                                animate={{ x: 0, opacity: 1 }}
                                transition={{ delay: idx * 0.1 }}
                                key={idx}
                                className="border border-zinc-800 p-4 hover:border-red-900 transition-colors"
                            >
                                <p className="text-sm text-zinc-300 italic mb-2">
                                    "{cite.excerpt}"
                                </p>
                                <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-wide">
                                    <span className="text-red-500">{cite.source_id.replace(/_/g, ' ')}</span>
                                    <span className="text-zinc-600">|</span>
                                    <span className="text-green-600">{cite.loc}</span>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </div>
            )}

            {/* Footer */}
            <div className="mt-8 text-center">
                <span className="text-[10px] font-mono text-zinc-600 uppercase tracking-[0.5em]">One God • One Aim • One Destiny</span>
            </div>
        </div>
    );
};
