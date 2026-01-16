'use client';

import { useState } from 'react';

interface AmbiguousTransaction {
    id: string;
    amount: number;
    source: string;
    date: string;
}

interface AmbiguityModalProps {
    transactions: AmbiguousTransaction[];
    onComplete: (classifications: Record<string, 'business' | 'personal'>) => void;
    onCancel: () => void;
}

export default function AmbiguityModal({
    transactions,
    onComplete,
    onCancel
}: AmbiguityModalProps) {
    const [currentIndex, setCurrentIndex] = useState(0);
    const [classifications, setClassifications] = useState<Record<string, 'business' | 'personal'>>({});

    const currentTransaction = transactions[currentIndex];
    const isLast = currentIndex === transactions.length - 1;
    const progress = ((currentIndex + 1) / transactions.length) * 100;

    const formatCurrency = (amount: number) => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0,
        }).format(amount);
    };

    const handleClassify = (type: 'business' | 'personal') => {
        const newClassifications = {
            ...classifications,
            [currentTransaction.id]: type,
        };
        setClassifications(newClassifications);

        if (isLast) {
            onComplete(newClassifications);
        } else {
            setCurrentIndex(currentIndex + 1);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-lg w-full mx-4 overflow-hidden">
                {/* Header */}
                <div className="border-b border-slate-700 p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-bold">🎯 Human-in-the-Loop</h2>
                        <button
                            onClick={onCancel}
                            className="text-slate-400 hover:text-white"
                        >
                            ✕
                        </button>
                    </div>

                    <p className="text-slate-400 text-sm">
                        We found <span className="text-blue-400 font-semibold">{transactions.length}</span> ambiguous credits.
                        Help us classify them for accurate tax calculation.
                    </p>

                    {/* Progress */}
                    <div className="mt-4">
                        <div className="flex justify-between text-xs text-slate-500 mb-1">
                            <span>Transaction {currentIndex + 1} of {transactions.length}</span>
                            <span>{Math.round(progress)}%</span>
                        </div>
                        <div className="h-1 bg-slate-700 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-emerald-500 transition-all duration-300"
                                style={{ width: `${progress}%` }}
                            />
                        </div>
                    </div>
                </div>

                {/* Transaction Card */}
                <div className="p-6">
                    <div className="bg-slate-800 rounded-xl p-6 text-center space-y-4">
                        <p className="text-3xl font-bold text-emerald-400 fiscal-num">
                            {formatCurrency(currentTransaction.amount)}
                        </p>
                        <div>
                            <p className="text-lg font-medium">{currentTransaction.source}</p>
                            <p className="text-sm text-slate-400">{currentTransaction.date}</p>
                        </div>
                    </div>

                    <p className="text-center text-slate-300 mt-6 mb-4">
                        Is this <span className="text-orange-400 font-semibold">Business Income</span> or{' '}
                        <span className="text-blue-400 font-semibold">Personal</span>?
                    </p>

                    {/* Action Buttons */}
                    <div className="grid grid-cols-2 gap-4">
                        <button
                            onClick={() => handleClassify('business')}
                            className="p-4 rounded-xl border-2 border-orange-500/30 bg-orange-500/10 hover:bg-orange-500/20 transition-all text-center"
                        >
                            <span className="text-2xl">🔧</span>
                            <p className="font-semibold mt-2">Business Income</p>
                            <p className="text-xs text-slate-400 mt-1">Subject to 44ADA</p>
                        </button>

                        <button
                            onClick={() => handleClassify('personal')}
                            className="p-4 rounded-xl border-2 border-blue-500/30 bg-blue-500/10 hover:bg-blue-500/20 transition-all text-center"
                        >
                            <span className="text-2xl">👤</span>
                            <p className="font-semibold mt-2">Personal / Refund</p>
                            <p className="text-xs text-slate-400 mt-1">Not taxable income</p>
                        </button>
                    </div>
                </div>

                {/* Footer Hint */}
                <div className="border-t border-slate-700 p-4 text-center text-xs text-slate-500">
                    💡 Your classification improves accuracy. Review carefully.
                </div>
            </div>
        </div>
    );
}
