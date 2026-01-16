'use client';

interface VictoryStateProps {
    totalSavings: number;
    originalTax: number;
    optimizedTax: number;
    badges: Badge[];
    onDownload: () => void;
}

interface Badge {
    id: string;
    name: string;
    icon: string;
}

export default function VictoryState({
    totalSavings,
    originalTax,
    optimizedTax,
    badges,
    onDownload,
}: VictoryStateProps) {
    const formatCurrency = (amount: number) => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0,
        }).format(amount);
    };

    const savingsPercentage = Math.round((totalSavings / originalTax) * 100);

    return (
        <div className="min-h-screen flex items-center justify-center p-8">
            <div className="max-w-2xl w-full text-center space-y-8">
                {/* Celebration Animation */}
                <div className="relative">
                    <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/20 to-blue-500/20 blur-3xl -z-10" />

                    <span className="text-7xl block mb-4">🏆</span>

                    <h1 className="text-4xl font-bold">
                        <span className="text-gradient">Optimization Complete!</span>
                    </h1>
                </div>

                {/* Summary Card */}
                <div className="card bg-gradient-to-br from-emerald-900/30 to-slate-900">
                    <p className="text-lg text-slate-400 mb-2">Total Wealth Rescued</p>
                    <p className="text-5xl font-bold text-emerald-400 fiscal-num">
                        {formatCurrency(totalSavings)}
                    </p>
                    <p className="text-sm text-slate-500 mt-2">
                        {savingsPercentage}% reduction from ₹{(originalTax / 100000).toFixed(1)}L
                    </p>

                    {/* Before/After */}
                    <div className="grid grid-cols-2 gap-6 mt-8 pt-6 border-t border-slate-700">
                        <div>
                            <p className="text-sm text-red-400">Original Tax</p>
                            <p className="text-2xl font-bold text-slate-400 line-through fiscal-num">
                                {formatCurrency(originalTax)}
                            </p>
                        </div>
                        <div>
                            <p className="text-sm text-emerald-400">Optimized Tax</p>
                            <p className="text-2xl font-bold text-white fiscal-num">
                                {formatCurrency(optimizedTax)}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Badges */}
                <div className="space-y-4">
                    <p className="text-lg text-slate-400">Achievements Unlocked</p>
                    <div className="flex justify-center gap-4 flex-wrap">
                        {badges.map((badge) => (
                            <div
                                key={badge.id}
                                className="px-4 py-3 bg-slate-800 rounded-xl border border-slate-700 flex items-center gap-2 hover-lift"
                            >
                                <span className="text-2xl">{badge.icon}</span>
                                <span className="font-medium">{badge.name}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Download Section */}
                <div className="space-y-4 pt-4">
                    <button
                        onClick={onDownload}
                        className="btn-primary text-lg px-12 py-4 hover-lift"
                    >
                        📄 Download Form 12BB
                    </button>

                    <div className="flex justify-center gap-4 text-sm">
                        <button className="btn-ghost">
                            Download Strategy PDF
                        </button>
                        <button className="btn-ghost">
                            Export for CA (JSON)
                        </button>
                    </div>
                </div>

                {/* Disclaimer */}
                <p className="text-xs text-slate-500 max-w-md mx-auto">
                    This optimization is based on your inputs for FY 2025-26.
                    Please verify with a Chartered Accountant before filing.
                </p>
            </div>
        </div>
    );
}
