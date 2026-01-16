/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
        './src/components/**/*.{js,ts,jsx,tsx,mdx}',
        './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
        extend: {
            colors: {
                // Background (Vault Navy)
                background: 'hsl(222.2 84% 4.9%)',
                foreground: 'hsl(210 40% 98%)',

                // Surface (Slate Glass)
                card: 'hsl(217.2 32.6% 17.5%)',
                'card-foreground': 'hsl(210 40% 98%)',

                // Primary (Net-Gain Green)
                primary: {
                    DEFAULT: '#10B981',
                    50: '#ECFDF5',
                    100: '#D1FAE5',
                    500: '#10B981',
                    600: '#059669',
                    700: '#047857',
                },

                // Danger (Leakage Red)
                destructive: {
                    DEFAULT: '#EF4444',
                    500: '#EF4444',
                    600: '#DC2626',
                },

                // Accent (Electric Blue)
                accent: {
                    DEFAULT: '#3B82F6',
                    500: '#3B82F6',
                    600: '#2563EB',
                },

                // Slate colors for surfaces
                slate: {
                    50: '#F8FAFC',
                    100: '#F1F5F9',
                    200: '#E2E8F0',
                    300: '#CBD5E1',
                    400: '#94A3B8',
                    500: '#64748B',
                    600: '#475569',
                    700: '#334155',
                    800: '#1E293B',
                    900: '#0F172A',
                    950: '#020617',
                },

                // Guardian Colors
                guardian: {
                    sentinel: '#3B82F6',   // Blue
                    architect: '#8B5CF6', // Purple
                    shield: '#F97316',    // Orange
                    warden: '#14B8A6',    // Teal
                },
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
                mono: ['JetBrains Mono', 'Menlo', 'monospace'],
            },
            animation: {
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'typewriter': 'typewriter 2s steps(40) forwards',
            },
            keyframes: {
                typewriter: {
                    'from': { width: '0' },
                    'to': { width: '100%' },
                },
            },
        },
    },
    plugins: [],
};
