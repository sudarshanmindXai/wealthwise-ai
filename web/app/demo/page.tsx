"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { DemoBanner } from "@/components/DemoBanner";
import { TunnelHeader } from "@/components/TunnelHeader";
import { Check, Briefcase, Wrench, BarChart3, Gift, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface IncomeSource {
    id: string;
    title: string;
    subtitle: string;
    icon: React.ElementType;
    color: string;
    borderColor: string;
    bgColor: string;
}

const INCOME_SOURCES: IncomeSource[] = [
    {
        id: "salary",
        title: "Salaried Job",
        subtitle: "Form 16, HRA, NPS, LTA optimizations",
        icon: Briefcase,
        color: "text-blue-400",
        borderColor: "border-blue-500/50",
        bgColor: "bg-blue-500/10",
    },
    {
        id: "freelance",
        title: "Freelancing / Gig Work",
        subtitle: "Sec 44ADA, Bank statement classification",
        icon: Wrench,
        color: "text-orange-400",
        borderColor: "border-orange-500/50",
        bgColor: "bg-orange-500/10",
    },
    {
        id: "stocks",
        title: "Stocks & Crypto",
        subtitle: "LTCG harvesting, 115BBH compliance",
        icon: BarChart3,
        color: "text-purple-400",
        borderColor: "border-purple-500/50",
        bgColor: "bg-purple-500/10",
    },
    {
        id: "rent",
        title: "Rent / Gifts",
        subtitle: "Rental income, Gift taxation",
        icon: Gift,
        color: "text-teal-400",
        borderColor: "border-teal-500/50",
        bgColor: "bg-teal-500/10",
    },
];

export default function DemoPage() {
    const router = useRouter();
    const [selectedSources, setSelectedSources] = useState<string[]>([
        "salary",
        "freelance",
        "stocks",
    ]);

    const toggleSource = (id: string) => {
        setSelectedSources((prev) =>
            prev.includes(id)
                ? prev.filter((s) => s !== id)
                : [...prev, id]
        );
    };

    const handleContinue = () => {
        router.push("/ingest?demo=true");
    };

    return (
        <div className="min-h-screen bg-slate-950 flex flex-col">
            {/* Demo Banner */}
            <DemoBanner isDemo={true} />

            {/* Tunnel Header */}
            <TunnelHeader
                title="Identify Income Sources"
                step={1}
                totalSteps={5}
                backHref="/"
                isDemo={true}
            />

            {/* Main Content */}
            <main className="flex-1 flex flex-col items-center justify-center px-4 py-12">
                <div className="max-w-3xl w-full space-y-8">
                    {/* Heading */}
                    <div className="text-center space-y-3">
                        <h1 className="text-4xl font-bold text-white tracking-tight">
                            What defines your financial year?
                        </h1>
                        <p className="text-slate-400 text-lg">
                            We've pre-selected Rohan's income sources. You can adjust if you'd like.
                        </p>
                    </div>

                    {/* Income Source Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {INCOME_SOURCES.map((source) => {
                            const isSelected = selectedSources.includes(source.id);
                            const Icon = source.icon;

                            return (
                                <button
                                    key={source.id}
                                    onClick={() => toggleSource(source.id)}
                                    className={cn(
                                        "relative p-5 rounded-xl border-2 text-left transition-all duration-200",
                                        "hover:scale-[1.02] active:scale-[0.98]",
                                        isSelected
                                            ? `${source.borderColor} ${source.bgColor}`
                                            : "border-slate-800 bg-slate-900/50 hover:border-slate-700"
                                    )}
                                >
                                    <div className="flex items-start gap-4">
                                        <div
                                            className={cn(
                                                "w-10 h-10 rounded-lg flex items-center justify-center",
                                                isSelected ? source.bgColor : "bg-slate-800"
                                            )}
                                        >
                                            <Icon
                                                className={cn(
                                                    "w-5 h-5",
                                                    isSelected ? source.color : "text-slate-400"
                                                )}
                                            />
                                        </div>
                                        <div className="flex-1">
                                            <h3 className="font-semibold text-white mb-1">
                                                {source.title}
                                            </h3>
                                            <p className="text-sm text-slate-400">
                                                {source.subtitle}
                                            </p>
                                        </div>
                                        {isSelected && (
                                            <div className={cn("w-6 h-6 rounded-full flex items-center justify-center", source.bgColor)}>
                                                <Check className={cn("w-4 h-4", source.color)} />
                                            </div>
                                        )}
                                    </div>
                                </button>
                            );
                        })}
                    </div>

                    {/* Demo Profile Panel */}
                    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 font-mono text-sm">
                        <div className="text-emerald-400">
                            <span className="text-slate-500">&gt;</span> Demo Profile:{" "}
                            <span className="text-amber-400">Rohan Sharma</span>
                        </div>
                        <div className="text-emerald-400">
                            <span className="text-slate-500">&gt;</span> Income:{" "}
                            <span className="text-white">₹18.5L Salary</span> +{" "}
                            <span className="text-white">₹6L Freelance</span> +{" "}
                            <span className="text-white">₹1.3L Stocks</span>
                        </div>
                        <div className="text-emerald-400">
                            <span className="text-slate-500">&gt;</span> Documents will be pre-filled for you...
                        </div>
                    </div>

                    {/* Continue Button */}
                    <div className="flex justify-center">
                        <Button
                            onClick={handleContinue}
                            size="lg"
                            className="px-10 py-6 text-lg bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl shadow-lg shadow-emerald-900/30 transition-all hover:scale-105"
                        >
                            Continue Demo
                            <ArrowRight className="ml-2 h-5 w-5" />
                        </Button>
                    </div>
                </div>
            </main>
        </div>
    );
}
