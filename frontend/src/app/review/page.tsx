'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

interface Transaction {
    id: string;
    amount: number;
    source: string;
    date: string;
    aiGuess: 'business' | 'personal' | 'gift';
    confidence: number;
    classification?: 'business' | 'personal' | 'gift' | 'unsure';
}

// Demo transactions (Rohan's ambiguous credits)
const DEMO_TRANSACTIONS: Transaction[] = [
    { id: '1', amount: 45000, source: 'UPI-RAZORPAY-MERCHANT', date: 'Jan 15, 2025', aiGuess: 'business', confidence: 0.72 },
    { id: '2', amount: 150000, source: 'HDFC-NEFT-KUMAR', date: 'Feb 28, 2025', aiGuess: 'personal', confidence: 0.45 },
    { id: '3', amount: 25000, source: 'PAYTM-TRANSFER-ABC', date: 'Mar 10, 2025', aiGuess: 'business', confidence: 0.68 },
    { id: '4', amount: 100000, source: 'ICICI-IMPS-FATHER', date: 'Apr 05, 2025', aiGuess: 'gift', confidence: 0.55 },
    { id: '5', amount: 35000, source: 'GPAY-FREELANCE-CLIENT', date: 'May 20, 2025', aiGuess: 'business', confidence: 0.82 },
];

const CLASSIFICATION_OPTIONS = [
    { id: 'business', label: 'Business Income', icon: '🔧', shortcut: 'B', description: 'Subject to 44ADA', color: 'orange' },
    { id: 'personal', label: 'Personal', icon: '👤', shortcut: 'P', description: 'Not taxable income', color: 'blue' },
    { id: 'gift', label: 'Gift', icon: '🎁', shortcut: 'G', description: 'From relative', color: 'purple' },
    { id: 'unsure', label: 'Unsure', icon: '❓', shortcut: 'U', description: 'Skip for now', color: 'slate' },
];

