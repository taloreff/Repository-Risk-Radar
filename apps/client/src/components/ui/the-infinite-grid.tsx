'use client';

import { useEffect } from 'react';
import {
  motion,
  useAnimationFrame,
  useMotionTemplate,
  useMotionValue
} from 'framer-motion';

import { InfiniteGridPattern } from '@/components/ui/infinite-grid-pattern';
import { cn } from '@/lib/utils';

type InfiniteGridProps = {
  className?: string;
};

export function InfiniteGridBackground({ className }: InfiniteGridProps) {
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const gridOffsetX = useMotionValue(0);
  const gridOffsetY = useMotionValue(0);

  useEffect(() => {
    const centerSpotlight = () => {
      mouseX.set(window.innerWidth * 0.5);
      mouseY.set(window.innerHeight * 0.32);
    };
    const trackPointer = (event: PointerEvent) => {
      mouseX.set(event.clientX);
      mouseY.set(event.clientY);
    };

    centerSpotlight();
    window.addEventListener('resize', centerSpotlight);
    window.addEventListener('pointermove', trackPointer);

    return () => {
      window.removeEventListener('resize', centerSpotlight);
      window.removeEventListener('pointermove', trackPointer);
    };
  }, [mouseX, mouseY]);

  useAnimationFrame(() => {
    gridOffsetX.set((gridOffsetX.get() + 0.18) % 40);
    gridOffsetY.set((gridOffsetY.get() + 0.18) % 40);
  });

  const maskImage = useMotionTemplate`radial-gradient(920px circle at ${mouseX}px ${mouseY}px, black 0%, black 42%, transparent 78%)`;

  return (
    <div
      className={cn('pointer-events-none fixed inset-0 z-0 overflow-hidden', className)}
      aria-hidden="true"
    >
      <div className="absolute -inset-24 opacity-[0.14] [mask-image:linear-gradient(to_bottom,black,transparent_94%)]">
        <InfiniteGridPattern offsetX={gridOffsetX} offsetY={gridOffsetY} />
      </div>
      <motion.div
        className="absolute -inset-24 opacity-45"
        style={{ maskImage, WebkitMaskImage: maskImage }}
      >
        <InfiniteGridPattern offsetX={gridOffsetX} offsetY={gridOffsetY} />
      </motion.div>
      <div className="absolute inset-x-0 top-0 h-80 bg-gradient-to-b from-primary/16 via-primary/7 to-transparent" />
      <div className="absolute inset-x-0 bottom-0 h-56 bg-gradient-to-t from-background/80 via-background/25 to-transparent" />
    </div>
  );
}
