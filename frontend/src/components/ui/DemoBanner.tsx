'use client';

import { useRouter } from 'next/navigation';

interface DemoBannerProps {
    variant?: 'inline' | 'header' | 'full';
    showExitButton?: boolean;
}

/**
 * Demo mode banner component
 * Shows DEMO indicator and exit button to return to homepage
 */
export default function DemoBanner({
    variant = 'inline',
    showExitButton = true,
}: DemoBannerProps) {
    const router = useRouter();

    const exitDemo = () => {
        // Clear demo mode
        localStorage.removeItem('demoMode');
        localStorage.removeItem('activeGuardians');
        localStorage.removeItem('extractedData');
        localStorage.removeItem('transactionClassifications');
        router.push('/');
    };

    if (variant === 'full') {
        // Full-width banner - edge to edge
        return (
            <div className="w-full bg-blue-500/20 border-y border-blue-500/30 px-6 py-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <span className="text-2xl">📊</span>
                    <div>
                        <p className="font-bold text-blue-400">DEMO MODE</p>
                        <p className="text-sm text-slate-400">
                            Viewing sample results for Rohan Sharma. This is not your real data.
                        </p>
                    </div>
                </div>
                {showExitButton && (
                    <button
                        onClick={exitDemo}
                        className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm transition-colors"
                    >
                        ✕ Exit Demo
                    </button>
                )}
            </div>
        );
    }

    if (variant === 'header') {
        // Compact version for page headers
        return (
            <div className="flex items-center gap-3">
                <span className="px-3 py-1 bg-blue-500/20 text-blue-400 text-xs rounded-full font-medium">
                    📊 DEMO MODE
                </span>
                {showExitButton && (
                    <button
                        onClick={exitDemo}
                        className="text-xs text-slate-500 hover:text-red-400 transition-colors"
                    >
                        Exit Demo
                    </button>
                )}
            </div>
        );
    }

    // Inline badge (default)
    return (
        <span className="px-3 py-1 bg-blue-500/20 text-blue-400 text-xs rounded-full">
            📊 DEMO MODE
        </span>
    );
}
