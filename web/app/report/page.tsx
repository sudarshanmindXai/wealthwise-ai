"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Download, Share2, Award, ArrowLeft, AlertTriangle, ShieldAlert, FileText } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import ChatPanel from "@/components/ChatPanel";

import { downloadForm12BB, fetchReportData } from "@/lib/api";

interface RiskAlert {
    title: string;
    description: string;
    level: "high" | "medium" | "low";
    category: string;
    section_ref?: string;
}

interface ReportData {
    user_name?: string;
    user_pan?: string;
    employer_name?: string;
    designation?: string;
    financial_year: string;
    gross_salary: number;
    basic_salary: number;
    hra_received: number;
    tds_deducted: number;
    rent_paid: number;
    landlord_name?: string;
    landlord_pan?: string;
    rental_address?: string;
    lta: number;
    home_loan_interest: number;
    home_loan_lender?: string;
    deductions_80c: { description: string; amount: number }[];
    total_80c: number;
    deduction_80d: number;
    deduction_80g: number;
    ltcg: number;
    stcg: number;
    business_income: number;
    risk_alerts: RiskAlert[];
}

// Default sample data for fallback
const DEFAULT_SAMPLE_DATA = {
    "user": {
        "name": "Rohan Patel",
        "address": "Flat 402, Oakwood Residency, Indiranagar, Bangalore - 560038",
        "pan": "ABCDE1234F",
        "father_name": "Suresh Patel",
        "designation": "Senior Software Engineer",
        "financial_year": "2025-26"
    },
    "hra": {
        "rent_paid": 180000,
        "landlord_name": "Amit Kumar",
        "landlord_pan": "FGHIJ5678K",
        "address": "Flat 402, Oakwood Residency, Indiranagar, Bangalore"
    },
    "lta": 45000,
    "home_loan_interest": {
        "amount": 200000,
        "lender_name": "HDFC Bank",
        "lender_pan": "HDFC000123"
    },
    "deductions_80c": [
        { "description": "EPF", "amount": 100000 },
        { "description": "PPF", "amount": 50000 }
    ],
    "deductions_points": {
        "80D": 25000,
        "80G": 10000
    }
};

