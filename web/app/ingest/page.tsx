"use client";

import { useState, useEffect, useCallback, useRef } from "react";
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
    TrendingUp,
    FileText,
    AlertTriangle,
    CheckCircle2,
    ArrowRight,
    Upload,
    FileUp,
    ShieldCheck,
    X,
    Loader2,
    ChevronDown,
    ChevronUp,
    Plus,
    AlertCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Suspense } from "react";

// Types
interface UploadedFile {
    id: string;
    file: File;
    status: "pending" | "uploading" | "processing" | "success" | "error" | "needs_review";
    progress: number;
    detectedType?: string;
    typeDescription?: string;
    confidence?: number;
    extractedData?: Record<string, any>;
    taxFacts?: Record<string, any>;
    warnings?: string[];
    error?: string;
}

interface CategoryConfig {
    id: string;
    title: string;
    subtitle: string;
    description: string;
    icon: React.ElementType;
    iconColor: string;
    bgColor: string;
    acceptedTypes: string[];
    required: boolean;
}

const CATEGORIES: CategoryConfig[] = [
    {
        id: "salary",
        title: "Salary Documents",
        subtitle: "Form 16, Salary Slips",
        description: "Upload Form 16 Part B and salary slips from all employers",
        icon: Briefcase,
        iconColor: "text-blue-400",
        bgColor: "bg-blue-500/20",
        acceptedTypes: [".pdf"],
        required: true,
    },
    {
        id: "bank",
        title: "Bank Statements",
        subtitle: "PDF, CSV, or XLSX",
        description: "Upload statements from all bank accounts to detect income sources",
        icon: Wrench,
        iconColor: "text-orange-400",
        bgColor: "bg-orange-500/20",
        acceptedTypes: [".pdf", ".csv", ".xlsx", ".xls"],
        required: true,
    },
    {
        id: "portfolio",
        title: "Portfolio P&L",
        subtitle: "Zerodha, Groww, etc.",
        description: "Upload trading P&L statements to calculate capital gains",
        icon: BarChart3,
        iconColor: "text-purple-400",
        bgColor: "bg-purple-500/20",
        acceptedTypes: [".xlsx", ".csv", ".pdf"],
        required: true,
    },
    {
        id: "investments",
        title: "Investment Receipts",
        subtitle: "ELSS, PPF, NPS, LIC",
        description: "Upload investment proofs for 80C/80CCD deductions",
        icon: TrendingUp,
        iconColor: "text-emerald-400",
        bgColor: "bg-emerald-500/20",
        acceptedTypes: [".pdf"],
        required: false,
    },
    {
        id: "other",
        title: "Other Documents",
        subtitle: "Rent, Medical, etc.",
        description: "Rental agreements, medical insurance receipts, education loans",
        icon: FileText,
        iconColor: "text-slate-400",
        bgColor: "bg-slate-500/20",
        acceptedTypes: [".pdf", ".csv", ".xlsx"],
        required: false,
    },
];

// Demo data for demo mode
const DEMO_FILES: Record<string, UploadedFile[]> = {
    salary: [
        {
            id: "demo-1",
            file: new File([], "form16_rohan.pdf"),
            status: "success",
            progress: 100,
            detectedType: "form16",
            typeDescription: "Form 16 - TDS Certificate from Employer",
            confidence: 0.95,
            extractedData: {
                gross_salary: 1850000,
                basic: 925000,
                hra: 370000,
                tds: 185000,
            },
        },
    ],
    bank: [
        {
            id: "demo-2",
            file: new File([], "bank_statement_rohan.csv"),
            status: "success",
            progress: 100,
            detectedType: "bank_statement",
            typeDescription: "Bank Account Statement",
            confidence: 0.92,
            extractedData: {
                total_credits: 1400000,
                business_income: 1200000,
                ambiguous_count: 5,
                personal: 150000,
                warnings: ["5 transactions need your review"],
            },
            warnings: ["5 transactions need your review"],
        },
    ],
    portfolio: [
        {
            id: "demo-3",
            file: new File([], "Zerodha_pnl_rohan.xlsx"),
            status: "success",
            progress: 100,
            detectedType: "broker_statement",
            typeDescription: "Stock Broker Statement",
            confidence: 0.88,
            extractedData: {
                ltcg: 80000,
                stcg: 45000,
                crypto_gains: 50000,
                crypto_losses: 20000,
            },
        },
    ],
    investments: [
        {
            id: "demo-4",
            file: new File([], "elss_receipt_rohan.pdf"),
            status: "success",
            progress: 100,
            detectedType: "investment_statement",
            typeDescription: "Investment Statement (PPF/NPS/ELSS/LIC)",
            confidence: 0.90,
            extractedData: {
                investment_type: "ELSS",
                contribution_amount: 150000,
            },
        },
    ],
    other: [],
};

