import type { Metadata } from 'next';
import { Actor, Bevan, Courier_Prime } from 'next/font/google';
import type { ReactNode } from 'react';

import './globals.css';

const fontSans = Actor({
  subsets: ['latin'],
  weight: '400',
  variable: '--font-sans'
});

const fontSerif = Bevan({
  subsets: ['latin'],
  weight: '400',
  variable: '--font-serif'
});

const fontMono = Courier_Prime({
  subsets: ['latin'],
  weight: ['400', '700'],
  variable: '--font-mono'
});

const themeInitScript = `
try {
  var storedTheme = localStorage.getItem('theme');
  if (storedTheme === 'light') {
    document.documentElement.classList.remove('dark');
  } else {
    document.documentElement.classList.add('dark');
  }
} catch (_) {}
`;

export const metadata: Metadata = {
  title: 'Repo Risk Radar',
  description: 'Dependency security risk radar for public GitHub repositories.'
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={`${fontSans.variable} ${fontSerif.variable} ${fontMono.variable} antialiased`}>
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
        {children}
      </body>
    </html>
  );
}
