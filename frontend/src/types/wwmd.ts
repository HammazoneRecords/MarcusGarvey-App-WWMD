export interface WwmdCitation {
    source_id: string;
    loc: string;
    excerpt: string;
    score: number;
    match_type: 'exact' | 'partial_ngram' | 'fuzzy_set';
}

export interface WwmdMeta {
    chunks_found: number;
    citation_search_space: number;
    timestamp: string;
    latency_ms: number;
}

export interface WwmdResponse {
    query: string;
    mode: string;
    answer: string;
    citations: WwmdCitation[];
    meta: WwmdMeta;
}
