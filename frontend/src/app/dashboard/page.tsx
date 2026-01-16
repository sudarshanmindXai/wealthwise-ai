'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import ChatPanel from '@/components/ChatPanel';
import DemoBanner from '@/components/ui/DemoBanner';

interface Guardian {
    id: string;
    name: string;
    icon: string;
    status: 'scanning' | 'optimized' | 'action_required' | 'inactive';
    savings: number;
    badgeClass: string;
}

const GUARDIAN_DATA: Record<string, Guardian> = {
    sentinel: {
        id: 'sentinel',
        name: 'Salary Sentinel',
        icon: '💼',
        status: 'action_required',
        savings: 37800,
        badgeClass: 'badge-sentinel',
    },
    shield: {
        id: 'shield',
        name: 'Hustle Shield',
        icon: '🔧',
        status: 'optimized',
        savings: 45000,
        badgeClass: 'badge-shield',
    },
    architect: {
        id: 'architect',
        name: 'Portfolio Architect',
        icon: '📊',
        status: 'action_required',
        savings: 0,
        badgeClass: 'badge-architect',
    },
    warden: {
        id: 'warden',
        name: 'Windfall Warden',
        icon: '🎁',
        status: 'optimized',
        savings: 12600,
        badgeClass: 'badge-warden',
    },
};

