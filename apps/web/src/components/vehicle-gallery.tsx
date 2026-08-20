"use client";

import Image from "next/image";
import useEmblaCarousel from "embla-carousel-react";
import { ChevronLeft, ChevronRight } from "lucide-react";

export function VehicleGallery({ photos, title }: { photos: string[]; title: string }) {
  const [ref, api] = useEmblaCarousel({ loop: photos.length > 1 });
  return <div className="relative overflow-hidden bg-carbon" ref={ref}><div className="flex">{photos.map((photo, index) => <div className="relative aspect-[4/3] min-w-0 flex-[0_0_100%]" key={`${photo}-${index}`}><Image src={photo} alt={`${title}, view ${index + 1}`} fill priority={index === 0} sizes="(max-width:1024px) 100vw, 65vw" className="object-cover" /></div>)}</div>{photos.length > 1 && <div className="absolute bottom-4 right-4 flex gap-1"><button type="button" aria-label="Previous image" onClick={() => api?.scrollPrev()} className="inline-flex size-10 items-center justify-center bg-white text-obsidian"><ChevronLeft className="size-5" /></button><button type="button" aria-label="Next image" onClick={() => api?.scrollNext()} className="inline-flex size-10 items-center justify-center bg-white text-obsidian"><ChevronRight className="size-5" /></button></div>}</div>;
}
