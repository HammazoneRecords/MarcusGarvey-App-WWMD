import React from 'react';
import { WwmdResponse } from '../../types/wwmd';
import { motion } from 'framer-motion';

interface Props {
    data: WwmdResponse;
}

export const WwmdCardNoir: React.FC<Props> = ({ data }) => {
    return (
        <div className="max-w-7xl mx-auto p-6 sm:p-10 bg-slate-950 text-slate-200 rounded-3xl shadow-2xl border border-slate-800 shadow-slate-900/50">
            {/* Minimal Header */}
            <div className="mb-10 flex items-center justify-between border-b border-slate-800 pb-6">
                <div className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]"></div>
                    <h2 className="text-xs font-mono text-slate-500 uppercase tracking-[0.2em]">
                        ARK INTELLIGENCE
                    </h2>
                </div>
                <span className="text-xs font-mono text-slate-600">{data.mode}</span>
            </div>

            {/* Query */}
            <div className="mb-12 text-center">
                <h1 className="text-3xl md:text-4xl font-light text-white tracking-tight leading-tight">
                    "{data.query}"
                </h1>
            </div>

            {/* Answer */}
            <div className="prose prose-invert prose-lg max-w-none mb-12 leading-loose text-slate-300 font-light">
                <div className="whitespace-pre-wrap">{data.answer}</div>
            </div>

            {/* Citations - Grid Layout */}
            {data.citations && data.citations.length > 0 && (
                <div className="border-t border-slate-800 pt-8">
                    <h3 className="text-xs font-bold uppercase tracking-widest text-slate-600 mb-6">
                        Verified Sources
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                        {data.citations.map((cite, idx) => (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                transition={{ delay: idx * 0.05 }}
                                key={idx}
                                className="group bg-slate-900/50 p-5 rounded-xl border border-slate-800 hover:border-slate-700 transition-all hover:shadow-lg"
                            >
                                <div className="flex justify-between items-start mb-3">
                                    <span className="text-[10px] font-mono text-emerald-500 bg-emerald-950/30 px-2 py-1 rounded border border-emerald-900/50 group-hover:bg-emerald-900/50 transition-colors">
                                        {cite.loc}
                                    </span>
                                    <span className="text-[10px] text-slate-600 uppercase tracking-wider">
                                        {cite.source_id.replace(/_/g, ' ')}
                                    </span>
                                </div>
                                <p className="text-sm text-slate-400 italic">
                                    "{cite.excerpt}"
                                </p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            )}

            {/* Footer */}
            <div className="mt-10 pt-6 border-t border-slate-900 flex justify-between text-[10px] font-mono text-slate-700 uppercase tracking-wider">
                <span>Latency: {data.meta.latency_ms}ms</span>
                <span>{new Date(data.meta.timestamp).toLocaleDateString()}</span>
            </div>
        </div>
    );
};
