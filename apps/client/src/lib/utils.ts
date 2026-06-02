import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatPercent(value?: number | null, digits = 1) {
  if (value === undefined || value === null) {
    return 'unknown';
  }
  return `${(value * 100).toFixed(digits)}%`;
}

export function formatNumber(value?: number | null, digits = 1) {
  if (value === undefined || value === null) {
    return 'unknown';
  }
  return value.toFixed(digits);
}
