import { useState, useEffect } from 'react';
import { GalleryItem } from '../../types';
import { Card } from '../ui/index';
import { X } from 'lucide-react';

export const Gallery = ({ items }: { items: GalleryItem[] }) => {
    const [selectedImage, setSelectedImage] = useState<GalleryItem | null>(null);

    useEffect(() => {
        if (selectedImage) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'unset';
        }
        return () => {
            document.body.style.overflow = 'unset';
        };
    }, [selectedImage]);

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <h2 className="text-sm font-bold uppercase tracking-widest text-zinc-500">Archival Gallery</h2>
            </div>

            <div className="flex overflow-x-auto gap-4 pb-4 -mx-4 px-4 snap-x">
                {items.map((item) => (
                    <Card
                        key={item.id}
                        className="min-w-[280px] p-0 overflow-hidden snap-center group cursor-zoom-in active:scale-95 transition-transform"
                        onClick={() => setSelectedImage(item)}
                    >
                        <div className="relative aspect-[4/3] overflow-hidden">
                            <img
                                src={item.url}
                                alt={item.caption}
                                className="w-full h-full object-cover object-top transition-transform duration-500 group-hover:scale-110"
                            />
                            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent flex flex-col justify-end p-4">
                                <p className="text-white text-xs font-medium leading-relaxed">
                                    {item.caption}
                                </p>
                                {item.year && (
                                    <span className="text-[10px] text-zinc-400 font-bold uppercase mt-1">
                                        Circa {item.year}
                                    </span>
                                )}
                            </div>
                        </div>
                    </Card>
                ))}
            </div>

            {/* Lightbox Overlay */}
            {selectedImage && (
                <div
                    className="fixed inset-0 z-[100] bg-black/95 backdrop-blur-sm animate-in fade-in duration-300 flex flex-col items-center justify-center p-6"
                    onClick={() => setSelectedImage(null)}
                >
                    <button
                        className="absolute top-6 right-6 p-2 bg-white/10 hover:bg-white/20 rounded-full text-white transition-colors"
                        onClick={(e) => {
                            e.stopPropagation();
                            setSelectedImage(null);
                        }}
                    >
                        <X className="w-6 h-6" />
                    </button>

                    <div className="w-full max-w-4xl relative animate-in zoom-in-95 duration-300 flex flex-col items-center">
                        <img
                            src={selectedImage.url}
                            alt={selectedImage.caption}
                            className="w-full h-auto max-h-[70vh] object-contain object-top rounded-lg shadow-2xl mx-auto"
                            onClick={(e) => e.stopPropagation()}
                        />
                        <div className="mt-6 text-center space-y-2">
                            <p className="text-white text-lg font-medium leading-relaxed max-w-2xl mx-auto">
                                {selectedImage.caption}
                            </p>
                            {selectedImage.year && (
                                <span className="inline-block px-3 py-1 bg-primary/20 text-secondary border border-secondary/20 rounded-full text-xs font-bold uppercase tracking-widest">
                                    Historical Record: {selectedImage.year}
                                </span>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
