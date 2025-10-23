/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./components/**/*.{js,ts,jsx,tsx}",
    "./pages/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Brand Colors
        primary: 'var(--color-brand-primary)',
        'primary-soft': 'var(--color-brand-primarySoftBg)',
        'primary-text': 'var(--color-brand-primaryStrongText)',
        
        // Background Colors
        'bg-app': 'var(--color-bg-app)',
        'bg-surface': 'var(--color-bg-surface)',
        'bg-sidebar': 'var(--color-bg-sidebar)',
        'bg-card': 'var(--color-bg-card)',
        'bg-input': 'var(--color-bg-input)',
        
        // Text Colors
        'text-title': 'var(--color-text-title)',
        'text-body': 'var(--color-text-body)',
        'text-muted': 'var(--color-text-muted)',
        
        // Border Colors
        'border-subtle': 'var(--color-border-subtle)',
        'border-strong': 'var(--color-border-strong)',
        
        // State Colors
        'success-bg': 'var(--color-state-successBg)',
        'success-fg': 'var(--color-state-successFg)',
        'danger-bg': 'var(--color-state-dangerBg)',
        'danger-fg': 'var(--color-state-dangerFg)',
        'warning-bg': 'var(--color-state-warningBg)',
        'warning-fg': 'var(--color-state-warningFg)',
        
        // Chart Colors
        'chart-primary': 'var(--color-chart-linePrimary)',
        'chart-secondary': 'var(--color-chart-lineSecondary)',
        'chart-pie1': 'var(--color-chart-pie1)',
        'chart-pie2': 'var(--color-chart-pie2)',
        'chart-pie3': 'var(--color-chart-pie3)',
        'chart-pie4': 'var(--color-chart-pie4)',
        'chart-pie5': 'var(--color-chart-pie5)',
        'chart-pie6': 'var(--color-chart-pie6)',
      },
      spacing: {
        '1': 'var(--primitive-spacing-1)',
        '2': 'var(--primitive-spacing-2)',
        '3': 'var(--primitive-spacing-3)',
        '4': 'var(--primitive-spacing-4)',
        '5': 'var(--primitive-spacing-5)',
        '6': 'var(--primitive-spacing-6)',
        '8': 'var(--primitive-spacing-8)',
        '10': 'var(--primitive-spacing-10)',
        '12': 'var(--primitive-spacing-12)',
        '16': 'var(--primitive-spacing-16)',
        '20': 'var(--primitive-spacing-20)',
        '24': 'var(--primitive-spacing-24)',
      },
      borderRadius: {
        'xs': 'var(--primitive-radius-xs)',
        'sm': 'var(--primitive-radius-sm)',
        'md': 'var(--primitive-radius-md)',
        'lg': 'var(--primitive-radius-lg)',
        'xl': 'var(--primitive-radius-xl)',
        '2xl': 'var(--primitive-radius-2xl)',
        'full': 'var(--primitive-radius-full)',
      },
      fontFamily: {
        'sans': ['var(--primitive-font-family-base)', 'system-ui', 'sans-serif'],
        'mono': ['var(--primitive-font-family-mono)', 'monospace'],
      },
      fontSize: {
        'xs': 'var(--primitive-font-size-xs)',
        'sm': 'var(--primitive-font-size-sm)',
        'md': 'var(--primitive-font-size-md)',
        'lg': 'var(--primitive-font-size-lg)',
        'xl': 'var(--primitive-font-size-xl)',
        '2xl': 'var(--primitive-font-size-2xl)',
      },
      fontWeight: {
        'regular': 'var(--primitive-font-weight-regular)',
        'medium': 'var(--primitive-font-weight-medium)',
        'semibold': 'var(--primitive-font-weight-semibold)',
        'bold': 'var(--primitive-font-weight-bold)',
      },
      lineHeight: {
        'tight': 'var(--primitive-font-lineHeight-tight)',
        'normal': 'var(--primitive-font-lineHeight-normal)',
        'relaxed': 'var(--primitive-font-lineHeight-relaxed)',
      },
      boxShadow: {
        'sm': 'var(--primitive-elevation-sm)',
        'card': 'var(--primitive-elevation-card)',
        'md': 'var(--primitive-elevation-md)',
        'popover': 'var(--primitive-elevation-popover)',
        'lg': 'var(--primitive-elevation-lg)',
        'modal': 'var(--primitive-elevation-modal)',
      },
      animation: {
        "fade-in": "fadeIn 0.5s ease-in-out",
        "expand-height": "expandHeight 1s ease-in-out",
        "fast": "var(--primitive-animation-duration-fast)",
        "normal": "var(--primitive-animation-duration-normal)",
        "slow": "var(--primitive-animation-duration-slow)",
      },
      transitionTimingFunction: {
        'ease': 'var(--primitive-animation-easing-ease)',
        'ease-in': 'var(--primitive-animation-easing-ease-in)',
        'ease-out': 'var(--primitive-animation-easing-ease-out)',
        'ease-in-out': 'var(--primitive-animation-easing-ease-in-out)',
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0", display: "none" },
          "1%": { opacity: "0", display: "block" },
          "100%": { opacity: "1", display: "block" },
        },
        expandHeight: {
          "0%": { height: "0", overflow: "hidden" },
          "100%": { height: "auto", overflow: "hidden" },
        },
      },
    },
  },
  variants: {},
  plugins: [],
};
