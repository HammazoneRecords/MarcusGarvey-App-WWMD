import { SourceRef, Fact, DailyItem, ToolkitTemplate } from '../types';
import db from './db.json';

export const MOCK_SOURCES = db.sources as SourceRef[];

export const MOCK_FACTS = db.facts.map(fact => ({
    ...fact,
    receipts: fact.receiptIds.map(id => MOCK_SOURCES.find(s => s.id === id)!)
})) as Fact[];

export const MOCK_DAILY = db.daily.map(item => ({
    ...item,
    source: MOCK_SOURCES.find(s => s.id === item.sourceId)!
})) as DailyItem[];

export const MOCK_TEMPLATES = db.templates as ToolkitTemplate[];

export const MOCK_GALLERY: any[] = [
    {
        id: "gal-1",
        url: "/assets/gallery/marcus-1.jpg",
        caption: "Marcus Mosiah Garvey in formal uniform.",
        year: 1922
    },
    {
        id: "gal-2",
        url: "/assets/gallery/marcus-garvey-1887-1940-loc-flickr-the-library-of-congress-5fcd97.jpg",
        caption: "Marcus Garvey (1887–1940). Library of Congress.",
        year: 1940
    },
    {
        id: "gal-3",
        url: "/assets/gallery/marcus-garvey-1922-91d215.jpg",
        caption: "Marcus Garvey, 1922.",
        year: 1922
    },
    {
        id: "gal-4",
        url: "/assets/gallery/marcus-garvey-president-general-of-the-african-republic-news-photo-1737995391.avif",
        caption: "Marcus Garvey, President-General of the African Republic.",
        year: 1922
    },
    {
        id: "gal-5",
        url: "/assets/gallery/service-pnp-ds-17200-17264v.jpg",
        caption: "Marcus Garvey. Library of Congress, Prints & Photographs.",
        year: 1924
    }
];
