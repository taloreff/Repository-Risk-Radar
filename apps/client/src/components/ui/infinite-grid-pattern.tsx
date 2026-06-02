'use client';

import { motion, type MotionValue } from 'framer-motion';

export function InfiniteGridPattern({
  offsetX,
  offsetY
}: {
  offsetX: MotionValue<number>;
  offsetY: MotionValue<number>;
}) {
  return (
    <svg className="h-full w-full text-primary/80">
      <defs>
        <motion.pattern
          id="repo-risk-radar-grid"
          width="40"
          height="40"
          patternUnits="userSpaceOnUse"
          x={offsetX}
          y={offsetY}
        >
          <path d="M 40 0 L 0 0 0 40" fill="none" stroke="currentColor" strokeWidth="1" />
        </motion.pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#repo-risk-radar-grid)" />
    </svg>
  );
}
