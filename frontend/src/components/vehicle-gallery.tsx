"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import useEmblaCarousel from "embla-carousel-react";
import { ChevronLeft, ChevronRight, Images } from "lucide-react";

export function VehicleGallery({ photos, title }: { photos: string[]; title: string }) {
  const [reducedMotion, setReducedMotion] = useState(false);
  const [selected, setSelected] = useState(0);
  const [ref, api] = useEmblaCarousel({ loop: photos.length > 1, duration: reducedMotion ? 0 : 25 });
  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setReducedMotion(media.matches);
    update();
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);
  useEffect(() => {
    if (!api) return;
    const update = () => setSelected(api.selectedScrollSnap());
    update();
    api.on("select", update);
    api.on("reInit", update);
    return () => { api.off("select", update); api.off("reInit", update); };
  }, [api]);
  return <section aria-label="Vehicle photos" className="vehicle-gallery overflow-hidden bg-carbon">
    <div className="overflow-hidden" ref={ref}><div className="flex">{photos.map((photo, index) => <div className="relative aspect-[4/3] min-w-0 flex-[0_0_100%]" key={`${photo}-${index}`}><Image src={photo} alt={`${title}, view ${index + 1}`} fill priority={index === 0} sizes="(max-width:1024px) 100vw, 65vw" className="object-cover" /></div>)}</div></div>
    <div className="flex items-center justify-between gap-3 border-t border-white/10 px-4 py-3 text-white">
      <p aria-live="polite" className="flex items-center gap-2 text-xs"><Images aria-hidden="true" className="size-4 text-white/60" />{selected + 1} / {photos.length} photos</p>
      {photos.length > 1 && <div className="flex gap-1"><button type="button" aria-label="Previous image" onClick={(event) => api?.scrollPrev(reducedMotion || event.detail === 0)} className="inline-flex size-11 items-center justify-center border border-white/25 text-white hover:bg-white/10"><ChevronLeft className="size-5" /></button><button type="button" aria-label="Next image" onClick={(event) => api?.scrollNext(reducedMotion || event.detail === 0)} className="inline-flex size-11 items-center justify-center bg-signal text-obsidian"><ChevronRight className="size-5" /></button></div>}
    </div>
  </section>;
}
