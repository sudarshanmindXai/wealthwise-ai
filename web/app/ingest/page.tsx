"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { DemoBanner } from "@/components/DemoBanner";
import { TunnelHeader } from "@/components/TunnelHeader";
import {
    Briefcase,
    Wrench,
    BarChart3,
    AlertTriangle,
    CheckCircle2,
    ArrowRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface DocumentData {
    id: string;
    title: string;
    subtitle: string;
    icon: React.ElementType;
    iconColor: string;
    status: "loading" | "loaded";
    fields: { label: string; value: string; highlight?: boolean }[];
    warning?: string;
}

const DEMO_DOCUMENTS: DocumentData[] = [
    {
        id: "salary",
        title: "Salary Documents",
        subtitle: "Form 16 Part B from your employer",
        icon: Briefcase,
        iconColor: "text-blue-400",
        status: "loaded",
        fields: [
            { label: "Gross Salary", value: "₹18,50,000" },
            { label: "Basic", value: "₹9,25,000" },
            { label: "HRA", value: "₹3,70,000" },
            { label: "TDS", value: "₹1,85,000" },
        ],
    },
    {
        id: "bank",
        title: "Bank Statement",
        subtitle: "Primary account statement (PDF or CSV)",
        icon: Wrench,
        iconColor: "text-orange-400",
        status: "loaded",
        fields: [
            { label: "Total Credits", value: "₹14,00,000" },
            { label: "Business Income", value: "₹12,00,000" },
            { label: "Ambiguous", value: "5", highlight: true },
            { label: "Personal", value: "₹1,50,000" },
        ],
        warning: "5 transactions need your review",
    },
    {
        id: "portfolio",
        title: "Portfolio P&L",
        subtitle: "Zerodha, Groww, or CoinDCX report",
        icon: BarChart3,
        iconColor: "text-purple-400",
        status: "loaded",
        fields: [
            { label: "LTCG", value: "₹80,000" },
            { label: "STCG", value: "₹45,000" },
            { label: "Crypto Gains", value: "₹50,000" },
            { label: "Crypto Losses", value: "₹20,000" },
        ],
    },
];

import { Suspense } from "react";
import { Upload, FileUp, ShieldCheck } from "lucide-react";

function IngestContent() {
    const searchParams = useSearchParams();
    const isDemo = searchParams.get("demo") === "true";
    const [documents, setDocuments] = useState<DocumentData[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [uploadedFiles, setUploadedFiles] = useState<Record<string, File | null>>({
        salary: null,
        bank: null,
        portfolio: null,
    });

    useEffect(() => {
        if (isDemo) {
            // Simulate loading documents one by one
            const loadDocs = async () => {
                for (let i = 0; i < DEMO_DOCUMENTS.length; i++) {
                    await new Promise((resolve) => setTimeout(resolve, 600));
                    setDocuments((prev) => [...prev, DEMO_DOCUMENTS[i]]);
                }
                setIsLoading(false);
            };
            loadDocs();
        } else {
            setDocuments([]); // Start empty for real mode
            setIsLoading(false);
        }
    }, [isDemo]);

    const handleFileUpload = (id: string, file: File) => {
        setUploadedFiles(prev => ({ ...prev, [id]: file }));
    };

    const allLoaded = isDemo
        ? (documents.length === DEMO_DOCUMENTS.length && !isLoading)
        : (uploadedFiles.salary && uploadedFiles.bank && uploadedFiles.portfolio);

    return (
        <div className="min-h-screen bg-slate-950 flex flex-col">
            {/* Demo Banner */}
            {isDemo && <DemoBanner isDemo={isDemo} />}

            {/* Tunnel Header */}
            <TunnelHeader
                title={isDemo ? "Document Collection Hub" : "Secure Document Ingress"}
                step={2}
                totalSteps={5}
                backHref={isDemo ? "/demo" : "/"}
                isDemo={isDemo}
            />

            {/* Main Content */}
            <main className="flex-1 container py-8 px-4">
                <div className="max-w-4xl mx-auto space-y-6">
                    {/* Info Card */}
                    <div className={cn(
                        "border rounded-xl p-5 transition-all duration-300",
                        isDemo ? "bg-slate-900 border-slate-800" : "bg-emerald-500/5 border-emerald-500/20"
                    )}>
                        <div className="flex items-start gap-4">
                            <div className={cn(
                                "w-10 h-10 rounded-lg flex items-center justify-center",
                                isDemo ? "bg-purple-500/20" : "bg-emerald-500/20"
                            )}>
                                {isDemo ? <BarChart3 className="w-5 h-5 text-purple-400" /> : <ShieldCheck className="w-5 h-5 text-emerald-400" />}
                            </div>
                            <div>
                                <h2 className="text-lg font-semibold text-white mb-1">
                                    {isDemo ? "Demo Mode: Auto-Filling Documents" : "Audit Setup: Upload Original Documents"}
                                </h2>
                                <p className="text-slate-400 text-sm">
                                    {isDemo
                                        ? <>We're loading sample documents for <span className="text-amber-400 underline">Rohan Sharma</span>.</>
                                        : "Upload your official financial statements. All processing happens locally in your browser/device for maximum privacy."
                                    }
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Document Cards Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {DEMO_DOCUMENTS.map((doc, index) => {
                            const isLoaded = isDemo ? documents.find((d) => d.id === doc.id) : !!uploadedFiles[doc.id];
                            const Icon = doc.icon;
                            const file = uploadedFiles[doc.id];

                            return (
                                <div
                                    key={doc.id}
                                    className={cn(
                                        "bg-slate-900 border rounded-xl px-5 py-6 transition-all duration-300",
                                        isLoaded
                                            ? "border-emerald-500/50 bg-emerald-500/5"
                                            : "border-slate-800 opacity-100"
                                    )}
                                >
                                    {/* Header */}
                                    <div className="flex items-start justify-between mb-4">
                                        <div className="flex items-center gap-3">
                                            <div className={cn("w-10 h-10 rounded-lg flex items-center justify-center",
                                                doc.id === "salary" ? "bg-blue-500/20" :
                                                    doc.id === "bank" ? "bg-orange-500/20" : "bg-purple-500/20"
                                            )}>
                                                <Icon className={cn("w-5 h-5", doc.iconColor)} />
                                            </div>
                                            <div>
                                                <div className="flex items-center gap-2">
                                                    <h3 className="font-semibold text-white text-sm">
                                                        {doc.title}
                                                    </h3>
                                                    <span className="text-red-400 text-sm">*</span>
                                                </div>
                                                <p className="text-xs text-slate-500">{doc.subtitle}</p>
                                            </div>
                                        </div>
                                        {isLoaded && isDemo && (
                                            <Badge variant="success" className="text-xs">
                                                <CheckCircle2 className="w-3 h-3 mr-1" />
                                                Loaded
                                            </Badge>
                                        )}
                                    </div>

                                    {/* Interactive Dropzone for Real Mode */}
                                    {!isDemo && !isLoaded ? (
                                        <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-slate-800 rounded-lg hover:border-emerald-500/40 hover:bg-emerald-500/5 cursor-pointer group transition-all">
                                            <div className="flex flex-col items-center justify-center pt-5 pb-6">
                                                <Upload className="w-6 h-6 text-slate-500 group-hover:text-emerald-400 mb-2" />
                                                <p className="text-xs text-slate-500 group-hover:text-slate-400">
                                                    Click or drag to upload
                                                </p>
                                            </div>
                                            <input
                                                type="file"
                                                className="hidden"
                                                onChange={(e) => {
                                                    const f = e.target.files?.[0];
                                                    if (f) handleFileUpload(doc.id, f);
                                                }}
                                            />
                                        </label>
                                    ) : !isDemo && isLoaded ? (
                                        <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-3 flex items-center justify-between">
                                            <div className="flex items-center gap-2 overflow-hidden">
                                                <FileUp className="w-4 h-4 text-emerald-400 shrink-0" />
                                                <span className="text-xs text-emerald-400 font-medium truncate">
                                                    {file?.name}
                                                </span>
                                            </div>
                                            <button
                                                onClick={() => setUploadedFiles(prev => ({ ...prev, [doc.id]: null }))}
                                                className="text-[10px] text-emerald-400/60 hover:text-emerald-400 underline"
                                            >
                                                Change
                                            </button>
                                        </div>
                                    ) : null}

                                    {/* Fields Grid for Demo Mode */}
                                    {isLoaded && isDemo && (
                                        <div className="grid grid-cols-2 gap-3 mb-3">
                                            {doc.fields.map((field, idx) => (
                                                <div key={idx} className="bg-slate-800/50 rounded-lg px-3 py-2">
                                                    <div className="text-xs text-slate-500 mb-0.5">
                                                        {field.label}
                                                    </div>
                                                    <div
                                                        className={cn(
                                                            "font-mono font-semibold text-sm",
                                                            field.highlight
                                                                ? "text-amber-400"
                                                                : "text-white"
                                                        )}
                                                    >
                                                        {field.value}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    {/* Warning for Demo Mode */}
                                    {isLoaded && isDemo && doc.warning && (
                                        <div className="flex items-center gap-2 bg-amber-500/10 border border-amber-500/20 rounded-lg px-3 py-2 text-amber-400 text-sm">
                                            <AlertTriangle className="w-4 h-4" />
                                            {doc.warning}
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>

                    {/* Footer */}
                    <div className="flex items-center justify-between pt-4">
                        <div className="flex items-center gap-2 text-sm">
                            {allLoaded ? (
                                <>
                                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                                    <span className="text-emerald-400">
                                        {isDemo ? "All required documents ready" : "All files securely staged"}
                                    </span>
                                </>
                            ) : (
                                <span className="text-slate-400">
                                    {isDemo ? "Loading documents..." : "Please upload all 3 required files"}
                                </span>
                            )}
                        </div>

                        <Link href={allLoaded ? (isDemo ? "/review?demo=true" : "/review") : "#"}>
                            <Button
                                size="lg"
                                disabled={!allLoaded}
                                className={cn(
                                    "px-8 rounded-xl shadow-lg transition-all hover:scale-105 disabled:opacity-50 disabled:hover:scale-100",
                                    allLoaded ? "bg-emerald-600 hover:bg-emerald-700 text-white shadow-emerald-900/30" : "bg-slate-800 text-slate-500"
                                )}
                            >
                                {isDemo ? "Review Transactions" : "Analyze My Data"}
                                <ArrowRight className="ml-2 h-5 w-5" />
                            </Button>
                        </Link>
                    </div>
                </div>
            </main>
        </div>
    );
}

export default function IngestPage() {
    return (
        <Suspense fallback={<div className="min-h-screen bg-slate-950 flex items-center justify-center text-white">Loading...</div>}>
            <IngestContent />
        </Suspense>
    );
}


