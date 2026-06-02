'use client';

import { useEffect, useState } from 'react';

export function useThemeState() {
  const [darkMode, setDarkMode] = useState(() =>
    typeof window === 'undefined'
      ? true
      : document.documentElement.classList.contains('dark')
  );

  useEffect(() => {
    const syncTheme = () => setDarkMode(document.documentElement.classList.contains('dark'));
    const observer = new MutationObserver(syncTheme);

    syncTheme();
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });

    return () => observer.disconnect();
  }, []);

  return [darkMode, setDarkMode] as const;
}
