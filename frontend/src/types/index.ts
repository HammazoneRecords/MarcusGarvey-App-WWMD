export type SourceType = "book" | "archive" | "speech" | "article";

export interface SourceRef {
    id: string;
    title: string;
    author: string;
    year: number;
    url?: string;
    page?: string;
    excerpt?: string;
    type: SourceType;
    /** Backend anchor_id for section fetch (same as id when from RAG). */
    anchorId?: string;
    /** Section locator e.g. "pdf:page:0010" — matches backend anchor_locator. */
    locator?: string;
}

/** API response for GET /api/source/<anchor_id>. */
export interface SourceSectionResponse {
    anchorId: string;
    title: string;
    locator?: string;
    sectionContent: string;
    pageLabel?: string;
    canonicalPath?: string;
}

export type ConfidenceLevel = "high" | "medium" | "disputed";

export interface Fact {
    id: string;
    claim: string;
    context: string;
    impactTrail: string[];
    categories: string[];
    readingTimeSec: number;
    confidence: ConfidenceLevel;
    receipts: SourceRef[];
}

export interface DailyItem {
    id: string;
    quote: string;
    context: string;
    reflectionQuestion: string;
    source: SourceRef;
}

export interface WWMDRequest {
    situation: string;
    mode?: "Personal" | "Community"; // optional; backend defaults to Personal
    tone: "Practical" | "Strict" | "Gentle";
}

export interface WWMDResponse {
    id?: string; // stable id for linking saved action steps
    query?: string; // Optional because legacy responses might not have it
    principle: string;
    historicalAnalogy: string;
    receipts: SourceRef[];
    actionSteps: { id: string; text: string; completed: boolean }[];
    mirrorQuestions: string[];
}

export interface ToolkitTemplate {
    id: string;
    title: string;
    description: string;
    markdown: string;
    tags: string[];
}

export interface GalleryItem {
    id: string;
    url: string;
    caption: string;
    year?: number;
}