function generateId(): string {
    return Math.random().toString(36).substring(2, 9);
}

function formatBytes(bytes: number): string {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

function formatCurrency(value: number): string {
    return "₹" + value.toLocaleString("en-IN");
}

// File Upload Zone Component
function FileUploadZone({
    category,
    files,
    onFilesAdded,
    onFileRemoved,
    isDemo,
}: {
    category: CategoryConfig;
    files: UploadedFile[];
    onFilesAdded: (categoryId: string, newFiles: File[]) => void;
    onFileRemoved: (categoryId: string, fileId: string) => void;
    isDemo: boolean;
}) {
    const [isDragOver, setIsDragOver] = useState(false);
    const [isExpanded, setIsExpanded] = useState(true);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const Icon = category.icon;
    const hasFiles = files.length > 0;
    const hasSuccess = files.some((f) => f.status === "success");
    const hasError = files.some((f) => f.status === "error");
    const isProcessing = files.some((f) => f.status === "uploading" || f.status === "processing");

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragOver(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragOver(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragOver(false);
        const droppedFiles = Array.from(e.dataTransfer.files);
        onFilesAdded(category.id, droppedFiles);
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            const selectedFiles = Array.from(e.target.files);
            onFilesAdded(category.id, selectedFiles);
        }
        if (fileInputRef.current) {
            fileInputRef.current.value = "";
        }
    };

    return (
        <div
            className={cn(
                "bg-slate-900 border rounded-xl transition-all duration-300",
                hasSuccess && !hasError
                    ? "border-emerald-500/50 bg-emerald-500/5"
                    : hasError
                        ? "border-red-500/50 bg-red-500/5"
                        : "border-slate-800"
            )}
        >
            {/* Header */}
            <div
                className="flex items-center justify-between p-4 cursor-pointer"
                onClick={() => setIsExpanded(!isExpanded)}
            >
                <div className="flex items-center gap-3">
                    <div className={cn("w-10 h-10 rounded-lg flex items-center justify-center", category.bgColor)}>
                        <Icon className={cn("w-5 h-5", category.iconColor)} />
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <h3 className="font-semibold text-white text-sm">{category.title}</h3>
                            {category.required && <span className="text-red-400 text-sm">*</span>}
                            {hasFiles && (
                                <Badge variant="outline" className="text-xs">
                                    {files.length} file{files.length !== 1 ? "s" : ""}
                                </Badge>
                            )}
                        </div>
                        <p className="text-xs text-slate-500">{category.subtitle}</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    {hasSuccess && <CheckCircle2 className="w-5 h-5 text-emerald-400" />}
                    {hasError && <AlertCircle className="w-5 h-5 text-red-400" />}
                    {isProcessing && <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />}
                    {isExpanded ? (
                        <ChevronUp className="w-5 h-5 text-slate-500" />
                    ) : (
                        <ChevronDown className="w-5 h-5 text-slate-500" />
                    )}
                </div>
            </div>

            {/* Expanded Content */}
            {isExpanded && (
                <div className="px-4 pb-4 space-y-3">
                    <p className="text-xs text-slate-400">{category.description}</p>

                    {/* File List */}
                    {files.length > 0 && (
                        <div className="space-y-2">
                            {files.map((file) => (
                                <div
                                    key={file.id}
                                    className={cn(
                                        "flex items-center justify-between rounded-lg px-3 py-2 border",
                                        file.status === "success"
                                            ? "bg-emerald-500/10 border-emerald-500/30"
                                            : file.status === "error"
                                                ? "bg-red-500/10 border-red-500/30"
                                                : file.status === "needs_review"
                                                    ? "bg-amber-500/10 border-amber-500/30"
                                                    : "bg-slate-800/50 border-slate-700"
                                    )}
                                >
                                    <div className="flex items-center gap-2 overflow-hidden flex-1">
                                        {file.status === "uploading" || file.status === "processing" ? (
                                            <Loader2 className="w-4 h-4 text-blue-400 animate-spin shrink-0" />
                                        ) : file.status === "success" ? (
                                            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                                        ) : file.status === "error" ? (
                                            <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
                                        ) : file.status === "needs_review" ? (
                                            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
                                        ) : (
                                            <FileUp className="w-4 h-4 text-slate-400 shrink-0" />
                                        )}
                                        <div className="overflow-hidden flex-1">
                                            <span className="text-xs text-white font-medium truncate block">
                                                {file.file.name}
                                            </span>
                                            <div className="flex items-center gap-2 mt-0.5">
                                                {file.typeDescription && (
                                                    <span className="text-[10px] text-slate-400">
                                                        {file.typeDescription}
                                                    </span>
                                                )}
                                                {file.confidence && (
                                                    <Badge
                                                        variant={file.confidence >= 0.8 ? "success" : "warning"}
                                                        className="text-[9px] px-1 py-0"
                                                    >
                                                        {Math.round(file.confidence * 100)}%
                                                    </Badge>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                    {!isDemo && (
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                onFileRemoved(category.id, file.id);
                                            }}
                                            className="text-slate-500 hover:text-red-400 p-1 transition-colors"
                                        >
                                            <X className="w-4 h-4" />
                                        </button>
                                    )}
                                </div>
                            ))}

                            {/* Extracted Data Preview */}
                            {files.some((f) => f.extractedData && Object.keys(f.extractedData).length > 0) && (
                                <div className="mt-3 bg-slate-800/50 rounded-lg p-3">
                                    <div className="text-xs text-slate-400 mb-2">Extracted Data</div>
                                    <div className="grid grid-cols-2 gap-2">
                                        {files
                                            .filter((f) => f.extractedData)
                                            .flatMap((f) =>
                                                Object.entries(f.extractedData || {}).slice(0, 4).map(([key, value]) => (
                                                    <div key={`${f.id}-${key}`} className="bg-slate-900/50 rounded px-2 py-1">
                                                        <div className="text-[10px] text-slate-500 capitalize">
                                                            {key.replace(/_/g, " ")}
                                                        </div>
                                                        <div className="text-xs text-white font-mono">
                                                            {typeof value === "number" && key.includes("amount") || key.includes("salary") || key.includes("income") || key.includes("tds")
                                                                ? formatCurrency(value)
                                                                : String(value)}
                                                        </div>
                                                    </div>
                                                ))
                                            )}
                                    </div>
                                </div>
                            )}

                            {/* Warnings */}
                            {files.some((f) => f.warnings && f.warnings.length > 0) && (
                                <div className="flex items-center gap-2 bg-amber-500/10 border border-amber-500/20 rounded-lg px-3 py-2 text-amber-400 text-xs">
                                    <AlertTriangle className="w-4 h-4 shrink-0" />
                                    <span>{Array.from(new Set(files.flatMap((f) => f.warnings || []))).join(", ")}</span>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Upload Zone */}
                    {!isDemo && (
                        <div
                            onDragOver={handleDragOver}
                            onDragLeave={handleDragLeave}
                            onDrop={handleDrop}
                            onClick={() => fileInputRef.current?.click()}
                            className={cn(
                                "flex flex-col items-center justify-center w-full py-6 border-2 border-dashed rounded-lg cursor-pointer transition-all",
                                isDragOver
                                    ? "border-emerald-500 bg-emerald-500/10"
                                    : "border-slate-700 hover:border-emerald-500/40 hover:bg-emerald-500/5"
                            )}
                        >
                            <input
                                ref={fileInputRef}
                                type="file"
                                className="hidden"
                                multiple
                                accept={category.acceptedTypes.join(",")}
                                onChange={handleFileSelect}
                            />
                            {hasFiles ? (
                                <div className="flex items-center gap-2 text-emerald-400">
                                    <Plus className="w-4 h-4" />
                                    <span className="text-xs font-medium">Add more files</span>
                                </div>
                            ) : (
                                <>
                                    <Upload className={cn("w-6 h-6 mb-2", isDragOver ? "text-emerald-400" : "text-slate-500")} />
                                    <p className="text-xs text-slate-500">
                                        {isDragOver ? "Drop files here" : "Click or drag to upload"}
                                    </p>
                                    <p className="text-[10px] text-slate-600 mt-1">
                                        {category.acceptedTypes.join(", ")} • Max 10MB
                                    </p>
                                </>
                            )}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

function IngestContent() {
    const searchParams = useSearchParams();
    const isDemo = searchParams.get("demo") === "true";
    const [categoryFiles, setCategoryFiles] = useState<Record<string, UploadedFile[]>>(
        isDemo ? DEMO_FILES : { salary: [], bank: [], portfolio: [], investments: [], other: [] }
    );
    const [isLoading, setIsLoading] = useState(isDemo);
    const [overallStatus, setOverallStatus] = useState<"idle" | "processing" | "complete">("idle");
    const [activeGuardians, setActiveGuardians] = useState<Set<string>>(new Set());

    // Load active guardians
    useEffect(() => {
        if (typeof window !== "undefined") {
            const stored = localStorage.getItem("activeGuardians");
            if (stored) {
                try {
                    const parsed = JSON.parse(stored);
                    setActiveGuardians(new Set(parsed));
                } catch (e) {
                    console.error("Failed to parse activeGuardians", e);
                }
            } else if (isDemo) {
                // Default demo guardians
                setActiveGuardians(new Set(["sentinel", "shield", "architect"]));
            }
        }
    }, [isDemo]);
    useEffect(() => {
        if (isDemo) {
            const timer = setTimeout(() => setIsLoading(false), 1500);
            return () => clearTimeout(timer);
        }
    }, [isDemo]);

    const handleFilesAdded = useCallback(async (categoryId: string, newFiles: File[]) => {
        const filesToAdd: UploadedFile[] = newFiles.map((file) => ({
            id: generateId(),
            file,
            status: "pending" as const,
            progress: 0,
        }));

        // Add files to state immediately
        setCategoryFiles((prev) => ({
            ...prev,
            [categoryId]: [...prev[categoryId], ...filesToAdd],
        }));

        // Process each file
        for (const uploadedFile of filesToAdd) {
            // Update to uploading
            setCategoryFiles((prev) => ({
                ...prev,
                [categoryId]: prev[categoryId].map((f) =>
                    f.id === uploadedFile.id ? { ...f, status: "uploading" as const, progress: 10 } : f
                ),
            }));

            try {
                const formData = new FormData();
                formData.append("file", uploadedFile.file);

                // 1. Initiate Upload
                const uploadRes = await fetch("http://localhost:8000/api/v1/ingest/upload", {
                    method: "POST",
                    body: formData,
                });

                if (!uploadRes.ok) {
                    const err = await uploadRes.json();
                    throw new Error(err.detail || "Upload failed");
                }

                const uploadData = await uploadRes.json();
                const taskId = uploadData.task_id;

                // 2. Poll for Status
                let isComplete = false;
                let pollAttempts = 0;

                while (!isComplete && pollAttempts < 60) { // Timeout after 60s
                    await new Promise(r => setTimeout(r, 1000)); // Wait 1s

                    const statusRes = await fetch(`http://localhost:8000/api/v1/ingest/status/${taskId}`);

                    if (!statusRes.ok) continue;

                    const statusData = await statusRes.json();

                    // Update progress
                    setCategoryFiles((prev) => ({
                        ...prev,
                        [categoryId]: prev[categoryId].map((f) =>
                            f.id === uploadedFile.id
                                ? { ...f, progress: statusData.progress, status: "processing" }
                                : f
                        ),
                    }));

                    if (statusData.status === "complete") {
                        isComplete = true;

                        // Transform extracted fields to key-value pairs
                        const extractedMap: Record<string, any> = {};
                        if (statusData.result?.fields) {
                            statusData.result.fields.forEach((field: any) => {
                                extractedMap[field.name] = field.value;
                            });
                        }

                        setCategoryFiles((prev) => ({
                            ...prev,
                            [categoryId]: prev[categoryId].map((f) =>
                                f.id === uploadedFile.id
                                    ? {
                                        ...f,
                                        status: "success",
                                        progress: 100,
                                        detectedType: statusData.document_type,
                                        extractedData: extractedMap,
                                        confidence: 1.0, // Should come from overall confidence if available
                                        warnings: statusData.result?.warnings || [],
                                        error: statusData.result?.errors && statusData.result.errors.length > 0
                                            ? statusData.result.errors[0]
                                            : undefined,
                                    }
                                    : f
                            ),
                        }));
                    } else if (statusData.status === "error" || statusData.status === "failed") {
                        throw new Error(statusData.error || "Processing failed");
                    }

                    pollAttempts++;
                }

                if (!isComplete) {
                    throw new Error("Processing timed out");
                }

            } catch (error) {
                setCategoryFiles((prev) => ({
                    ...prev,
                    [categoryId]: prev[categoryId].map((f) =>
                        f.id === uploadedFile.id
                            ? {
                                ...f,
                                status: "error" as const,
                                progress: 100,
                                error: error instanceof Error ? error.message : "Upload failed",
                            }
                            : f
                    ),
                }));
            }
        }
    }, []);

    const handleFileRemoved = useCallback((categoryId: string, fileId: string) => {
        setCategoryFiles((prev) => ({
            ...prev,
            [categoryId]: prev[categoryId].filter((f) => f.id !== fileId),
        }));
    }, []);

    // Category Mapping Logic
    const GUARDIAN_TO_CATEGORIES: Record<string, string[]> = {
        sentinel: ["salary", "investments"],
        shield: ["bank"],
        architect: ["portfolio"],
        warden: ["other"],
    };

    // Filter categories based on active guardians
    const visibleCategories = CATEGORIES.filter((category) => {
        // Always show 'other' category
        if (category.id === "other") return true;

        // If no guardians selected yet (direct access), show all required
        if (activeGuardians.size === 0 && !isDemo) return true;

        // Check if category is mapped to any active guardian
        return Array.from(activeGuardians).some(guardianId =>
            GUARDIAN_TO_CATEGORIES[guardianId]?.includes(category.id)
        );
    });

    // Check if visible required categories have files
    const allRequiredHaveFiles = visibleCategories
        .filter(c => c.required)
        .every((c) => categoryFiles[c.id]?.some((f) => f.status === "success" || f.status === "needs_review"));
    const totalFiles = Object.values(categoryFiles).flat().length;
    const successfulFiles = Object.values(categoryFiles)
        .flat()
        .filter((f) => f.status === "success" || f.status === "needs_review").length;
    const isProcessing = Object.values(categoryFiles)
        .flat()
        .some((f) => f.status === "uploading" || f.status === "processing");

    const canProceed = isDemo ? true : (allRequiredHaveFiles && !isProcessing);

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
                    <div
                        className={cn(
                            "border rounded-xl p-5 transition-all duration-300",
                            isDemo ? "bg-slate-900 border-slate-800" : "bg-emerald-500/5 border-emerald-500/20"
                        )}
                    >
                        <div className="flex items-start gap-4">
                            <div
                                className={cn(
                                    "w-10 h-10 rounded-lg flex items-center justify-center",
                                    isDemo ? "bg-purple-500/20" : "bg-emerald-500/20"
                                )}
                            >
                                {isDemo ? (
                                    <BarChart3 className="w-5 h-5 text-purple-400" />
                                ) : (
                                    <ShieldCheck className="w-5 h-5 text-emerald-400" />
                                )}
                            </div>
                            <div className="flex-1">
                                <h2 className="text-lg font-semibold text-white mb-1">
                                    {isDemo ? "Demo Mode: Sample Documents Loaded" : "Upload Your Financial Documents"}
                                </h2>
                                <p className="text-slate-400 text-sm">
                                    {isDemo ? (
                                        <>
                                            Sample documents for{" "}
                                            <span className="text-amber-400 underline">Rohan Sharma</span> have been
                                            pre-loaded.
                                        </>
                                    ) : (
                                        "Upload multiple files per category. All processing happens securely on the server. Your data is never shared."
                                    )}
                                </p>
                                <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 mt-3 text-xs text-slate-500">
                                    <div className="flex items-center gap-2 text-emerald-400/80 bg-emerald-500/10 px-2 py-1 rounded border border-emerald-500/20">
                                        <ShieldCheck className="w-3 h-3" />
                                        <span>PII Scrubbing Active: Personal details removed</span>
                                    </div>
                                    <div className="flex gap-4">
                                        <span>✅ Encryption (TLS 1.3)</span>
                                        <span>✅ Auto-deletion</span>
                                    </div>
                                </div>
                            </div>
                            {totalFiles > 0 && (
                                <div className="text-right">
                                    <div className="text-2xl font-bold text-white">{successfulFiles}/{totalFiles}</div>
                                    <div className="text-xs text-slate-400">files processed</div>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Document Categories */}
                    <div className="space-y-4">
                        {visibleCategories.map((category) => (
                            <FileUploadZone
                                key={category.id}
                                category={category}
                                files={categoryFiles[category.id] || []}
                                onFilesAdded={handleFilesAdded}
                                onFileRemoved={handleFileRemoved}
                                isDemo={isDemo}
                            />
                        ))}
                    </div>

                    {/* Footer */}
                    <div className="flex items-center justify-between pt-4">
                        <div className="flex items-center gap-2 text-sm">
                            {canProceed ? (
                                <>
                                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                                    <span className="text-emerald-400">
                                        {isDemo ? "All demo documents loaded" : "Ready to proceed"}
                                    </span>
                                </>
                            ) : isProcessing ? (
                                <>
                                    <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
                                    <span className="text-blue-400">Processing files...</span>
                                </>
                            ) : (
                                <span className="text-slate-400">
                                    Upload required documents to continue (marked with *)
                                </span>
                            )}
                        </div>

                        <Link href={canProceed ? (isDemo ? "/review?demo=true" : "/review") : "#"}>
                            <Button
                                size="lg"
                                disabled={!canProceed}
                                className={cn(
                                    "px-8 rounded-xl shadow-lg transition-all hover:scale-105 disabled:opacity-50 disabled:hover:scale-100",
                                    canProceed
                                        ? "bg-emerald-600 hover:bg-emerald-700 text-white shadow-emerald-900/30"
                                        : "bg-slate-800 text-slate-500"
                                )}
                            >
                                {isDemo ? "Review Transactions" : "Analyze Documents"}
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
        <Suspense
            fallback={
                <div className="min-h-screen bg-slate-950 flex items-center justify-center text-white">
                    <Loader2 className="w-8 h-8 animate-spin" />
                </div>
            }
        >
            <IngestContent />
        </Suspense>
    );
}