export default function ReportPage() {
    const [score, setScore] = useState(0);
    const [isDownloading, setIsDownloading] = useState(false);
    const [reportData, setReportData] = useState<ReportData | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Animate score
        const interval = setInterval(() => {
            setScore(prev => {
                if (prev >= 85) return 85;
                return prev + 1;
            });
        }, 20);
        return () => clearInterval(interval);
    }, []);

    // Fetch report data from API
    useEffect(() => {
        const loadReportData = async () => {
            setIsLoading(true);
            const data = await fetchReportData();
            if (data) {
                setReportData(data);
            }
            setIsLoading(false);
        };
        loadReportData();
    }, []);

    const handleDownloadReport = async () => {
        // Placeholder for Download Report logic
        alert("Downloading detailed Tax Analysis Report...");
    };

    const handleDownload = async () => {
        setIsDownloading(true);

        // Build Form 12BB data from reportData or fallback to sample
        let form12BBData;

        if (reportData && reportData.gross_salary > 0) {
            // Use real data from API
            form12BBData = {
                "user": {
                    "name": reportData.user_name || "Tax Payer",
                    "address": reportData.rental_address || "Address not provided",
                    "pan": reportData.user_pan || "XXXXX0000X",
                    "father_name": "Not Provided",
                    "designation": reportData.designation || "Employee",
                    "financial_year": reportData.financial_year
                },
                "hra": {
                    "rent_paid": reportData.rent_paid,
                    "landlord_name": reportData.landlord_name || "",
                    "landlord_pan": reportData.landlord_pan || "",
                    "address": reportData.rental_address || ""
                },
                "lta": reportData.lta,
                "home_loan_interest": {
                    "amount": reportData.home_loan_interest,
                    "lender_name": reportData.home_loan_lender || "",
                    "lender_pan": ""
                },
                "deductions_80c": reportData.deductions_80c.length > 0
                    ? reportData.deductions_80c
                    : [{ "description": "Total 80C", "amount": reportData.total_80c }],
                "deductions_points": {
                    "80D": reportData.deduction_80d,
                    "80G": reportData.deduction_80g
                }
            };
        } else {
            // Fallback to sample data
            form12BBData = DEFAULT_SAMPLE_DATA;
        }

        const success = await downloadForm12BB(form12BBData);
        if (success) {
            console.log("Download successful");
        } else {
            alert("Failed to download Form 12BB");
        }
        setIsDownloading(false);
    };

    // Display values
    const displayTaxOld = reportData?.gross_salary
        ? Math.round((reportData.gross_salary - 250000) * 0.3)
        : 420000;
    const displayTaxNew = reportData?.gross_salary
        ? Math.round((reportData.gross_salary - 300000) * 0.2)
        : 300000;
    const displaySavings = displayTaxOld - displayTaxNew;

    // Risk Analysis Display
    const riskAlerts = reportData?.risk_alerts || [];
    const hasHighRisk = riskAlerts.some(a => a.level === "high");

    return (
        <div className="min-h-screen bg-slate-950 text-slate-50 p-6 font-sans flex items-center justify-center">
            <div className="max-w-3xl w-full space-y-8">

                <div className="text-center space-y-4">
                    <div className="inline-block p-4 rounded-full bg-yellow-500/10 mb-4 animate-in zoom-in duration-500">
                        <Award className="w-16 h-16 text-yellow-500" />
                    </div>
                    <h1 className="text-4xl font-bold text-white tracking-tight">Audit Complete</h1>
                    <p className="text-xl text-slate-400">We've constructed your financial fortress.</p>
                </div>

                {/* Risk Radar - Only show if risks detected */}
                {riskAlerts.length > 0 && (
                    <Card className={`border-l-4 ${hasHighRisk ? 'border-l-red-500 border-red-500/20 bg-red-500/5' : 'border-l-orange-500 border-orange-500/20 bg-orange-500/5'}`}>
                        <CardHeader>
                            <div className="flex items-center gap-2">
                                <ShieldAlert className={`w-6 h-6 ${hasHighRisk ? 'text-red-500' : 'text-orange-500'}`} />
                                <CardTitle className="text-white">Tax Risk Radar</CardTitle>
                            </div>
                            <CardDescription>
                                We detected {riskAlerts.length} potential scrutiny triggers in your profile.
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {riskAlerts.map((alert, idx) => (
                                <div key={idx} className="bg-slate-900/50 p-4 rounded-lg border border-white/5">
                                    <div className="flex justify-between items-start mb-1">
                                        <h4 className={`font-bold ${alert.level === 'high' ? 'text-red-400' : 'text-orange-400'}`}>
                                            {alert.title}
                                        </h4>
                                        {alert.section_ref && (
                                            <span className="text-xs bg-slate-800 px-2 py-1 rounded text-slate-400">
                                                {alert.section_ref}
                                            </span>
                                        )}
                                    </div>
                                    <p className="text-sm text-slate-300">{alert.description}</p>
                                </div>
                            ))}
                        </CardContent>
                    </Card>
                )}

                <div className="grid md:grid-cols-2 gap-6">
                    {/* Tax Stack Visualization */}
                    <Card className="bg-slate-900 border-slate-800">
                        <CardHeader>
                            <CardTitle className="text-slate-200">Tax Breakdown</CardTitle>
                            <CardDescription>Old Regime vs New Regime</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="space-y-2">
                                <div className="flex justify-between text-xs text-slate-400">
                                    <span>Old Regime</span>
                                    <span>₹ {(displayTaxOld / 100000).toFixed(1)}L</span>
                                </div>
                                <div className="h-4 bg-slate-800 rounded-full overflow-hidden flex">
                                    <div className="h-full bg-red-500/80 w-[70%]" title="Tax"></div>
                                    <div className="h-full bg-blue-500/50 w-[30%]" title="Cess & Surcharge"></div>
                                </div>
                            </div>
                            <div className="space-y-2">
                                <div className="flex justify-between text-xs text-slate-400">
                                    <span>New Regime (Optimized)</span>
                                    <span className="text-emerald-400">₹ {(displayTaxNew / 100000).toFixed(1)}L</span>
                                </div>
                                <div className="h-4 bg-slate-800 rounded-full overflow-hidden flex">
                                    <div className="h-full bg-emerald-500/80 w-[50%]" title="Tax"></div>
                                    <div className="h-full bg-emerald-500/30 w-[20%]" title="Cess"></div>
                                </div>
                            </div>
                            <div className="pt-2 text-xs text-slate-500">
                                <span className="inline-block w-2 h-2 rounded-full bg-emerald-500 mr-1"></span> You save ₹ {(displaySavings / 100000).toFixed(1)}L annually
                            </div>
                        </CardContent>
                    </Card>

                    {/* Action Plan */}
                    <Card className="bg-slate-900 border-slate-800">
                        <CardHeader>
                            <CardTitle className="text-slate-200">Action Plan</CardTitle>
                            <CardDescription> Immediate next steps</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-3">
                            <div className="flex gap-3 items-start">
                                <div className="mt-1 bg-emerald-500/20 text-emerald-400 w-5 h-5 rounded flex items-center justify-center text-xs font-bold">1</div>
                                <p className="text-sm text-slate-300">Submit HRA receipts for <span className="text-white font-medium">₹1.8L</span> to employer.</p>
                            </div>
                            <div className="flex gap-3 items-start">
                                <div className="mt-1 bg-emerald-500/20 text-emerald-400 w-5 h-5 rounded flex items-center justify-center text-xs font-bold">2</div>
                                <p className="text-sm text-slate-300">Invest <span className="text-white font-medium">₹50k</span> in NPS (Tier 1) for 80CCD(1B).</p>
                            </div>
                            <div className="flex gap-3 items-start">
                                <div className="mt-1 bg-emerald-500/20 text-emerald-400 w-5 h-5 rounded flex items-center justify-center text-xs font-bold">3</div>
                                <p className="text-sm text-slate-300">Harvest <span className="text-white font-medium">₹35k</span> short-term losses before March 31.</p>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                <div className="flex flex-col sm:flex-row gap-4 justify-center pt-8">
                    <Button
                        size="lg"
                        className="bg-white text-slate-950 hover:bg-slate-200"
                        onClick={handleDownload}
                        disabled={isDownloading}
                    >
                        {isDownloading ? (
                            <span className="flex items-center gap-2">
                                <span className="animate-spin h-4 w-4 border-2 border-slate-900 border-t-transparent rounded-full" />
                                Generating 12BB...
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
                        onClick={handleDownloadReport}
                    >
                        <Download className="w-4 h-4 mr-2" /> Download Report
                    </Button>

                    <Button size="lg" variant="outline" className="border-slate-700 text-slate-300 hover:bg-slate-800">
                        <Share2 className="mr-2 w-4 h-4" /> Share with Advisor
                    </Button>
                </div>

                <div className="text-center">
                    <Link href="/dashboard" className="text-slate-500 hover:text-white text-sm flex items-center justify-center gap-1">
                        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
                    </Link>
                </div>
            </div>

            {/* Chat Panel */}
            <ChatPanel userContext={{
                gross_income: reportData?.gross_salary || 0,
                tax_old: displayTaxOld,
                tax_new: displayTaxNew,
                recommended: displayTaxNew < displayTaxOld ? "New Regime" : "Old Regime",
                potential_savings: displaySavings
            }} />
        </div>
    );
}
