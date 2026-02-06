import React from 'react';
import { WwmdResponse } from '../types/wwmd';
import { motion } from 'framer-motion';

interface Props {
    data: WwmdResponse;
}

export const WwmdCard: React.FC<Props> = ({ data }) => {
    return (
        <div className="max-w-5xl mx-auto p-6 sm:p-10 bg-slate-900/40 text-slate-100 rounded-3xl shadow-2xl border border-white/5 backdrop-blur-xl">
            {/* Header */}
            <div className="mb-8 border-b border-white/10 pb-6">
                <h2 className="text-sm font-mono text-emerald-400 mb-1 tracking-wider uppercase">
                    ARK Query: {data.mode}
                </h2>
                <h1 className="text-2xl font-bold font-serif italic text-white">
                    "{data.query}"
                </h1>
            </div>

            {/* Answer */}
            <div className="prose prose-invert prose-lg max-w-none mb-8 leading-relaxed text-slate-200">
                <div className="whitespace-pre-wrap">{data.answer}</div>
            </div>

            {/* Citations */}
            {data.citations && data.citations.length > 0 && (
                <div className="space-y-4">
                    <h3 className="text-sm font-bold uppercase tracking-widest text-slate-500 border-b border-slate-800 pb-2">
                        Verified Evidence ({data.citations.length})
                    </h3>
                    <div className="grid gap-3">
                        {data.citations.map((cite, idx) => (
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: idx * 0.1 }}
                                key={idx}
                                className="bg-slate-800/50 p-3 rounded-lg border-l-4 border-emerald-500 hover:bg-slate-800 transition-colors"
                            >
                                <div className="flex justify-between items-start mb-1">
                                    <span className="text-xs font-mono text-emerald-400 bg-emerald-900/30 px-2 py-0.5 rounded">
                                        {cite.loc}
                                    </span>
                                    <span className="text-xs text-slate-500" title={`Score: ${cite.score}`}>
                                        {cite.source_id.replace(/_/g, ' ')}
                                    </span>
                                </div>
                                <p className="text-sm text-slate-300 italic font-serif">
                                    "{cite.excerpt}"
                                </p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            )}

            {/* Footer Meta */}
            <div className="mt-8 pt-4 border-t border-slate-800 flex justify-between text-xs font-mono text-slate-600">
                <span>Latency: {data.meta.latency_ms}ms</span>
                <span>Scanned: {data.meta.citation_search_space} lines</span>
                <span>Timestamp: {new Date(data.meta.timestamp).toLocaleString()}</span>
            </div>
        </div>
    );
};
