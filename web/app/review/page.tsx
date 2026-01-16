"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { DemoBanner } from "@/components/DemoBanner";
import { TunnelHeader } from "@/components/TunnelHeader";
import {
    Wrench,
    User,
    Gift,
    HelpCircle,
    ArrowRight,
    ChevronDown,
    Undo2,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface Transaction {
    id: number;
    date: string;
    amount: number;
    description: string;
    aiSuggestion: "business" | "personal" | "gift" | "unsure";
    aiConfidence: number;
}

interface Classification {
    transactionId: number;
    category: "business" | "personal" | "gift" | "unsure";
}

const DEMO_TRANSACTIONS: Transaction[] = [
    {
        id: 1,
        date: "Jan 15, 2025",
        amount: 45000,
        description: "UPI-RAZORPAY-MERCHANT",
        aiSuggestion: "business",
        aiConfidence: 72,
    },
    {
        id: 2,
        date: "Jan 22, 2025",
        amount: 25000,
        description: "NEFT-KUMAR FAMILY TRUST",
        aiSuggestion: "gift",
        aiConfidence: 85,
    },
    {
        id: 3,
        date: "Feb 01, 2025",
        amount: 18500,
        description: "UPI-PAYTM-TRANSFER",
        aiSuggestion: "personal",
        aiConfidence: 68,
    },
    {
        id: 4,
        date: "Feb 14, 2025",
        amount: 50000,
        description: "IMPS-MOM-DAD-ANNIVERSARY",
        aiSuggestion: "gift",
        aiConfidence: 91,
    },
    {
        id: 5,
        date: "Feb 28, 2025",
        amount: 32000,
        description: "RTGS-CLIENT-PAYMENT-FEB",
        aiSuggestion: "personal",
        aiConfidence: 54,
    },
];

const CATEGORY_CONFIG = {
    business: {
        label: "Business Income",
        subtitle: "Subject to 44ADA",
        icon: Wrench,
        shortcut: "B",
        color: "border-orange-500/50 bg-orange-500/10 text-orange-400",
        activeColor: "border-orange-500 bg-orange-500/20",
    },
    personal: {
        label: "Personal",
        subtitle: "Not taxable income",
        icon: User,
        shortcut: "P",
        color: "border-slate-600 bg-slate-800/50 text-slate-300",
        activeColor: "border-slate-500 bg-slate-700",
    },
    gift: {
        label: "Gift",
        subtitle: "From relative",
        icon: Gift,
        shortcut: "G",
        color: "border-red-500/50 bg-red-500/10 text-red-400",
        activeColor: "border-red-500 bg-red-500/20",
    },
    unsure: {
        label: "Unsure",
        subtitle: "Skip for now",
        icon: HelpCircle,
        shortcut: "U",
        color: "border-slate-600 bg-slate-800/50 text-slate-400",
        activeColor: "border-slate-500 bg-slate-700",
    },
};

import { Suspense } from "react";

function ReviewContent() {
    const searchParams = useSearchParams();
    const isDemo = searchParams.get("demo") === "true";
    const [currentIndex, setCurrentIndex] = useState(0);
    const [classifications, setClassifications] = useState<Classification[]>([]);
    const [showClassifications, setShowClassifications] = useState(false);

    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    // Fetch transactions
    useEffect(() => {
        if (isDemo) {
            setTransactions(DEMO_TRANSACTIONS);
            return;
        }

        const fetchTransactions = async () => {
            setIsLoading(true);
            try {
                const res = await fetch("http://localhost:8000/api/v1/review/transactions");
                if (res.ok) {
                    const data = await res.json();
                    // Map API data to UI structure if needed (checking keys)
                    // API returns: id, date, description, amount, category, confidence
                    // UI Expects: same + aiSuggestion (mapped from category)

                    const mapped = data.map((t: any) => ({
                        ...t,
                        aiSuggestion: t.category,
                        aiConfidence: Math.round(t.confidence * 100)
                    }));

                    setTransactions(mapped);
                }
            } catch (err) {
                console.error("Failed to fetch transactions", err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchTransactions();
    }, [isDemo]);

    const displayTransactions = transactions;
    const currentTransaction = displayTransactions[currentIndex];
    const isComplete = displayTransactions.length > 0 && classifications.length === displayTransactions.length;

    const classify = useCallback(
        (category: "business" | "personal" | "gift" | "unsure") => {
            if (isComplete) return;

            if (!currentTransaction) return; // Guard

            setClassifications((prev) => [
                ...prev,
                { transactionId: currentTransaction.id, category },
            ]);

            if (currentIndex < displayTransactions.length - 1) {
                setCurrentIndex((prev) => prev + 1);
            }
        },
        [currentIndex, currentTransaction, isComplete, displayTransactions.length]
    );

    // Keyboard shortcuts
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (isComplete) return;

            switch (e.key.toLowerCase()) {
                case "b":
                    classify("business");
                    break;
                case "p":
                    classify("personal");
                    break;
                case "g":
                    classify("gift");
                    break;
                case "u":
                    classify("unsure");
                    break;
            }
        };

        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, [classify, isComplete]);

    const undoLast = () => {
        if (classifications.length === 0) return;
        setClassifications((prev) => prev.slice(0, -1));
        if (currentIndex > 0 && classifications.length === currentIndex + 1) {
            setCurrentIndex((prev) => prev - 1);
        }
    };

    const getCategoryCounts = () => {
        const counts = { business: 0, personal: 0, gift: 0, unsure: 0 };
        classifications.forEach((c) => counts[c.category]++);
        return counts;
    };

    const counts = getCategoryCounts();

    return (
        <div className="min-h-screen bg-slate-950 flex flex-col">
            {/* Demo Banner */}
            {isDemo && <DemoBanner />}

            {/* Tunnel Header */}
            <TunnelHeader
                title={isComplete
                    ? (isDemo ? "Classification Complete" : "Review Finalized")
                    : (isDemo ? "Transaction Review" : "Intelligent Classification")
                }
                step={isComplete ? 4 : 3}
                totalSteps={5}
                backHref={isDemo ? "/ingest?demo=true" : "/ingest"}
                isDemo={isDemo}
            />

            {/* Main Content */}
            <main className="flex-1 container py-8 px-4">
                <div className="max-w-3xl mx-auto space-y-6">
                    {/* Instructions Card */}
                    <div className={cn(
                        "border rounded-xl p-5 transition-all duration-300",
                        isDemo ? "bg-slate-900 border-slate-800" : "bg-emerald-500/5 border-emerald-500/20"
                    )}>
                        <div className="flex items-start gap-4">
                            <div className="text-2xl">{isDemo ? "💡" : "✨"}</div>
                            <div>
                                <h2 className="text-lg font-semibold text-white mb-2">
                                    {isDemo ? "Demo: Classify These Transactions" : "Review High-Value Transactions"}
                                </h2>
                                <p className="text-slate-400 text-sm mb-2">
                                    {isDemo
                                        ? "Click a button or use keyboard shortcuts below."
                                        : "Our AI has flagged these for review. Confirm or change categories to optimize your tax position."
                                    }
                                </p>
                                <div className="flex flex-wrap gap-2 mt-3">
                                    <kbd className="px-1.5 py-0.5 bg-slate-800 border border-slate-700 rounded text-[10px] font-mono text-slate-400">B: Business</kbd>
                                    <kbd className="px-1.5 py-0.5 bg-slate-800 border border-slate-700 rounded text-[10px] font-mono text-slate-400">P: Personal</kbd>
                                    <kbd className="px-1.5 py-0.5 bg-slate-800 border border-slate-700 rounded text-[10px] font-mono text-slate-400">G: Gift</kbd>
                                    <kbd className="px-1.5 py-0.5 bg-slate-800 border border-slate-700 rounded text-[10px] font-mono text-slate-400">U: Unsure</kbd>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Transaction Card or Completion State */}
                    {displayTransactions.length === 0 && !isLoading ? (
                        <div className="text-center py-12 border rounded-xl border-dashed border-slate-800">
                            <div className="text-4xl mb-4">📂</div>
                            <h3 className="text-xl font-semibold text-white mb-2">No Transactions Found</h3>
                            <p className="text-slate-400 mb-6">Upload a bank statement to start reviewing.</p>
                            <Link href="/ingest">
                                <Button variant="outline">Go to Upload</Button>
                            </Link>
                        </div>
                    ) : !isComplete && currentTransaction ? (
                        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
                            {/* Transaction Header */}
                            <div className="flex items-center justify-between">
                                <div className="text-slate-400 text-sm font-medium">
                                    Item {currentIndex + 1} of {displayTransactions.length}
                                </div>
                                <div className="flex items-center gap-2">
                                    <span className="text-xs text-slate-500">AI Confidence:</span>
                                    <span
                                        className={cn(
                                            "text-sm font-semibold",
                                            currentTransaction.aiConfidence >= 80
                                                ? "text-emerald-400"
                                                : currentTransaction.aiConfidence >= 60
                                                    ? "text-amber-400"
                                                    : "text-red-400"
                                        )}
                                    >
                                        {currentTransaction.aiConfidence}%
                                    </span>
                                </div>
                            </div>

                            {/* Transaction Details */}
                            <div className="text-center py-8 border-l-4 border-emerald-500/30 pl-6 bg-slate-800/30 rounded-r-xl">
                                <div className="text-sm text-slate-400 mb-2">
                                    {currentTransaction.date}
                                </div>
                                <div className="text-5xl font-mono font-bold text-emerald-400 mb-2">
                                    ₹{currentTransaction.amount.toLocaleString("en-IN")}
                                </div>
                                <div className="text-slate-300 font-mono text-sm tracking-wide bg-slate-950/50 py-2 px-4 rounded-lg inline-block">
                                    {currentTransaction.description}
                                </div>
                                <div className="mt-4 text-sm text-slate-400">
                                    AI Recommendation:{" "}
                                    <span className="text-white font-semibold capitalize underline decoration-emerald-500/50 decoration-2">
                                        {currentTransaction.aiSuggestion}
                                    </span>
                                </div>
                            </div>

                            {/* Classification Buttons */}
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                                {(["business", "personal", "gift", "unsure"] as const).map(
                                    (category) => {
                                        const config = CATEGORY_CONFIG[category];
                                        const Icon = config.icon;
                                        const isAiPick =
                                            category === currentTransaction.aiSuggestion;

                                        return (
                                            <button
                                                key={category}
                                                onClick={() => classify(category)}
                                                className={cn(
                                                    "relative flex flex-col items-center p-4 rounded-xl border-2 transition-all duration-200",
                                                    "hover:scale-[1.02] active:scale-95",
                                                    isAiPick ? config.activeColor : config.color
                                                )}
                                            >
                                                {isAiPick && (
                                                    <Badge
                                                        variant="ai"
                                                        className="absolute -top-2 -right-2 text-[10px] px-1.5 py-0.5"
                                                    >
                                                        AI Pick
                                                    </Badge>
                                                )}
                                                <Icon className="w-5 h-5 mb-2" />
                                                <span className="font-semibold text-xs">
                                                    {config.label}
                                                </span>
                                                <span className="text-[10px] text-slate-500 mt-0.5">
                                                    {config.subtitle}
                                                </span>
                                                <div className="mt-2 px-1.5 py-0.5 bg-slate-800 rounded text-[9px] font-mono text-slate-500 border border-slate-700">
                                                    {config.shortcut}
                                                </div>
                                            </button>
                                        );
                                    }
                                )}
                            </div>
                        </div>
                    ) : (
                        /* Completion State */
                        <div className="bg-slate-900 border border-emerald-500/30 rounded-xl p-8 text-center space-y-6">
                            <div className="text-6xl">✅</div>
                            <h2 className="text-2xl font-bold text-white">
                                {isDemo ? "All Transactions Classified!" : "Review Cycle Complete"}
                            </h2>

                            {/* Category Summary */}
                            <div className="flex flex-wrap items-center justify-center gap-3">
                                <Badge
                                    variant={counts.business > 0 ? "warning" : "outline"}
                                    className="px-3 py-1"
                                >
                                    {counts.business} Business
                                </Badge>
                                <Badge
                                    variant={counts.personal > 0 ? "info" : "outline"}
                                    className="px-3 py-1"
                                >
                                    {counts.personal} Personal
                                </Badge>
                                <Badge
                                    variant={counts.gift > 0 ? "destructive" : "outline"}
                                    className="px-3 py-1 bg-red-500/20 text-red-400 border-red-500/30"
                                >
                                    {counts.gift} Gift
                                </Badge>
                                <Badge variant="outline" className="px-3 py-1">
                                    {counts.unsure} Unsure
                                </Badge>
                            </div>

                            {/* Expandable Classifications */}
                            <button
                                onClick={() => setShowClassifications(!showClassifications)}
                                className="flex items-center gap-2 mx-auto text-sm text-slate-400 hover:text-white transition-colors"
                            >
                                <ChevronDown
                                    className={cn(
                                        "w-4 h-4 transition-transform",
                                        showClassifications && "rotate-180"
                                    )}
                                />
                                Summary details ({classifications.length})
                            </button>

                            {showClassifications && (
                                <div className="space-y-2 text-left max-w-md mx-auto">
                                    {classifications.map((c, idx) => {
                                        const tx = displayTransactions.find((t) => t.id === c.transactionId);
                                        return (
                                            <div
                                                key={idx}
                                                className="flex items-center justify-between bg-slate-800/50 rounded-lg px-4 py-2 text-xs border border-slate-700"
                                            >
                                                <span className="text-slate-300">
                                                    <span className="font-mono">₹{tx?.amount.toLocaleString("en-IN")}</span> —{" "}
                                                    <span className="capitalize">{c.category}</span>
                                                </span>
                                                <button
                                                    onClick={undoLast}
                                                    className="text-slate-500 hover:text-white"
                                                >
                                                    <Undo2 className="w-3 h-3" />
                                                </button>
                                            </div>
                                        );
                                    })}
                                </div>
                            )}

                            {/* Continue Button */}
                            <Link href={isDemo ? "/dashboard?demo=true" : "/dashboard"}>
                                <Button
                                    size="lg"
                                    className="px-10 py-6 text-lg bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl shadow-lg shadow-emerald-900/30 transition-all hover:scale-105"
                                >
                                    {isDemo ? "Continue to Dashboard" : "Finalize Audit Results"}
                                    <ArrowRight className="ml-2 h-5 w-5" />
                                </Button>
                            </Link>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
}

import { useSearchParams } from "next/navigation";

export default function ReviewPage() {
    return (
        <Suspense fallback={<div className="min-h-screen bg-slate-950 flex items-center justify-center text-white">Loading...</div>}>
            <ReviewContent />
        </Suspense>
    );
}

