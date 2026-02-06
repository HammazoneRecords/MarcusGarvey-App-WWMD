import React from 'react';
import { WwmdResponse } from '../../types/wwmd';
import { motion } from 'framer-motion';

interface Props {
    data: WwmdResponse;
}

export const WwmdCardPaper: React.FC<Props> = ({ data }) => {
    return (
        <div className="max-w-6xl mx-auto bg-[#FDFBF7] text-slate-900 p-8 sm:p-16 shadow-sm border border-slate-200">
            {/* Header - Academic Style */}
            <div className="text-center mb-12 border-b-2 border-slate-900 pb-8">
                <h2 className="text-xs font-bold uppercase tracking-[0.2em] mb-4 text-slate-500">
                    Garvey Institute of Analysis
                </h2>
                <h1 className="text-4xl font-serif font-bold text-slate-900 mb-2 leading-tight">
                    {data.query}
                </h1>
                <p className="text-sm font-serif italic text-slate-500">
                    Generated Report • {new Date(data.meta.timestamp).toLocaleDateString()}
                </p>
            </div>

            {/* Answer - Serif Typography */}
            <div className="prose prose-slate prose-lg max-w-none mb-16 font-serif leading-loose text-justify">
                <div className="whitespace-pre-wrap">{data.answer}</div>
            </div>

            {/* Citations - Footnotes Style */}
            {data.citations && data.citations.length > 0 && (
                <div className="pt-8 border-t border-slate-300">
                    <h3 className="text-sm font-bold uppercase text-slate-900 mb-6">
                        References & Excerpts
                    </h3>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {data.citations.map((cite, idx) => (
                            <div key={idx} className="bg-white p-6 border border-slate-100 shadow-[0_2px_10px_rgba(0,0,0,0.03)]">
                                <p className="text-sm text-slate-600 italic font-serif mb-3 leading-relaxed">
                                    "{cite.excerpt}"
                                </p>
                                <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                                    <span className="w-4 h-[1px] bg-slate-400"></span>
                                    {cite.source_id.replace(/_/g, ' ')} • {cite.loc}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Footer */}
            <div className="mt-16 text-center text-[10px] text-slate-400 uppercase tracking-widest font-sans">
                Lat: {data.meta.latency_ms}ms • Scanned {data.meta.citation_search_space} lines
            </div>
        </div>
    );
};
