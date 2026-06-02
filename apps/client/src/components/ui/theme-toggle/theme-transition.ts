export type ThemeTransitionType = 'horizontal' | 'vertical';

type ViewTransitionDocument = Document & {
  startViewTransition?: (updateCallback: () => void) => { ready: Promise<void> };
};

export function setDocumentTheme(darkMode: boolean) {
  document.documentElement.classList.toggle('dark', darkMode);
  localStorage.setItem('theme', darkMode ? 'dark' : 'light');
}

export async function withThemeViewTransition(updateTheme: () => void) {
  const startViewTransition = (document as ViewTransitionDocument).startViewTransition;

  if (!startViewTransition) {
    updateTheme();
    return false;
  }

  await startViewTransition.call(document, updateTheme).ready;
  return true;
}

export function triggerThemeTransition(type: ThemeTransitionType) {
  const clipPath =
    type === 'vertical'
      ? ['inset(0 50% 0 50%)', 'inset(0 0 0 0)']
      : ['inset(50% 0 50% 0)', 'inset(0 0 0 0)'];

  document.documentElement.animate(
    { clipPath },
    {
      duration: 700,
      easing: 'ease-in-out',
      pseudoElement: '::view-transition-new(root)'
    } as KeyframeAnimationOptions
  );
}
