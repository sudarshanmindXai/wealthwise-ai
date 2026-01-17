"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";
import { DemoBanner } from "@/components/DemoBanner";
import ChatPanel from "@/components/ChatPanel";
import {
    LayoutDashboard,
    Briefcase,
    Wrench,
    BarChart3,
    FileText,
    Shield,
    Zap,
    Download,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
    { id: "overview", label: "Overview", icon: LayoutDashboard },
    { id: "salary", label: "Salary", icon: Briefcase },
    { id: "hustle", label: "Hustle", icon: Wrench },
    { id: "portfolio", label: "Portfolio", icon: BarChart3 },
    { id: "report", label: "Generate Report", icon: FileText },
];

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { fetchAnalysis, fetchReviewSummary, downloadForm12BB } from "@/lib/api";

function DashboardContent() {
    const searchParams = useSearchParams();
    const isDemo = searchParams.get("demo") === "true";
    const [activeNav, setActiveNav] = useState("overview");
    const [rentPaid, setRentPaid] = useState(20000);
    const [analysisData, setAnalysisData] = useState<AnalysisResponse | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [isDownloading, setIsDownloading] = useState(false);

    // Types
    interface Insight {
        title: string;
        description: string;
        impact_currency: number;
        confidence: number;
        category: "deduction" | "exemption" | "compliance" | "warning" | "info";
        action_item?: string;
    }

    interface AnalysisResponse {
        insights: Insight[];
        total_potential_savings: number;
    }

    // Fetch Analysis (Simulated Context)
    // State for Real Data
    const [incomeDetails, setIncomeDetails] = useState({
        salary: 1500000, // Fallback default
        business: 0,
        rent_paid: 20000 * 12,
        ltcg: 0,
        stcg: 0
    });

    // Fetch Analysis (Real Context)
    useEffect(() => {
        const loadDashboardData = async () => {
            setIsLoading(true);
            try {
                // 1. Get financial summary from Review step
                let summary = { salary: 1500000, business: 0, gift: 0, personal_expense: 0 };

                if (!isDemo) {
                    summary = await fetchReviewSummary();
                }

                // Update local state for sliders/calculations
                setIncomeDetails(prev => ({
                    ...prev,
                    salary: summary.salary || 1500000,
                    business: summary.business || 0,
                }));

                // 2. Run Analysis with this data
                const analysisReq = {
                    user_id: isDemo ? "demo_user" : "user_123",
                    income_details: {
                        salary: summary.salary || 1500000,
                        hra: 0, // We don't know HRA received yet, assume 0 or need input
                        rent_paid: rentPaid * 12,
                        business: summary.business,
                        ltcg: 0 // Todo: Fetch from capital gains parser
                    },
                    regime: "new"
                };

                const data = await fetchAnalysis(analysisReq);
                if (data) {
                    setAnalysisData(data);
                }
            } catch (err) {
                console.error("Failed to load dashboard", err);
            } finally {
                setIsLoading(false);
            }
        };

        loadDashboardData();
    }, [rentPaid, isDemo]);

    // Derived values
    // Tax Calculation Logic (Client-side fallback for sliders)
    const GROSS_INCOME = incomeDetails.salary + incomeDetails.business;
    const STANDARD_DEDUCTION_OLD = 50000;
    const STANDARD_DEDUCTION_NEW = 75000;

    // Old Regime (with deductions)
    const hra_exemption = Math.min(rentPaid * 12 * 0.5, 120000); // Simplistic HRA calc
    const other_deductions = 150000; // 80C, 80D etc
    const taxable_old = Math.max(0, GROSS_INCOME - STANDARD_DEDUCTION_OLD - other_deductions - hra_exemption);
    const tax_old = calculateTaxOld(taxable_old);

    // New Regime (minimal deductions)
    const taxable_new = Math.max(0, GROSS_INCOME - STANDARD_DEDUCTION_NEW);
    const tax_new = calculateTaxNew(taxable_new);

    const regimeSavings = Math.abs(tax_old - tax_new);
    const isNewBetter = tax_new < tax_old;

    // Insights Savings (from Guardian Analysis)
    const insightsSavings = analysisData?.total_potential_savings || 0;

    // Total Potential Savings = Regime Savings + Insights Savings
    // If New Regime is better (which is usually the baseline for our "Optimization"), we add on top.
    // If Old Regime is better, that's also a "saving" vs the alternative.
    const totalPotentialSavings = regimeSavings + insightsSavings;

    // Logic functions...
    function calculateTaxOld(income: number): number {
        if (income <= 250000) return 0;
        if (income <= 500000) return (income - 250000) * 0.05;
        if (income <= 1000000) return 12500 + (income - 500000) * 0.2;
        return 12500 + 100000 + (income - 1000000) * 0.3;
    }

    function calculateTaxNew(income: number): number {
        if (income <= 300000) return 0;
        if (income <= 700000) return (income - 300000) * 0.05;
        if (income <= 1000000) return 20000 + (income - 700000) * 0.1;
        if (income <= 1200000) return 20000 + 30000 + (income - 1000000) * 0.15;
        if (income <= 1500000) return 20000 + 30000 + 30000 + (income - 1200000) * 0.2;
        return 20000 + 30000 + 30000 + 60000 + (income - 1500000) * 0.3;
    }

    const maxTax = Math.max(tax_old, tax_new, 1); // Avoid div by zero
    const oldBarHeight = (tax_old / maxTax) * 100;
    const newBarHeight = (tax_new / maxTax) * 100;

    return (
        <div className="min-h-screen bg-slate-950 flex flex-col">
            {/* Demo Banner */}
            {isDemo && <DemoBanner isDemo={isDemo} />}

            {/* Header */}
            <header className="border-b border-slate-800 bg-slate-950 px-6 py-4">
                <div className="flex items-center justify-between max-w-6xl mx-auto">
                    <div className="flex items-center gap-6">
                        {/* Logo */}
                        <Link href="/" className="flex items-center gap-2 font-bold text-lg hover:opacity-80 transition-opacity">
                            <div className="h-8 w-8 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                                <Shield className="h-5 w-5 text-emerald-400" />
                            </div>
                            <span className="text-white">WealthWise AI</span>
                        </Link>

                        {/* Title */}
                        <div className="flex flex-col gap-0.5">
                            {isDemo && (
                                <div className="flex items-center gap-2">
                                    <Badge variant="outline" className="text-[10px] h-5 border-emerald-500/30 text-emerald-400 px-1.5 uppercase tracking-wider">Step 5 of 5</Badge>
                                </div>
                            )}
                            <h1 className="text-xl font-bold text-white">
                                {isDemo ? "Tax Optimization Dashboard" : "Investment & Tax Cockpit"}
                            </h1>
                        </div>
                    </div>
                    <div className="text-right">
                        <div className="text-sm text-slate-400">Total Savings Potential</div>
                        <div className="text-3xl font-mono font-bold text-emerald-400">
                            ₹{totalPotentialSavings.toLocaleString("en-IN")}
                        </div>
                    </div>
                </div>
            </header>

            {/* Dashboard Content */}
            <main className="flex-1 p-6 space-y-6 overflow-auto">
                <div className="max-w-6xl mx-auto space-y-8">

                    {/* Guidance Card for Demo */}
                    {isDemo && (
                        <div className="bg-emerald-500/5 border border-emerald-500/20 rounded-xl p-4 flex items-center justify-between">
                            <div className="flex items-center gap-4">
                                <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center animate-pulse">
                                    <Zap className="h-5 w-5 text-emerald-400" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-white">Analysis Complete</h3>
                                    <p className="text-sm text-slate-300">
                                        We analyzed your <strong>₹{(GROSS_INCOME / 100000).toFixed(1)}L income</strong>.
                                        The <strong>New Regime</strong> is your best bet, saving you <strong>₹{regimeSavings.toLocaleString("en-IN")}</strong> instantly.
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Regime Showdown */}
                    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                        <h2 className="text-lg font-semibold text-white mb-6">Regime Showdown</h2>
                        <div className="grid md:grid-cols-2 gap-12 items-end">
                            {/* Old Regime */}
                            <div className="space-y-4">
                                <div className="flex items-center justify-between">
                                    <span className="text-slate-300 font-medium">Old Regime</span>
                                </div>
                                <div className="relative h-48 bg-slate-800/50 rounded-lg overflow-hidden">
                                    <div
                                        className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-red-600 to-red-500 transition-all duration-500 rounded-t-lg"
                                        style={{ height: `${oldBarHeight}%` }}
                                    />
                                    <div className="absolute inset-0 flex items-end justify-center pb-4">
                                        <span className="text-2xl font-mono font-bold text-white drop-shadow-lg">
                                            ₹{Math.round(tax_old).toLocaleString("en-IN")}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            {/* New Regime */}
                            <div className="space-y-4">
                                <div className="flex items-center justify-between">
                                    <span className="text-slate-300 font-medium">New Regime</span>
                                    {isNewBetter && (
                                        <Badge variant="success" className="px-2 py-0.5">
                                            WINNER
                                        </Badge>
                                    )}
                                </div>
                                <div className="relative h-48 bg-slate-800/50 rounded-lg overflow-hidden">
                                    <div
                                        className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-emerald-600 to-emerald-500 transition-all duration-500 rounded-t-lg"
                                        style={{ height: `${newBarHeight}%` }}
                                    />
                                    <div className="absolute inset-0 flex items-end justify-center pb-4">
                                        <span className="text-2xl font-mono font-bold text-white drop-shadow-lg">
                                            ₹{Math.round(tax_new).toLocaleString("en-IN")}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Savings Summary */}
                        <div className="mt-6 text-center">
                            <span className="text-slate-300">
                                {isNewBetter ? "New Regime" : "Old Regime"} saves you{" "}
                                <span className="text-emerald-400 font-bold font-mono">
                                    ₹{Math.abs(Math.round(regimeSavings)).toLocaleString("en-IN")}
                                </span>
                            </span>
                        </div>
                    </div>

                    {/* Guardian Insights (NEW) */}
                    {analysisData?.insights && analysisData.insights.length > 0 && (
                        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                            <div className="flex items-center gap-2 mb-4">
                                <span className="text-2xl">🛡️</span>
                                <h2 className="text-lg font-semibold text-white">Guardian Intelligence</h2>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {analysisData.insights.map((insight, idx) => (
                                    <div key={idx} className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/50 hover:border-emerald-500/30 transition-colors">
                                        <div className="flex items-start justify-between mb-2">
                                            <Badge variant={insight.category === "warning" ? "destructive" : "outline"} className="capitalize">
                                                {insight.category}
                                            </Badge>
                                            {insight.impact_currency > 0 && (
                                                <Badge variant="success" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20">
                                                    Save ₹{Math.round(insight.impact_currency).toLocaleString("en-IN")}
                                                </Badge>
                                            )}
                                        </div>
                                        <h3 className="font-semibold text-white text-sm mb-1">{insight.title}</h3>
                                        <p className="text-xs text-slate-400 mb-3">{insight.description}</p>
                                        {insight.action_item && (
                                            <div className="text-xs text-emerald-400 font-medium flex items-center gap-1">
                                                <Zap className="w-3 h-3" />
                                                {insight.action_item}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Rent Optimizer */}
                    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                        <div className="flex items-center justify-between mb-6">
                            <div>
                                <h2 className="text-lg font-semibold text-white">Rent Optimizer</h2>
                                <p className="text-sm text-slate-400">Find the sweet spot for HRA</p>
                            </div>
                            <Badge variant="outline" className="border-emerald-500/30 text-emerald-400">
                                Current: ₹{(rentPaid).toLocaleString("en-IN")}/mo
                            </Badge>
                        </div>

                        <div className="space-y-6">
                            <Slider
                                value={[rentPaid]}
                                min={5000}
                                max={100000}
                                step={1000}
                                onValueChange={(vals) => setRentPaid(vals[0])}
                                className="py-4"
                            />
                            <div className="flex justify-between text-xs text-slate-500">
                                <span>₹5,000</span>
                                <span>₹50,000</span>
                                <span>₹1,00,000</span>
                            </div>

                            <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/50">
                                <div className="flex justify-between items-center mb-2">
                                    <span className="text-slate-300">Revised HRA Exemption</span>
                                    <span className="text-white font-mono font-bold">₹{Math.round(Math.min(rentPaid * 12 * 0.5, 120000)).toLocaleString("en-IN")}</span>
                                </div>
                                <p className="text-xs text-slate-400">
                                    Increasing rent to <span className="text-emerald-400">₹{(rentPaid + 5000).toLocaleString("en-IN")}</span> could save another ₹{Math.round(5000 * 12 * 0.3).toLocaleString("en-IN")} in taxes.
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                        <h2 className="text-lg font-semibold text-white mb-4">Generate Reports</h2>
                        <div className="flex flex-wrap gap-4">
                            <Button
                                size="lg"
                                className="bg-white text-slate-950 hover:bg-slate-200"
                                onClick={async () => {
                                    setIsDownloading(true);
                                    const form12BBData = {
                                        "user": {
                                            "name": "Tax Payer",
                                            "address": "Address not provided",
                                            "pan": "XXXXX0000X",
                                            "father_name": "Not Provided",
                                            "designation": "Employee",
                                            "financial_year": "2025-26"
                                        },
                                        "hra": { "rent_paid": rentPaid * 12, "landlord_name": "", "landlord_pan": "", "address": "" },
                                        "lta": 0,
                                        "home_loan_interest": { "amount": 0, "lender_name": "", "lender_pan": "" },
                                        "deductions_80c": [{ "description": "Total 80C", "amount": 150000 }],
                                        "deductions_points": { "80D": 25000, "80G": 0 }
                                    };
                                    await downloadForm12BB(form12BBData);
                                    setIsDownloading(false);
                                }}
                                disabled={isDownloading}
                            >
                                {isDownloading ? (
                                    <span className="flex items-center gap-2">
                                        <span className="animate-spin h-4 w-4 border-2 border-slate-900 border-t-transparent rounded-full" />
                                        Generating...
                                    </span>
                                ) : (
                                    <span className="flex items-center gap-2">
                                        <FileText className="w-4 h-4" /> Generate Form 12BB
                                    </span>
                                )}
                            </Button>

                            <Button
                                size="lg"
                                variant="secondary"
                                className="bg-emerald-600 text-white hover:bg-emerald-700"
                                onClick={async () => {
                                    setIsDownloading(true);
                                    try {
                                        const reportReq = {
                                            "user": {
                                                "name": isDemo ? "Demo User" : "Valued Client",
                                                "pan": "ABCDE1234F"
                                            },
                                            "analysis": {
                                                "gross_income": GROSS_INCOME,
                                                "taxable_income": isNewBetter ? taxable_new : taxable_old,
                                                "tax_old": tax_old,
                                                "tax_new": tax_new,
                                                "regime": isNewBetter ? "new" : "old",
                                                "savings": regimeSavings,
                                                "tax_payable": isNewBetter ? tax_new : tax_old
                                            },
                                            "insights": analysisData?.insights || []
                                        };
                                        await import("@/lib/api").then(mod => mod.downloadReport(reportReq));
                                    } catch (e) {
                                        console.error(e);
                                    }
                                    setIsDownloading(false);
                                }}
                                disabled={isDownloading}
                            >
                                {isDownloading ? (
                                    <span className="flex items-center gap-2">Generating...</span>
                                ) : (
                                    <span className="flex items-center gap-2">
                                        <Download className="w-4 h-4" /> Download Report
                                    </span>
                                )}
                            </Button>
                        </div>
                    </div>
                </div>
            </main>

            {/* Chat Panel */}
            <ChatPanel userContext={{
                gross_income: GROSS_INCOME,
                tax_old: tax_old,
                tax_new: tax_new,
                recommended: isNewBetter ? "New Regime" : "Old Regime",
                potential_savings: totalPotentialSavings
            }} />
        </div>
    );
}

export default function DashboardPage() {
    return (
        <Suspense fallback={<div className="min-h-screen bg-slate-950 flex items-center justify-center text-white">Loading...</div>}>
            <DashboardContent />
        </Suspense>
    );
}

