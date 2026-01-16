'use client';

import { useState } from 'react';

interface UnlockCardProps {
    title: string;
    section: string;
    potential_savings: number;
    description: string;
    icon: string;
    onActivate: () => void;
}

export default function UnlockCard({
    title,
    section,
    potential_savings,
    description,
    icon,
    onActivate,
}: UnlockCardProps) {
    const [isUnlocking, setIsUnlocking] = useState(false);
    const [isUnlocked, setIsUnlocked] = useState(false);
    const [showConfetti, setShowConfetti] = useState(false);

    const formatCurrency = (amount: number) => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0,
        }).format(amount);
    };

    const handleUnlock = () => {
        setIsUnlocking(true);

        // Simulate processing
        setTimeout(() => {
            setIsUnlocking(false);
            setIsUnlocked(true);
            setShowConfetti(true);
            onActivate();

            // Hide confetti after animation
            setTimeout(() => setShowConfetti(false), 3000);
        }, 1500);
    };

    if (isUnlocked) {
        return (
            <div className="card-success relative overflow-hidden">
                {/* Confetti Animation */}
                {showConfetti && (
                    <div className="absolute inset-0 pointer-events-none">
                        <div className="absolute top-0 left-1/4 w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '0s' }} />
                        <div className="absolute top-0 left-1/2 w-2 h-2 bg-yellow-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                        <div className="absolute top-0 left-3/4 w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                    </div>
                )}

                <div className="flex items-center gap-4">
                    <span className="text-4xl">{icon}</span>
                    <div className="flex-1">
                        <div className="flex items-center gap-2">
                            <span className="text-emerald-400 text-xl">✓</span>
                            <h3 className="font-bold text-lg">{title} Activated!</h3>
                        </div>
                        <p className="text-slate-400 text-sm mt-1">{section}</p>
                    </div>
                    <div className="text-right">
                        <p className="text-sm text-slate-400">Saved</p>
                        <p className="text-2xl font-bold text-emerald-400 fiscal-num">
                            {formatCurrency(potential_savings)}
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="card border-l-4 border-l-yellow-500 relative">
            {/* Locked Indicator */}
            <div className="absolute top-4 right-4">
                <span className="px-2 py-1 bg-yellow-500/20 text-yellow-400 text-xs rounded-full">
                    🔒 Locked
                </span>
            </div>

            <div className="flex items-start gap-4">
                <span className="text-4xl opacity-50">{icon}</span>
                <div className="flex-1">
                    <h3 className="font-bold text-lg">{title}</h3>
                    <p className="text-sm text-slate-400 mt-1">{description}</p>
                    <p className="text-xs text-slate-500 mt-2">{section}</p>
                </div>
            </div>

            <div className="mt-4 pt-4 border-t border-slate-700 flex items-center justify-between">
                <div>
                    <p className="text-xs text-slate-400">Potential Savings</p>
                    <p className="text-xl font-bold text-yellow-400 fiscal-num">
                        {formatCurrency(potential_savings)}
                    </p>
                </div>

                <button
                    onClick={handleUnlock}
                    disabled={isUnlocking}
                    className="btn-primary disabled:opacity-50"
                >
                    {isUnlocking ? (
                        <span className="flex items-center gap-2">
                            <span className="animate-spin">⏳</span>
                            Activating...
                        </span>
                    ) : (
                        <span>Activate {title} →</span>
                    )}
                </button>
            </div>
        </div>
    );
}
