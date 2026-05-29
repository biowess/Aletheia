import type { Config } from 'tailwindcss'

export default {
  content: [
    "./index.html",
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      // ── Aletheia Canonical Color Palette (BRANDING.md) ─────────────────────
      colors: {
        aletheia: {
          navy:  '#162C41',
          slate: '#4F606F',
          white: '#FFFFFF',
        },
        clinical: {
          // Backgrounds
          background:                   '#F5F8FB',
          surface:                      '#F5F8FB',
          'surface-dim':                '#EDF3F8',
          'surface-bright':             '#FFFFFF',
          'surface-container-lowest':   '#FFFFFF',
          'surface-container-low':      '#F9FBFD',
          'surface-container':          '#F2F6FA',
          'surface-container-high':     '#E6EDF4',
          'surface-container-highest':  '#D7E2EC',
          'surface-variant':            '#EDF3F8',
          'surface-tint':               '#C4D3E0',
          'surface-muted':              '#F2F6FA',

          // Text hierarchy
          'on-surface':                 '#162C41',   // text-primary
          'on-surface-variant':         '#4F606F',   // text-secondary
          'on-surface-muted':           '#7C8A97',   // text-muted
          'on-surface-faint':           '#A7B4C0',   // text-faint
          'inverse-surface':            '#162C41',
          'inverse-on-surface':         '#FFFFFF',

          // Primary — navy-anchored action layer
          primary:                      '#D7E2EC',   // border-default (light fill)
          'on-primary':                 '#162C41',
          'primary-container':          '#EDF3F8',   // bg-secondary
          'on-primary-container':       '#162C41',
          'inverse-primary':            '#244B73',   // state-info (action blue)
          'primary-fixed':              '#EDF3F8',
          'primary-fixed-dim':          '#D7E2EC',
          'on-primary-fixed':           '#162C41',
          'on-primary-fixed-variant':   '#4F606F',

          // Secondary — slate layer
          secondary:                    '#C4D3E0',   // border-strong
          'on-secondary':               '#162C41',
          'secondary-container':        '#F9FBFD',   // surface-secondary
          'on-secondary-container':     '#4F606F',   // text-secondary
          'secondary-fixed':            '#F9FBFD',
          'secondary-fixed-dim':        '#D7E2EC',
          'on-secondary-fixed':         '#162C41',
          'on-secondary-fixed-variant': '#4F606F',

          // Tertiary — subtle backgrounds
          tertiary:                     '#E7EEF5',   // border-subtle
          'on-tertiary':                '#162C41',
          'tertiary-container':         '#F5F8FB',   // bg-primary
          'on-tertiary-container':      '#4F606F',
          'tertiary-fixed':             '#F5F8FB',
          'tertiary-fixed-dim':         '#E7EEF5',
          'on-tertiary-fixed':          '#162C41',
          'on-tertiary-fixed-variant':  '#4F606F',

          // Borders
          outline:                      '#D7E2EC',   // border-default
          'outline-variant':            '#E7EEF5',   // border-subtle
          'outline-strong':             '#C4D3E0',   // border-strong

          // Semantic states
          'state-stable':               '#3E6B61',
          'state-evolving':             '#C58A2B',
          'state-declined':             '#9B4A4A',
          'state-info':                 '#244B73',

          // Error / danger
          error:                        '#9B4A4A',   // state-declined
          'on-error':                   '#FFFFFF',
          'error-container':            '#F5ECEC',
          'on-error-container':         '#7A3535',

          // Confidence scale
          'confidence-high':            '#244B73',
          'confidence-medium':          '#5D7892',
          'confidence-low':             '#A5B4C2',
          'confidence-minimal':         '#D5DEE7',

          // Legacy badge helpers (keep for backward compat)
          high:    '#244B73',
          medium:  '#5D7892',
          low:     '#A5B4C2',
        },
      },

      // ── Typography ────────────────────────────────────────────────────────
      fontFamily: {
        sans:   ['IBM Plex Sans', 'Source Sans 3', 'Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        ui:     ['IBM Plex Sans', 'Source Sans 3', 'Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        report: ['EB Garamond', 'Garamond', 'Times New Roman', 'Georgia', 'serif'],
        mono:   ['IBM Plex Mono', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      fontSize: {
        'xs':         ['12px', { lineHeight: '1.4' }],
        'sm':         ['13px', { lineHeight: '1.45' }],
        'md':         ['14px', { lineHeight: '1.5' }],
        'lg':         ['16px', { lineHeight: '1.5' }],
        'xl':         ['20px', { lineHeight: '1.35' }],
        '2xl':        ['24px', { lineHeight: '1.3' }],
        '3xl':        ['32px', { lineHeight: '1.2' }],
        '4xl':        ['40px', { lineHeight: '1.1' }],
        // Legacy aliases
        'label-sm':   ['12px', { lineHeight: '16px', letterSpacing: '0.04em' }],
        'body-md':    ['14px', { lineHeight: '20px' }],
        'body-lg':    ['16px', { lineHeight: '24px' }],
        'headline-md':['20px', { lineHeight: '28px' }],
        'headline-lg':['24px', { lineHeight: '32px' }],
      },
      lineHeight: {
        tight:    '1.15',
        snug:     '1.3',
        normal:   '1.5',
        relaxed:  '1.65',
      },

      // ── Border Radius — sharp, not iOS-like ───────────────────────────────
      borderRadius: {
        'none': '0px',
        'sm':   '2px',
        DEFAULT:'4px',
        'md':   '4px',
        'lg':   '4px',   // cap at 4px per BRANDING.md
        'xl':   '4px',
        'full': '9999px',
      },

      // ── Shadows ───────────────────────────────────────────────────────────
      boxShadow: {
        'soft':     '0 1px 2px rgba(22,44,65,0.04), 0 6px 24px rgba(22,44,65,0.06)',
        'elevated': '0 2px 6px rgba(22,44,65,0.05), 0 12px 40px rgba(22,44,65,0.08)',
        'card':     '0 1px 3px rgba(22,44,65,0.06), 0 4px 16px rgba(22,44,65,0.06)',
        'card-elevated': '0 2px 6px rgba(22,44,65,0.07), 0 10px 32px rgba(22,44,65,0.08)',
        'panel':    '0 1px 2px rgba(22,44,65,0.04), 0 8px 32px rgba(22,44,65,0.07)',
        'focus':    '0 0 0 3px rgba(36,75,115,0.20)',
        'focus-error': '0 0 0 3px rgba(155,74,74,0.20)',
      },

      // ── Spacing tokens ────────────────────────────────────────────────────
      spacing: {
        '1':  '4px',
        '2':  '8px',
        '3':  '12px',
        '4':  '16px',
        '5':  '24px',
        '6':  '32px',
        '7':  '48px',
        '8':  '64px',
        'container-padding': '24px',
        'card-gap':          '16px',
        'section-margin':    '40px',
        'glass-padding':     '16px',
      },

      // ── Motion ────────────────────────────────────────────────────────────
      transitionDuration: {
        fast:    '120ms',
        normal:  '180ms',
        soft:    '260ms',
        slow:    '360ms',
        ambient: '480ms',
        // Legacy aliases
        standard:  '180ms',
        cinematic: '360ms',
        drift:     '480ms',
      },
      transitionTimingFunction: {
        'standard': 'cubic-bezier(0.2, 0.8, 0.2, 1)',
        'soft':     'cubic-bezier(0.16, 1, 0.3, 1)',
        // Legacy
        'clinical': 'cubic-bezier(0.2, 0.8, 0.2, 1)',
        'spring':   'cubic-bezier(0.16, 1, 0.3, 1)',
      },

      // ── Keyframes ─────────────────────────────────────────────────────────
      keyframes: {
        'fade-up': {
          '0%':   { opacity: '0', transform: 'translateY(4px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'fade-in': {
          '0%':   { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'shimmer': {
          '0%':   { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        'dialog-content-show': {
          '0%': { opacity: '0', transform: 'translate(-50%, -48%) scale(0.96)' },
          '100%': { opacity: '1', transform: 'translate(-50%, -50%) scale(1)' },
        },
        'dialog-content-hide': {
          '0%': { opacity: '1', transform: 'translate(-50%, -50%) scale(1)' },
          '100%': { opacity: '0', transform: 'translate(-50%, -48%) scale(0.96)' },
        },
        'dialog-overlay-show': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'dialog-overlay-hide': {
          '0%': { opacity: '1' },
          '100%': { opacity: '0' },
        },
      },
      animation: {
        'fade-up':  'fade-up 260ms cubic-bezier(0.16, 1, 0.3, 1) both',
        'fade-in':  'fade-in 180ms cubic-bezier(0.2, 0.8, 0.2, 1) both',
        'shimmer':  'shimmer 1.8s ease-in-out infinite',
        'dialog-content-show': 'dialog-content-show 200ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'dialog-content-hide': 'dialog-content-hide 200ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'dialog-overlay-show': 'dialog-overlay-show 200ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'dialog-overlay-hide': 'dialog-overlay-hide 200ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
} satisfies Config