export default function TransactionReviewPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const isDemo = searchParams.get('demo') === 'true' || (typeof window !== 'undefined' && localStorage.getItem('demoMode') === 'true');

    const [transactions, setTransactions] = useState<Transaction[]>(DEMO_TRANSACTIONS);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [showClassified, setShowClassified] = useState(false);

    const pendingTransactions = transactions.filter(t => !t.classification);
    const classifiedTransactions = transactions.filter(t => t.classification);
    const currentTransaction = pendingTransactions[0]; // Always show first pending
    const isComplete = pendingTransactions.length === 0;

    const formatCurrency = (amount: number) => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0,
        }).format(amount);
    };

    // Keyboard shortcuts (Heuristic #7: Flexibility & Efficiency)
    const handleKeyDown = useCallback((e: KeyboardEvent) => {
        if (isComplete || !currentTransaction) return;

        switch (e.key.toLowerCase()) {
            case 'b': handleClassify('business'); break;
            case 'p': handleClassify('personal'); break;
            case 'g': handleClassify('gift'); break;
            case 'u': handleClassify('unsure'); break;
        }
    }, [currentTransaction, isComplete]);

    useEffect(() => {
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [handleKeyDown]);

    const handleClassify = (classification: 'business' | 'personal' | 'gift' | 'unsure') => {
        if (!currentTransaction) return;

        setTransactions(prev => prev.map(t =>
            t.id === currentTransaction.id
                ? { ...t, classification }
                : t
        ));
    };

    const handleUndo = (transactionId: string) => {
        setTransactions(prev => prev.map(t =>
            t.id === transactionId
                ? { ...t, classification: undefined }
                : t
        ));
    };

    const handleContinue = () => {
        const classified = transactions.map(t => ({
            ...t,
            classification: t.classification || 'unsure',
        }));
        localStorage.setItem('transactionClassifications', JSON.stringify(classified));
        router.push('/dashboard' + (isDemo ? '?demo=true' : ''));
    };

    const getConfidenceColor = (confidence: number) => {
        if (confidence >= 0.8) return 'text-emerald-400';
        if (confidence >= 0.6) return 'text-yellow-400';
        return 'text-red-400';
    };

    const getClassificationStyle = (type: string, isHighlighted = false) => {
        const base = {
            business: 'border-orange-500 bg-orange-500',
            personal: 'border-blue-500 bg-blue-500',
            gift: 'border-purple-500 bg-purple-500',
            unsure: 'border-slate-500 bg-slate-500',
        }[type] || 'border-slate-500 bg-slate-500';

        if (isHighlighted) {
            return `${base}/30 border-2`;
        }
        return `${base}/10 border-2 ${base.split(' ')[0]}/30`;
    };

    return (
        <div className="min-h-screen flex flex-col">
            {/* Header */}
            <header className="border-b border-slate-800 px-6 py-4">
                <div className="max-w-4xl mx-auto flex items-center justify-between">
                    <button
                        onClick={() => router.back()}
                        className="text-slate-400 hover:text-white flex items-center gap-2"
                    >
                        ← Back
                    </button>

                    <div className="flex items-center gap-3">
                        {isDemo && (
                            <span className="px-3 py-1 bg-blue-500/20 text-blue-400 text-xs rounded-full">
                                📊 DEMO MODE
                            </span>
                        )}
                        <span className="font-bold">🏷️ Transaction Review</span>
                        <span className="text-sm text-slate-400">
                            {classifiedTransactions.length}/{transactions.length} done
                        </span>
                    </div>

                    <div className="w-32" />
                </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 px-6 py-8">
                {/* Demo Banner (Full Width - Edge to Edge) */}
                {isDemo && (
                    <div className="w-full mb-6">
                        <div className="bg-blue-500/20 border-y border-blue-500/30 px-6 py-3 flex items-center justify-between">
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
                                    localStorage.removeItem('extractedData');
                                    localStorage.removeItem('transactionClassifications');
                                    router.push('/');
                                }}
                                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm transition-colors"
                            >
                                ✕ Exit Demo
                            </button>
                        </div>
                    </div>
                )}

                <div className="max-w-4xl mx-auto space-y-6">
                    {/* Instructions */}
                    <div className="card bg-blue-500/10 border-blue-500/30">
                        <div className="flex items-start gap-4">
                            <span className="text-2xl">💡</span>
                            <div>
                                <h2 className="font-bold text-lg">
                                    {isDemo ? 'Demo: Classify These Transactions' : 'Help Us Classify These Transactions'}
                                </h2>
                                <p className="text-slate-400 text-sm mt-1">
                                    Click a button or use keyboard shortcuts:
                                    <span className="ml-2 text-slate-300">
                                        <kbd className="px-2 py-1 bg-slate-700 rounded mx-1">B</kbd> Business
                                        <kbd className="px-2 py-1 bg-slate-700 rounded mx-1">P</kbd> Personal
                                        <kbd className="px-2 py-1 bg-slate-700 rounded mx-1">G</kbd> Gift
                                        <kbd className="px-2 py-1 bg-slate-700 rounded mx-1">U</kbd> Unsure
                                    </span>
                                </p>
                                {isDemo && (
                                    <p className="text-blue-400 text-sm mt-2">
                                        ✨ AI suggestion is highlighted. Try clicking a button to classify!
                                    </p>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Current Transaction Card */}
                    {!isComplete && currentTransaction && (
                        <div className="card space-y-6">
                            {/* Progress Header */}
                            <div className="flex items-center justify-between">
                                <h3 className="text-lg font-bold">
                                    Transaction {classifiedTransactions.length + 1} of {transactions.length}
                                </h3>
                                <div className="flex items-center gap-4">
                                    <span className={`${getConfidenceColor(currentTransaction.confidence)} text-sm`}>
                                        AI Confidence: {Math.round(currentTransaction.confidence * 100)}%
                                    </span>
                                </div>
                            </div>

                            {/* Transaction Details */}
                            <div className="bg-slate-800 rounded-xl p-8 text-center space-y-4">
                                <p className="text-sm text-slate-500">{currentTransaction.date}</p>
                                <p className="text-5xl font-bold text-emerald-400 fiscal-num">
                                    {formatCurrency(currentTransaction.amount)}
                                </p>
                                <p className="text-xl text-slate-300">{currentTransaction.source}</p>
                                <p className="text-sm text-slate-500">
                                    AI suggests: <span className="text-white font-medium capitalize">{currentTransaction.aiGuess}</span>
                                </p>
                            </div>

                            {/* Classification Buttons - ALWAYS VISIBLE AND CLICKABLE */}
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                {CLASSIFICATION_OPTIONS.map((option) => {
                                    const isAiSuggestion = currentTransaction.aiGuess === option.id;

                                    return (
                                        <button
                                            key={option.id}
                                            onClick={() => handleClassify(option.id as any)}
                                            className={`relative p-5 rounded-xl transition-all duration-200 hover:scale-105 active:scale-95 cursor-pointer ${getClassificationStyle(option.id, isAiSuggestion)}`}
                                        >
                                            {/* AI Suggestion Badge */}
                                            {isAiSuggestion && (
                                                <div className="absolute -top-2 -right-2 px-2 py-1 bg-emerald-500 text-white text-xs rounded-full shadow-lg">
                                                    AI Pick
                                                </div>
                                            )}

                                            <div className="text-center space-y-2">
                                                <span className="text-3xl">{option.icon}</span>
                                                <p className="font-semibold">{option.label}</p>
                                                <p className="text-xs text-slate-400">{option.description}</p>
                                                <p className="text-xs text-slate-500">
                                                    Press <kbd className="px-1 bg-slate-700 rounded">{option.shortcut}</kbd>
                                                </p>
                                            </div>
                                        </button>
                                    );
                                })}
                            </div>
                        </div>
                    )}

                    {/* Completion State */}
                    {isComplete && (
                        <div className="card-success text-center py-8 space-y-4">
                            <span className="text-5xl">✅</span>
                            <h2 className="text-2xl font-bold">All Transactions Classified!</h2>
                            <div className="flex justify-center gap-4 text-sm">
                                <span className="px-3 py-1 bg-orange-500/20 text-orange-400 rounded-full">
                                    {classifiedTransactions.filter(t => t.classification === 'business').length} Business
                                </span>
                                <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full">
                                    {classifiedTransactions.filter(t => t.classification === 'personal').length} Personal
                                </span>
                                <span className="px-3 py-1 bg-purple-500/20 text-purple-400 rounded-full">
                                    {classifiedTransactions.filter(t => t.classification === 'gift').length} Gift
                                </span>
                                <span className="px-3 py-1 bg-slate-500/20 text-slate-400 rounded-full">
                                    {classifiedTransactions.filter(t => t.classification === 'unsure').length} Unsure
                                </span>
                            </div>
                        </div>
                    )}

                    {/* Classified List (Collapsible) */}
                    {classifiedTransactions.length > 0 && (
                        <div className="space-y-3">
                            <button
                                onClick={() => setShowClassified(!showClassified)}
                                className="flex items-center gap-2 text-sm text-slate-400 hover:text-white"
                            >
                                <span>{showClassified ? '▼' : '▶'}</span>
                                <span>Your Classifications ({classifiedTransactions.length})</span>
                                <span className="text-xs text-slate-500">— click to {showClassified ? 'hide' : 'show'} or undo</span>
                            </button>

                            {showClassified && (
                                <div className="space-y-2 max-h-64 overflow-y-auto">
                                    {classifiedTransactions.map((t) => (
                                        <div
                                            key={t.id}
                                            className={`flex items-center justify-between p-3 rounded-lg border ${getClassificationStyle(t.classification!)}`}
                                        >
                                            <div className="flex items-center gap-4">
                                                <span className="font-bold fiscal-num">{formatCurrency(t.amount)}</span>
                                                <span className="text-sm opacity-70 truncate max-w-[200px]">{t.source}</span>
                                            </div>
                                            <div className="flex items-center gap-3">
                                                <span className="text-sm capitalize font-medium">{t.classification}</span>
                                                <button
                                                    onClick={() => handleUndo(t.id)}
                                                    className="px-2 py-1 text-xs bg-slate-700 hover:bg-slate-600 rounded transition-colors"
                                                >
                                                    Undo
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}

                    {/* Continue Button */}
                    <div className="flex items-center justify-between pt-4 border-t border-slate-800">
                        <div className="text-sm text-slate-400">
                            {!isComplete && (
                                <span>{pendingTransactions.length} transactions remaining</span>
                            )}
                        </div>
                        <button
                            onClick={handleContinue}
                            disabled={!isComplete}
                            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isComplete ? 'Continue to Dashboard →' : `Classify ${pendingTransactions.length} more to continue`}
                        </button>
                    </div>
                </div>
            </main>
        </div>
    );
}