export default function Dashboard() {
    const searchParams = useSearchParams();
    const isDemo = searchParams.get('demo') === 'true' || (typeof window !== 'undefined' && localStorage.getItem('demoMode') === 'true');

    const [activeGuardians, setActiveGuardians] = useState<string[]>([]);
    const [oldRegimeTax, setOldRegimeTax] = useState(245000);
    const [newRegimeTax, setNewRegimeTax] = useState(220000);
    const [rentPaid, setRentPaid] = useState(20000);
    const [showConfetti, setShowConfetti] = useState(false);

    useEffect(() => {
        // Load active guardians
        const stored = localStorage.getItem('activeGuardians');
        if (stored) {
            setActiveGuardians(JSON.parse(stored));
        } else {
            // Default: all guardians
            setActiveGuardians(['sentinel', 'shield', 'architect', 'warden']);
        }
    }, []);

    // IKEA Effect: Rent slider updates tax in real-time
    const handleRentChange = (value: number) => {
        setRentPaid(value);
        // Simulate HRA impact on Old Regime
        const hraExemption = Math.min(value * 12, value * 12 - 90000, 450000);
        const newOldTax = 245000 - (hraExemption * 0.30);
        setOldRegimeTax(Math.max(150000, newOldTax));
    };

    const formatCurrency = (amount: number) => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0,
        }).format(amount);
    };

    const totalSavings = Object.values(GUARDIAN_DATA)
        .filter(g => activeGuardians.includes(g.id))
        .reduce((sum, g) => sum + g.savings, 0);

    const winner = newRegimeTax < oldRegimeTax ? 'new' : 'old';
    const savingsAmount = Math.abs(newRegimeTax - oldRegimeTax);

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'optimized': return 'border-l-emerald-500';
            case 'action_required': return 'border-l-yellow-500';
            case 'scanning': return 'border-l-blue-500 animate-pulse';
            default: return 'border-l-slate-600';
        }
    };

    const getStatusText = (status: string) => {
        switch (status) {
            case 'optimized': return '✓ Optimized';
            case 'action_required': return '⚠️ Action Required';
            case 'scanning': return '⏳ Scanning...';
            default: return 'Inactive';
        }
    };

    return (
        <div className="min-h-screen flex">
            {/* Sidebar (Cockpit Navigation) */}
            <aside className="w-64 border-r border-slate-800 bg-slate-900 p-6 flex flex-col">
                <div className="flex items-center gap-2 mb-8">
                    <span className="text-2xl">💰</span>
                    <span className="text-lg font-bold">WealthWise AI</span>
                </div>

                <nav className="space-y-2 flex-1">
                    <Link href="/dashboard" className="flex items-center gap-3 px-4 py-3 rounded-lg bg-slate-800 text-white">
                        <span>📊</span>
                        <span>Overview</span>
                    </Link>

                    {activeGuardians.includes('sentinel') && (
                        <Link href="/dashboard/salary" className="flex items-center gap-3 px-4 py-3 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800">
                            <span>💼</span>
                            <span>Salary</span>
                        </Link>
                    )}

                    {activeGuardians.includes('shield') && (
                        <Link href="/dashboard/hustle" className="flex items-center gap-3 px-4 py-3 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800">
                            <span>🔧</span>
                            <span>Hustle</span>
                        </Link>
                    )}

                    {activeGuardians.includes('architect') && (
                        <Link href="/dashboard/portfolio" className="flex items-center gap-3 px-4 py-3 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800">
                            <span>📊</span>
                            <span>Portfolio</span>
                        </Link>
                    )}

                    {activeGuardians.includes('warden') && (
                        <Link href="/dashboard/windfall" className="flex items-center gap-3 px-4 py-3 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800">
                            <span>🎁</span>
                            <span>Windfall</span>
                        </Link>
                    )}

                    <div className="pt-4 border-t border-slate-800 mt-4">
                        <Link href="/dashboard/report" className="flex items-center gap-3 px-4 py-3 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800">
                            <span>📄</span>
                            <span>Generate Report</span>
                        </Link>
                    </div>
                </nav>

                <div className="pt-4 border-t border-slate-800 text-xs text-slate-500">
                    <p>🔒 Session expires in 29:59</p>
                    <p>FY 2025-26 (AY 2026-27)</p>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-auto">
                {/* Demo Banner (Full Width) */}
                {isDemo && <DemoBanner variant="full" />}

                {/* Header */}
                <header className="border-b border-slate-800 px-8 py-4 flex justify-between items-center">
                    <div>
                        <h1 className="text-2xl font-bold">Tax Optimization Dashboard</h1>
                        <p className="text-slate-400 text-sm">FY 2025-26 • Last updated just now</p>
                    </div>
                    <div className="text-right">
                        <p className="text-sm text-slate-400">Potential Savings</p>
                        <p className="text-2xl font-bold text-emerald-400 fiscal-num">
                            {formatCurrency(totalSavings)}
                        </p>
                    </div>
                </header>

                <div className="p-8 space-y-8">
                    {/* Twin-Engine: Regime Comparison */}
                    <section className="card">
                        <h2 className="text-xl font-bold mb-6">Regime Showdown</h2>

                        <div className="grid grid-cols-2 gap-8">
                            {/* Old Regime */}
                            <div className={`p-6 rounded-xl ${winner === 'old' ? 'bg-emerald-900/20 border border-emerald-500/30' : 'bg-slate-800/50'}`}>
                                <div className="flex justify-between items-center mb-4">
                                    <h3 className="font-semibold">Old Regime</h3>
                                    {winner === 'old' && (
                                        <span className="px-3 py-1 bg-emerald-500 text-white text-sm rounded-full winner-glow">
                                            WINNER
                                        </span>
                                    )}
                                </div>
                                <div className="h-40 bg-slate-900 rounded-lg flex items-end p-4">
                                    <div
                                        className="tax-bar tax-bar-old w-full"
                                        style={{ height: `${(oldRegimeTax / 300000) * 100}%` }}
                                    />
                                </div>
                                <p className="text-center mt-4 text-2xl font-bold fiscal-num">
                                    {formatCurrency(oldRegimeTax)}
                                </p>
                            </div>

                            {/* New Regime */}
                            <div className={`p-6 rounded-xl ${winner === 'new' ? 'bg-emerald-900/20 border border-emerald-500/30' : 'bg-slate-800/50'}`}>
                                <div className="flex justify-between items-center mb-4">
                                    <h3 className="font-semibold">New Regime</h3>
                                    {winner === 'new' && (
                                        <span className="px-3 py-1 bg-emerald-500 text-white text-sm rounded-full winner-glow">
                                            WINNER
                                        </span>
                                    )}
                                </div>
                                <div className="h-40 bg-slate-900 rounded-lg flex items-end p-4">
                                    <div
                                        className="tax-bar tax-bar-new w-full"
                                        style={{ height: `${(newRegimeTax / 300000) * 100}%` }}
                                    />
                                </div>
                                <p className="text-center mt-4 text-2xl font-bold fiscal-num">
                                    {formatCurrency(newRegimeTax)}
                                </p>
                            </div>
                        </div>

                        <div className="mt-6 text-center">
                            <p className="text-lg text-slate-400">
                                {winner === 'new' ? 'New' : 'Old'} Regime saves you{' '}
                                <span className="text-emerald-400 font-bold fiscal-num">{formatCurrency(savingsAmount)}</span>
                            </p>
                        </div>
                    </section>

                    {/* IKEA Effect: Rent Slider */}
                    {activeGuardians.includes('sentinel') && (
                        <section className="card">
                            <h2 className="text-xl font-bold mb-4">🏠 Rent Optimizer (HRA Impact)</h2>
                            <p className="text-slate-400 mb-6">
                                Drag the slider to see how rent affects your Old Regime tax.
                            </p>

                            <div className="space-y-4">
                                <div className="flex justify-between text-sm">
                                    <span className="text-slate-400">₹0</span>
                                    <span className="text-emerald-400 font-bold fiscal-num">
                                        ₹{rentPaid.toLocaleString('en-IN')}/month
                                    </span>
                                    <span className="text-slate-400">₹50,000</span>
                                </div>

                                <input
                                    type="range"
                                    min="0"
                                    max="50000"
                                    step="1000"
                                    value={rentPaid}
                                    onChange={(e) => handleRentChange(Number(e.target.value))}
                                    className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
                                />

                                <div className="terminal-log">
                                    <p>&gt; HRA Exemption: {formatCurrency(rentPaid * 12 * 0.5)}</p>
                                    <p>&gt; Old Regime Tax Updated: {formatCurrency(oldRegimeTax)}</p>
                                </div>
                            </div>
                        </section>
                    )}

                    {/* Guardian Cards Grid */}
                    <section>
                        <h2 className="text-xl font-bold mb-6">Guardian Status</h2>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {activeGuardians.map((guardianId) => {
                                const guardian = GUARDIAN_DATA[guardianId];
                                if (!guardian) return null;

                                return (
                                    <div
                                        key={guardian.id}
                                        className={`card border-l-4 ${getStatusColor(guardian.status)} cursor-pointer hover:bg-slate-800/50 transition-all`}
                                    >
                                        <div className="flex items-start justify-between">
                                            <div className="flex items-center gap-4">
                                                <span className="text-3xl">{guardian.icon}</span>
                                                <div>
                                                    <h3 className="font-semibold">{guardian.name}</h3>
                                                    <p className="text-sm text-slate-400">
                                                        {getStatusText(guardian.status)}
                                                    </p>
                                                </div>
                                            </div>

                                            {guardian.savings > 0 && (
                                                <div className="text-right">
                                                    <p className="text-xs text-slate-400">Savings</p>
                                                    <p className="text-lg font-bold text-emerald-400 fiscal-num">
                                                        +{formatCurrency(guardian.savings)}
                                                    </p>
                                                </div>
                                            )}
                                        </div>

                                        {guardian.status === 'action_required' && (
                                            <button className="btn-primary mt-4 w-full text-sm">
                                                Fix Issue →
                                            </button>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    </section>

                    {/* Victory CTA */}
                    <section className="card bg-gradient-to-r from-emerald-900/30 to-blue-900/30 text-center">
                        <h2 className="text-2xl font-bold mb-2">Ready to Lock Your Strategy?</h2>
                        <p className="text-slate-400 mb-6">
                            Total potential savings: <span className="text-emerald-400 font-bold fiscal-num">{formatCurrency(totalSavings)}</span>
                        </p>
                        <div className="flex justify-center gap-4">
                            <button className="btn-primary text-lg px-8">
                                Lock Strategy & Generate Report
                            </button>
                        </div>
                    </section>
                </div>
            </main>

            {/* CA Companion Chat */}
            <ChatPanel
                userContext={{
                    gross_income: 2400000,
                    tax_old: oldRegimeTax,
                    tax_new: newRegimeTax,
                    recommended: winner,
                    potential_savings: totalSavings,
                }}
            />
        </div>
    );
}
