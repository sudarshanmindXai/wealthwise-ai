"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";
import { DemoBanner } from "@/components/DemoBanner";
import {
    LayoutDashboard,
    Briefcase,
    Wrench,
    BarChart3,
    FileText,
    MessageCircle,
    Shield,
    Zap,
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

function DashboardContent() {
    const searchParams = useSearchParams();
    const isDemo = searchParams.get("demo") === "true";
    const [activeNav, setActiveNav] = useState("overview");
    const [rentPaid, setRentPaid] = useState(20000);

    // Tax Calculation Logic
    const GROSS_INCOME = 2580000; // ₹25.8L total
    const STANDARD_DEDUCTION_OLD = 50000;
    const STANDARD_DEDUCTION_NEW = 75000;

    // Old Regime (with deductions)
    const hra_exemption = Math.min(rentPaid * 12 * 0.5, 120000);
    const other_deductions = 150000; // 80C, 80D etc
    const taxable_old = GROSS_INCOME - STANDARD_DEDUCTION_OLD - other_deductions - hra_exemption;
    const tax_old = calculateTaxOld(taxable_old);

    // New Regime (minimal deductions)
    const taxable_new = GROSS_INCOME - STANDARD_DEDUCTION_NEW;
    const tax_new = calculateTaxNew(taxable_new);

    const savings = tax_old - tax_new;
    const isNewBetter = savings > 0;
    const potentialSavings = 82800; // Fixed for demo

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

    const maxTax = Math.max(tax_old, tax_new);
    const oldBarHeight = (tax_old / maxTax) * 100;
    const newBarHeight = (tax_new / maxTax) * 100;

    return (
        <div className="min-h-screen bg-slate-950 flex">
            {/* Sidebar */}
            <aside className="w-56 border-r border-slate-800 bg-slate-900/50 flex flex-col">
                {/* Logo */}
                <div className="p-4 border-b border-slate-800">
                    <div className="flex items-center gap-2 font-bold text-lg">
                        <div className="h-8 w-8 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                            <Shield className="h-5 w-5 text-emerald-400" />
                        </div>
                        <span className="text-white">WealthWise AI</span>
                    </div>
                </div>

                {/* Navigation */}
                <nav className="flex-1 p-3 space-y-1">
                    {NAV_ITEMS.map((item) => {
                        const Icon = item.icon;
                        const isActive = activeNav === item.id;

                        return (
                            <button
                                key={item.id}
                                onClick={() => setActiveNav(item.id)}
                                className={cn(
                                    "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                                    isActive
                                        ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                                        : "text-slate-400 hover:text-white hover:bg-slate-800"
                                )}
                            >
                                <Icon className="h-4 w-4" />
                                {item.label}
                            </button>
                        );
                    })}
                </nav>
            </aside>

            {/* Main Content */}
            <div className="flex-1 flex flex-col">
                {/* Demo Banner */}
                {isDemo && <DemoBanner isDemo={isDemo} />}

                {/* Header */}
                <header className="border-b border-slate-800 bg-slate-950 px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex flex-col gap-1">
                            {isDemo && (
                                <div className="flex items-center gap-2 mb-1">
                                    <Badge variant="outline" className="text-[10px] h-5 border-emerald-500/30 text-emerald-400 px-1.5 uppercase tracking-wider">Step 5 of 5</Badge>
                                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Optimization Cockpit</span>
                                </div>
                            )}
                            <h1 className="text-2xl font-bold text-white">
                                {isDemo ? "Tax Optimization Dashboard" : "Investment & Tax Cockpit"}
                            </h1>
                            <p className="text-sm text-slate-400">
                                FY 2025-26 • Last updated just now
                            </p>
                        </div>
                        <div className="text-right">
                            <div className="text-sm text-slate-400">Potential Savings</div>
                            <div className="text-3xl font-mono font-bold text-emerald-400">
                                ₹{potentialSavings.toLocaleString("en-IN")}
                            </div>
                        </div>
                    </div>
                </header>

                {/* Dashboard Content */}
                <main className="flex-1 p-6 space-y-6 overflow-auto">
                    {/* Guidance Card for Demo */}
                    {isDemo && (
                        <div className="bg-emerald-500/5 border border-emerald-500/20 rounded-xl p-4 flex items-center justify-between">
                            <div className="flex items-center gap-4">
                                <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center animate-pulse">
                                    <Zap className="h-5 w-5 text-emerald-400" />
                                </div>
                                <div>
                                    <h3 className="text-sm font-semibold text-white">Demo Mission: Find Your Zero</h3>
                                    <p className="text-xs text-slate-400">Use the <span className="text-emerald-400 font-bold">Rent Optimizer</span> below to find the exact rent amount that makes the Old Regime better than the New Regime.</p>
                                </div>
                            </div>
                            <Button size="sm" variant="ghost" className="text-xs text-slate-500 hover:text-white">Dismiss Guide</Button>
                        </div>
                    )}

                    {/* Regime Showdown */}
                    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                        <h2 className="text-lg font-semibold text-white mb-6">
                            Regime Showdown
                        </h2>

                        <div className="grid grid-cols-2 gap-6">
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
                                    ₹{Math.abs(Math.round(savings)).toLocaleString("en-IN")}
                                </span>
                            </span>
                        </div>
                    </div>

                    {/* Rent Optimizer */}
                    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                        <div className="flex items-center gap-3 mb-4">
                            <span className="text-2xl">🏠</span>
                            <div>
                                <h2 className="text-lg font-semibold text-white">
                                    Rent Optimizer (HRA Impact)
                                </h2>
                                <p className="text-sm text-slate-400">
                                    Drag the slider to see how rent affects your Old Regime tax.
                                </p>
                            </div>
                        </div>

                        {/* Slider */}
                        <div className="space-y-4">
                            <div className="flex items-center justify-between text-sm">
                                <span className="text-slate-400">₹0</span>
                                <span className="text-emerald-400 font-mono font-semibold">
                                    ₹{rentPaid.toLocaleString("en-IN")}/month
                                </span>
                                <span className="text-slate-400">₹50,000</span>
                            </div>
                            <Slider
                                value={[rentPaid]}
                                min={0}
                                max={50000}
                                step={1000}
                                onValueChange={(vals) => setRentPaid(vals[0])}
                                className="py-4"
                            />
                        </div>

                        {/* HRA Calculation Display */}
                        <div className="mt-4 bg-slate-800/50 rounded-lg p-4 font-mono text-sm space-y-1">
                            <div className="text-emerald-400">
                                <span className="text-slate-500">&gt;</span> HRA Exemption:{" "}
                                <span className="text-white">
                                    ₹{hra_exemption.toLocaleString("en-IN")}
                                </span>
                            </div>
                            <div className="text-emerald-400">
                                <span className="text-slate-500">&gt;</span> Old Regime Tax Updated:{" "}
                                <span className="text-white">
                                    ₹{Math.round(tax_old).toLocaleString("en-IN")}
                                </span>
                            </div>
                        </div>
                    </div>
                </main>

                {/* Floating Chat Button */}
                <button className="fixed bottom-6 right-6 w-14 h-14 bg-emerald-600 hover:bg-emerald-700 rounded-full shadow-lg shadow-emerald-900/50 flex items-center justify-center transition-transform hover:scale-110">
                    <MessageCircle className="w-6 h-6 text-white" />
                </button>
            </div>
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

