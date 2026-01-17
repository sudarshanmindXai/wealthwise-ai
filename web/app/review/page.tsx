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
    Loader2,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { saveReview } from "@/lib/api";

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

    // State
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [classifications, setClassifications] = useState<Classification[]>([]);

    // Clustering State
    const [clusters, setClusters] = useState<Cluster[]>([]);
    const [currentClusterIndex, setCurrentClusterIndex] = useState(0);
    const [viewMode, setViewMode] = useState<"cluster" | "individual" | "complete">("cluster");
    const [showClassifications, setShowClassifications] = useState(false);

    // Context Selection State
    const [userContext, setUserContext] = useState<{ isFreelancer: boolean; hasReceivedGifts: boolean } | null>(null);

    // Fetch transactions
    useEffect(() => {
        if (isDemo) {
            // Generate 300 demo transactions for stress testing "Cluster Mode"
            const generated = generateDemoTransactions();
            setTransactions(generated);
            setClusters(clusterTransactions(generated));
            return;
        }

        const fetchTransactions = async () => {
            setIsLoading(true);
            try {
                const res = await fetch("http://localhost:8000/api/v1/review/transactions");
                if (res.ok) {
                    const data = await res.json();
                    const mapped = data.map((t: any) => ({
                        ...t,
                        aiSuggestion: t.category,
                        aiConfidence: Math.round(t.confidence * 100)
                    }));
                    if (mapped.length === 0) {
                        // Don't auto-complete, let empty state render
                        setTransactions([]);
                        setClusters([]);
                        setIsLoading(false);
                    } else {
                        setTransactions(mapped);
                        setClusters(clusterTransactions(mapped));
                    }
                }
            } catch (err) {
                console.error("Failed to fetch transactions", err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchTransactions();
    }, [isDemo]);

    // Derived Logic
    const currentCluster = clusters[currentClusterIndex];
    const isClusterComplete = currentClusterIndex >= clusters.length;

    // Switch to complete mode when done
    useEffect(() => {
        if (transactions.length > 0 && classifications.length === transactions.length) {
            setViewMode("complete");
        } else if (isClusterComplete && transactions.length > 0) {
            setViewMode("complete");
        }
    }, [isClusterComplete, transactions.length, classifications.length]);

    const classifyCluster = (category: "business" | "personal" | "gift" | "unsure") => {
        if (!currentCluster) return;

        const newClassifications = currentCluster.transactions.map(t => ({
            transactionId: t.id,
            category
        }));

        setClassifications(prev => [...prev, ...newClassifications]);

        if (currentClusterIndex < clusters.length - 1) {
            setCurrentClusterIndex(prev => prev + 1);
        } else {
            setViewMode("complete");
        }
    };

    const undoLast = () => {
        if (currentClusterIndex > 0) {
            const prevCluster = clusters[currentClusterIndex - 1];
            // Remove classifications for this cluster
            const idsToRemove = new Set(prevCluster.transactions.map(t => t.id));
            setClassifications(prev => prev.filter(c => !idsToRemove.has(c.transactionId)));
            setCurrentClusterIndex(prev => prev - 1);
            setViewMode("cluster");
        }
    };

    const getCategoryCounts = () => {
        const counts = { business: 0, personal: 0, gift: 0, unsure: 0 };
        classifications.forEach((c) => counts[c.category]++);
        return counts;
    };

    const counts = getCategoryCounts();

    // Helper to format currency
    const fmt = (n: number) => "₹" + n.toLocaleString("en-IN");

    // Context Selector Component
    if (!userContext && viewMode !== "complete" && transactions.length > 0) {
        return (
            <div className="min-h-screen bg-slate-950 flex flex-col">
                <TunnelHeader title="Review Setup" step={3} totalSteps={5} backHref="/ingest" isDemo={isDemo} />
                <main className="flex-1 container py-8 px-4 flex items-center justify-center">
                    <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
                        <div className="text-center">
                            <h2 className="text-xl font-bold text-white mb-2">Help us categorize faster</h2>
                            <p className="text-slate-400 text-sm">Select all that apply to you this financial year.</p>
                        </div>

                        <div className="space-y-3">
                            <button
                                onClick={() => setUserContext(prev => ({ isFreelancer: !(prev?.isFreelancer), hasReceivedGifts: prev?.hasReceivedGifts || false }))} // Toggle logic handled in actual implementation below easier
                                className="hidden"
                            />
                            {/* Temporary simple implementation needed for replacing the block */}
                        </div>

                        <div className="grid gap-3">
                            <Button
                                variant="outline"
                                className="h-auto py-4 justify-start space-x-3 border-slate-700 hover:bg-slate-800 text-left"
                                onClick={() => setUserContext({ isFreelancer: false, hasReceivedGifts: false })}
                            >
                                <User className="w-5 h-5 text-emerald-500" />
                                <div>
                                    <div className="font-semibold text-white">Salaried Individual</div>
                                    <div className="text-xs text-slate-400">I only have salary and personal expenses</div>
                                </div>
                            </Button>

                            <Button
                                variant="outline"
                                className="h-auto py-4 justify-start space-x-3 border-slate-700 hover:bg-slate-800 text-left"
                                onClick={() => setUserContext({ isFreelancer: true, hasReceivedGifts: false })}
                            >
                                <Wrench className="w-5 h-5 text-orange-500" />
                                <div>
                                    <div className="font-semibold text-white">Freelancer / Business</div>
                                    <div className="text-xs text-slate-400">I have business income/expenses</div>
                                </div>
                            </Button>

                            <Button
                                variant="outline"
                                className="h-auto py-4 justify-start space-x-3 border-slate-700 hover:bg-slate-800 text-left"
                                onClick={() => setUserContext({ isFreelancer: true, hasReceivedGifts: true })}
                            >
                                <Gift className="w-5 h-5 text-red-500" />
                                <div>
                                    <div className="font-semibold text-white">Freelancer + Gifts</div>
                                    <div className="text-xs text-slate-400">I have business income and received gifts</div>
                                </div>
                            </Button>
                        </div>
                    </div>
                </main>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-950 flex flex-col">
            {isDemo && <DemoBanner />}

            <TunnelHeader
                title={viewMode === "complete"
                    ? "Classification Complete"
                    : viewMode === "cluster"
                        ? "Rapid Cluster Review"
                        : "Transaction Review"
                }
                step={viewMode === "complete" ? 4 : 3}
                totalSteps={5}
                backHref={isDemo ? "/ingest?demo=true" : "/ingest"}
                isDemo={isDemo}
            />

            <main className="flex-1 container py-8 px-4">
                <div className="max-w-3xl mx-auto space-y-6">

                    {/* Progress Bar for Clusters */}
                    {viewMode === "cluster" && clusters.length > 0 && (
                        <div className="space-y-2">
                            <div className="flex justify-between text-xs text-slate-400 font-medium">
                                <span>Batch {currentClusterIndex + 1} of {clusters.length}</span>
                                <span>{Math.round((currentClusterIndex / clusters.length) * 100)}% Complete</span>
                            </div>
                            <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden border border-slate-800">
                                <div
                                    className="h-full bg-emerald-500 transition-all duration-300 relative"
                                    style={{ width: `${((currentClusterIndex + 1) / clusters.length) * 100}%` }}
                                >
                                    <div className="absolute inset-0 bg-white/20 animate-[shimmer_2s_infinite]" />
                                </div>
                            </div>
                        </div>
                    )}

                    {viewMode === "cluster" && currentCluster ? (
                        <div className="space-y-6">
                            <div className="text-center">
                                <h2 className="text-3xl font-bold text-white mb-2">
                                    {currentCluster.name}
                                </h2>
                                <p className="text-slate-400">
                                    Found <span className="text-emerald-400 font-mono font-bold">{currentCluster.count}</span> similar transactions
                                    totaling <span className="text-white font-mono font-bold">{fmt(currentCluster.totalAmount)}</span>
                                </p>
                            </div>

                            {/* Sample Transactions in Cluster */}
                            <div className="bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden">
                                <div className="px-4 py-2 bg-slate-900 border-b border-slate-800 text-xs text-slate-500 uppercase tracking-wider">
                                    Examples from this cluster
                                </div>
                                <div className="divide-y divide-slate-800/50">
                                    {currentCluster.transactions.slice(0, 3).map(t => (
                                        <div key={t.id} className="flex justify-between p-4 text-sm">
                                            <span className="text-slate-300">{t.description}</span>
                                            <div className="text-right">
                                                <div className="font-mono text-white">{fmt(t.amount)}</div>
                                                <div className="text-xs text-slate-500">{t.date}</div>
                                            </div>
                                        </div>
                                    ))}
                                    {currentCluster.count > 3 && (
                                        <div className="p-3 text-center text-xs text-slate-500 italic">
                                            + {currentCluster.count - 3} more similar items
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Review Actions */}
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                                {(["business", "personal", "gift", "unsure"] as const).map((category) => {
                                    // Logic to hide categories based on userContext
                                    if (category === "business" && !userContext?.isFreelancer) return null;
                                    if (category === "gift" && !userContext?.hasReceivedGifts) return null;

                                    const config = CATEGORY_CONFIG[category];
                                    const Icon = config.icon;
                                    const isAiPick = category === currentCluster.commonCategory;

                                    return (
                                        <button
                                            key={category}
                                            onClick={() => classifyCluster(category)}
                                            className={cn(
                                                "relative flex flex-col items-center p-6 rounded-xl border-2 transition-all duration-200",
                                                "hover:scale-[1.02] active:scale-95",
                                                isAiPick ? config.activeColor : config.color
                                            )}
                                        >
                                            {isAiPick && (
                                                <Badge variant="ai" className="absolute -top-3 -right-2">
                                                    AI Pick ({currentCluster.confidence}%)
                                                </Badge>
                                            )}
                                            <Icon className="w-8 h-8 mb-3" />
                                            <span className="font-bold text-sm uppercase tracking-wide">
                                                {config.label}
                                            </span>
                                            <span className="text-xs opacity-70 mt-1">
                                                Apply to all {currentCluster.count}
                                            </span>
                                        </button>
                                    );
                                })}
                            </div>

                            <div className="flex justify-center mt-8">
                                <button
                                    onClick={undoLast}
                                    disabled={currentClusterIndex === 0}
                                    className="flex items-center gap-2 text-slate-500 hover:text-white disabled:opacity-30"
                                >
                                    <Undo2 className="w-4 h-4" />
                                    Undo previous cluster
                                </button>
                            </div>
                        </div>
                    ) : viewMode === "complete" ? (
                        /* Completion State */
                        <div className="bg-slate-900 border border-emerald-500/30 rounded-xl p-8 text-center space-y-6 animate-in fade-in zoom-in duration-500">
                            <div className="text-6xl">🎉</div>
                            <div>
                                <h2 className="text-2xl font-bold text-white mb-2">
                                    Review Complete!
                                </h2>
                                <p className="text-slate-400">
                                    You have classified <span className="text-white font-bold">{transactions.length} transactions</span>.
                                    <br />Your audit report is ready.
                                </p>
                            </div>

                            {/* Category Summary */}
                            <div className="flex flex-wrap items-center justify-center gap-3">
                                <Badge variant={counts.business > 0 ? "warning" : "outline"} className="px-3 py-1 text-lg">
                                    {counts.business} Business
                                </Badge>
                                <Badge variant={counts.personal > 0 ? "info" : "outline"} className="px-3 py-1 text-lg">
                                    {counts.personal} Personal
                                </Badge>
                                <Badge variant={counts.gift > 0 ? "destructive" : "outline"} className="px-3 py-1 text-lg bg-red-500/20 text-red-400 border-red-500/30">
                                    {counts.gift} Gift
                                </Badge>
                            </div>

                            <Button
                                size="lg"
                                onClick={async () => {
                                    if (!isDemo) {
                                        try {
                                            await saveReview(classifications);
                                        } catch (e) { /* error handled in api.ts */ }
                                    }
                                    window.location.href = isDemo ? "/dashboard?demo=true" : "/dashboard";
                                }}
                                className="w-full sm:w-auto px-12 py-6 text-lg bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl shadow-xl shadow-emerald-900/40 transition-all hover:scale-105 mt-4"
                            >
                                Generate Audit Report
                                <ArrowRight className="ml-2 h-5 w-5" />
                            </Button>

                        </div>
                    ) : transactions.length === 0 && !isLoading ? (
                        /* Empty State (No Transactions Found) */
                        <div className="text-center py-20 space-y-6">
                            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-slate-800/50 mb-4">
                                <HelpCircle className="w-10 h-10 text-slate-500" />
                            </div>
                            <div>
                                <h2 className="text-xl font-bold text-white mb-2">No Transactions Found</h2>
                                <p className="text-slate-400 max-w-sm mx-auto">
                                    We couldn't find any transactions to review. This usually means no bank statement was uploaded or the session expired.
                                </p>
                            </div>
                            <div className="flex flex-col sm:flex-row gap-4 justify-center">
                                <Button variant="outline" onClick={() => window.location.href = "/ingest"}>
                                    <Undo2 className="mr-2 h-4 w-4" /> Go Back to Upload
                                </Button>
                                <Button onClick={() => window.location.href = "/review?demo=true"}>
                                    Try Demo Mode
                                </Button>
                            </div>
                        </div>
                    ) : (
                        <div className="text-center py-20">
                            <Loader2 className="w-10 h-10 animate-spin text-emerald-500 mx-auto mb-4" />
                            <p className="text-slate-400">Analyzing patterns...</p>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
}

// --- Helper Functions and Types below ---

interface Cluster {
    id: string;
    name: string;
    transactions: Transaction[];
    count: number;
    totalAmount: number;
    commonCategory: "business" | "personal" | "gift" | "unsure";
    confidence: number;
}

function clusterTransactions(transactions: Transaction[]): Cluster[] {
    const groups: Record<string, Transaction[]> = {};

    // 1. Group by description (normalized)
    transactions.forEach(t => {
        // Normalize: "UBER INDIA RIDE" -> "UBER", "SWIGGY 1234" -> "SWIGGY"
        // Simple heuristic: First 2 words, uppercase, remove numbers
        const cleanDesc = t.description
            .replace(/[0-9]/g, '')
            .replace(/[-_]/g, ' ')
            .trim()
            .toUpperCase()
            .split(' ')
            .slice(0, 2) // Take first 2 words
            .join(' ');

        if (!groups[cleanDesc]) groups[cleanDesc] = [];
        groups[cleanDesc].push(t);
    });

    // 2. Convert to Array and Sort by Count (High impact first)
    return Object.entries(groups)
        .map(([name, txs], idx) => {
            // Calculate common category (mode)
            const catCounts: Record<string, number> = {};
            txs.forEach(t => {
                catCounts[t.aiSuggestion] = (catCounts[t.aiSuggestion] || 0) + 1;
            });
            const commonCategory = Object.entries(catCounts)
                .sort((a, b) => b[1] - a[1])[0][0] as any;

            // Average confidence
            const avgConf = Math.round(txs.reduce((sum, t) => sum + t.aiConfidence, 0) / txs.length);

            return {
                id: `cluster-${idx}`,
                name: name || "MISC TRANSACTIONS",
                transactions: txs,
                count: txs.length,
                totalAmount: txs.reduce((sum, t) => sum + t.amount, 0),
                commonCategory,
                confidence: avgConf
            };
        })
        .sort((a, b) => b.count - a.count); // Sort by biggest clusters first
}

function generateDemoTransactions(): Transaction[] {
    const patterns = [
        { desc: "UBER RIDE", cat: "personal", amount: [200, 800] },
        { desc: "ZOMATO ORDER", cat: "personal", amount: [300, 1500] },
        { desc: "AWS SERVICES", cat: "business", amount: [5000, 12000] },
        { desc: "WEWORK INDIA", cat: "business", amount: [15000, 15000] },
        { desc: "STARBUCKS", cat: "personal", amount: [400, 900] },
        { desc: "UPWORK PAYOUT", cat: "business", amount: [40000, 80000] },
        { desc: "CREDIT CARD BILL", cat: "personal", amount: [20000, 50000] },
        { desc: "UPI TRANSFER", cat: "unsure", amount: [500, 5000] },
    ];

    const txs: Transaction[] = [];
    for (let i = 0; i < 300; i++) {
        const p = patterns[Math.floor(Math.random() * patterns.length)];
        txs.push({
            id: i + 1,
            date: "2025-03-15",
            description: `${p.desc} #${Math.floor(Math.random() * 1000)}`,
            amount: Math.floor(Math.random() * (p.amount[1] - p.amount[0]) + p.amount[0]),
            aiSuggestion: p.cat as any,
            aiConfidence: Math.floor(Math.random() * 20) + 80 // 80-99%
        });
    }
    return txs;
}

import { useSearchParams } from "next/navigation";

export default function ReviewPage() {
    return (
        <Suspense fallback={<div className="min-h-screen bg-slate-950 flex items-center justify-center text-white">Loading...</div>}>
            <ReviewContent />
        </Suspense>
    );
}

