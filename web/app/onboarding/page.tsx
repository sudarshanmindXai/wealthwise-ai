'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

interface Guardian {
    id: string;
    name: string;
    icon: string;
    description: string;
    color: string;
}

const GUARDIANS: Guardian[] = [
    {
        id: 'sentinel',
        name: 'Salaried Job',
        icon: '💼',
        description: 'Form 16, HRA, NPS, LTA optimizations',
        color: 'border-blue-500 bg-blue-500/10',
    },
    {
        id: 'shield',
        name: 'Freelancing / Gig Work',
        icon: '🔧',
        description: 'Sec 44ADA, Bank statement classification',
        color: 'border-orange-500 bg-orange-500/10',
    },
    {
        id: 'architect',
        name: 'Stocks & Crypto',
        icon: '📊',
        description: 'LTCG harvesting, 115BBH compliance',
        color: 'border-purple-500 bg-purple-500/10',
    },
    {
        id: 'warden',
        name: 'Rent / Gifts',
        icon: '🎁',
        description: 'Rental income, Gift taxation',
        color: 'border-teal-500 bg-teal-500/10',
    },
];

export default function OnboardingPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const isDemo = searchParams.get('demo') === 'true' || (typeof window !== 'undefined' && localStorage.getItem('demoMode') === 'true');

    const [selected, setSelected] = useState<Set<string>>(new Set());
    const [step, setStep] = useState(1);

    // In demo mode, pre-select guardians based on "Rohan" profile
    useEffect(() => {
        if (isDemo) {
            // Rohan has: Salary + Freelance + Stocks (not Windfall)
            setSelected(new Set(['sentinel', 'shield', 'architect']));
        }
    }, [isDemo]);

    const toggleGuardian = (id: string) => {
        const newSelected = new Set(selected);
        if (newSelected.has(id)) {
            newSelected.delete(id);
        } else {
            newSelected.add(id);
        }
        setSelected(newSelected);
    };

    const handleContinue = () => {
        if (selected.size === 0) return;
        localStorage.setItem('activeGuardians', JSON.stringify(Array.from(selected)));
        if (isDemo) {
            localStorage.setItem('demoMode', 'true');
        }
        router.push('/ingest' + (isDemo ? '?demo=true' : ''));
    };

    return (
        <div className="min-h-screen flex flex-col">
            {/* Tunnel Header */}
            <header className="border-b border-slate-800 px-6 py-4">
                <div className="max-w-4xl mx-auto flex items-center justify-between">
                    <button
                        onClick={() => router.push('/')}
                        className="text-slate-400 hover:text-white flex items-center gap-2"
                    >
                        ← Back
                    </button>

                    <div className="flex items-center gap-3">
                        {isDemo && (
                            <>
                                <span className="px-3 py-1 bg-blue-500/20 text-blue-400 text-xs rounded-full">
                                    📊 DEMO MODE
                                </span>
                                <button
                                    onClick={() => {
                                        localStorage.removeItem('demoMode');
                                        localStorage.removeItem('activeGuardians');
                                        router.push('/');
                                    }}
                                    className="text-xs text-slate-500 hover:text-red-400"
                                >
                                    Exit Demo
                                </button>
                            </>
                        )}
                        <span className="text-sm text-slate-400">Step {step} of 3</span>
                        <div className="w-32 h-1 bg-slate-800 rounded-full overflow-hidden">
                            <div
                                className="tunnel-progress"
                                style={{ width: `${(step / 3) * 100}%` }}
                            />
                        </div>
                    </div>

                    <span className="text-sm text-slate-500">Identity Sieve</span>
                </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 flex flex-col items-center justify-center px-6 py-12">
                {/* Demo Banner (Full Width - Edge to Edge) */}
                {isDemo && (
                    <div className="w-full mb-6 -mt-12 px-0">
                        <div className="bg-blue-500/20 border border-blue-500/30 rounded-xl px-6 py-3 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <span className="text-2xl">📊</span>
                                <div>
                                    <p className="font-bold text-blue-400">DEMO MODE</p>
                                    <p className="text-sm text-slate-400">
                                        Viewing sample results for Rohan Sharma. This is not your real data.
                                    </p>
                                </div>
                            </div>
                            <button
                                onClick={() => {
                                    localStorage.removeItem('demoMode');
                                    localStorage.removeItem('activeGuardians');
                                    router.push('/');
                                }}
                                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm transition-colors"
                            >
                                ✕ Exit Demo
                            </button>
                        </div>
                    </div>
                )}

                <div className="max-w-2xl w-full space-y-8">
                    {/* Question */}
                    <div className="text-center space-y-4">
                        <h1 className="text-3xl md:text-4xl font-bold">
                            What defines your financial year?
                        </h1>
                        <p className="text-lg text-slate-400">
                            {isDemo
                                ? "We've pre-selected Rohan's income sources. You can adjust if you'd like."
                                : "Select all that apply. We'll activate the right Guardians for you."
                            }
                        </p>
                    </div>

                    {/* Guardian Selection Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {GUARDIANS.map((guardian) => {
                            const isSelected = selected.has(guardian.id);
                            return (
                                <button
                                    key={guardian.id}
                                    onClick={() => toggleGuardian(guardian.id)}
                                    className={`p-6 rounded-xl border-2 text-left transition-all duration-200 hover-lift ${isSelected
                                        ? guardian.color
                                        : 'border-slate-700 hover:border-slate-600 bg-slate-900'
                                        }`}
                                >
                                    <div className="flex items-start gap-4">
                                        <span className="text-3xl">{guardian.icon}</span>
                                        <div className="flex-1">
                                            <div className="flex items-center justify-between">
                                                <span className="font-semibold text-lg">{guardian.name}</span>
                                                {isSelected && (
                                                    <span className="text-emerald-400 text-xl">✓</span>
                                                )}
                                            </div>
                                            <p className="text-sm text-slate-400 mt-1">
                                                {guardian.description}
                                            </p>
                                        </div>
                                    </div>
                                </button>
                            );
                        })}
                    </div>

                    {/* Demo Info */}
                    {isDemo && (
                        <div className="terminal-log text-sm">
                            <p>&gt; Demo Profile: <span className="text-emerald-400">Rohan Sharma</span></p>
                            <p>&gt; Income: ₹18.5L Salary + ₹6L Freelance + ₹1.3L Stocks</p>
                            <p>&gt; Documents will be pre-filled for you...</p>
                        </div>
                    )}

                    {/* Continue Button */}
                    <div className="flex justify-center pt-4">
                        <button
                            onClick={handleContinue}
                            disabled={selected.size === 0}
                            className="btn-primary text-lg px-12 py-4 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isDemo ? 'Continue Demo →' : 'Initialize Guardians →'}
                        </button>
                    </div>
                </div>
            </main>
        </div>
    );
}
