'use client';

import { AnimatePresence, motion } from 'framer-motion';
import { Moon, Sun } from 'lucide-react';
import { useCallback, useRef } from 'react';
import { flushSync } from 'react-dom';

import {
  setDocumentTheme,
  triggerThemeTransition,
  type ThemeTransitionType,
  withThemeViewTransition
} from '@/components/ui/theme-toggle/theme-transition';
import { useThemeState } from '@/components/ui/theme-toggle/use-theme-state';
import { cn } from '@/lib/utils';

type AnimatedThemeToggleButtonProps = {
  type?: ThemeTransitionType;
  className?: string;
};

export function AnimatedThemeToggleButton({
  type = 'vertical',
  className
}: AnimatedThemeToggleButtonProps) {
  const buttonRef = useRef<HTMLButtonElement>(null);
  const [darkMode, setDarkMode] = useThemeState();

  const handleToggle = useCallback(async () => {
    if (!buttonRef.current) {
      return;
    }

    const nextDarkMode = !darkMode;

    const didStartViewTransition = await withThemeViewTransition(() => {
      flushSync(() => {
        setDarkMode(nextDarkMode);
        setDocumentTheme(nextDarkMode);
      });
    });

    if (didStartViewTransition) {
      triggerThemeTransition(type);
    }
  }, [darkMode, setDarkMode, type]);

  return (
    <button
      ref={buttonRef}
      type="button"
      onClick={handleToggle}
      aria-label="Toggle color theme"
      title="Toggle color theme"
      className={cn(
        'flex h-9 w-9 items-center justify-center rounded-full border bg-card text-foreground shadow-sm shadow-primary/10 transition-colors hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
        className
      )}
    >
      <AnimatePresence mode="wait" initial={false}>
        {darkMode ? (
          <motion.span
            key="sun"
            initial={{ opacity: 0, scale: 0.55, rotate: 25 }}
            animate={{ opacity: 1, scale: 1, rotate: 0 }}
            exit={{ opacity: 0, scale: 0.75 }}
            transition={{ duration: 0.28 }}
            className="text-warning"
          >
            <Sun className="h-4 w-4" aria-hidden="true" />
          </motion.span>
        ) : (
          <motion.span
            key="moon"
            initial={{ opacity: 0, scale: 0.55, rotate: -25 }}
            animate={{ opacity: 1, scale: 1, rotate: 0 }}
            exit={{ opacity: 0, scale: 0.75 }}
            transition={{ duration: 0.28 }}
            className="text-primary"
          >
            <Moon className="h-4 w-4" aria-hidden="true" />
          </motion.span>
        )}
      </AnimatePresence>
    </button>
  );
}
