/**
 * Portora Design System
 * 
 * This file defines the color palette and design tokens used across the entire application.
 * All components should use these values for consistency.
 */

export const colors = {
  // Brand Colors (Sky Blue)
  brand: {
    50: '#f0f9ff',   // Lightest sky - backgrounds, hover states
    100: '#e0f2fe',  // Very light sky - subtle backgrounds
    200: '#bae6fd',  // Light sky - borders, dividers
    300: '#7dd3fc',  // Medium light sky
    400: '#38bdf8',  // Medium sky
    500: '#0ea5e9',  // Base sky - primary actions
    600: '#0284c7',  // Dark sky - CTA buttons
    700: '#0369a1',  // Darker sky - hover states
    800: '#075985',  // Very dark sky
    900: '#0c4a6e',  // Darkest sky
  },
  
  // Neutral Colors (Grays)
  neutral: {
    50: '#fafafa',   // Pure white-alternative
    100: '#f5f5f5',  // Very light gray
    200: '#e5e5e5',  // Light gray - borders
    300: '#d4d4d4',  // Medium light gray
    400: '#a3a3a3',  // Medium gray
    500: '#737373',  // Base gray
    600: '#525252',  // Dark gray - secondary text
    700: '#404040',  // Darker gray
    800: '#262626',  // Very dark gray
    900: '#171717',  // Almost black - primary text
  },
  
  // Semantic Colors
  success: '#22C55E',  // Gains, positive actions
  danger: '#DC2626',   // Losses, errors
  warning: '#F59E0B',  // Warnings
  info: '#0ea5e9',     // Informational
} as const

export const gradients = {
  brand: 'linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)',
  soft: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
  hero: 'linear-gradient(135deg, #ffffff 0%, #f1f5f9 50%, #e2e8f0 100%)',
  textBrand: 'linear-gradient(135deg, #0284c7 0%, #0ea5e9 50%, #38bdf8 100%)',
} as const

export const shadows = {
  soft: '0 2px 8px 0 rgba(0, 0, 0, 0.04)',
  medium: '0 4px 16px 0 rgba(0, 0, 0, 0.08)',
  strong: '0 8px 32px 0 rgba(0, 0, 0, 0.12)',
  brand: '0 4px 16px 0 rgba(2, 132, 199, 0.15)',
} as const

export const transitions = {
  default: 'transition-all duration-200',
  smooth: 'transition-all duration-300',
  fast: 'transition-all duration-150',
} as const

/**
 * Usage Guidelines:
 * 
 * Primary Actions (CTAs): bg-brand-600 or bg-gradient-brand
 * Secondary Actions: border-neutral-300, text-neutral-700
 * Text Primary: text-neutral-900
 * Text Secondary: text-neutral-600
 * Borders: border-neutral-200
 * Cards: bg-white, border-neutral-200, shadow-soft
 * Hover States: hover:bg-brand-50, hover:text-brand-600
 * Gradients: Use bg-gradient-brand for primary elements
 * Shadows: Use shadow-soft for cards, shadow-brand for brand elements
 */
