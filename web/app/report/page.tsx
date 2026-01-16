"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Download, Share2, Award, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function ReportPage() {
    const [score, setScore] = useState(0);

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
                                    <span>₹ 4.2L</span>
                                </div>
                                <div className="h-4 bg-slate-800 rounded-full overflow-hidden flex">
                                    <div className="h-full bg-red-500/80 w-[70%]" title="Tax"></div>
                                    <div className="h-full bg-blue-500/50 w-[30%]" title="Cess & Surcharge"></div>
                                </div>
                            </div>
                            <div className="space-y-2">
                                <div className="flex justify-between text-xs text-slate-400">
                                    <span>New Regime (Optimized)</span>
                                    <span className="text-emerald-400">₹ 3.0L</span>
                                </div>
                                <div className="h-4 bg-slate-800 rounded-full overflow-hidden flex">
                                    <div className="h-full bg-emerald-500/80 w-[50%]" title="Tax"></div>
                                    <div className="h-full bg-emerald-500/30 w-[20%]" title="Cess"></div>
                                </div>
                            </div>
                            <div className="pt-2 text-xs text-slate-500">
                                <span className="inline-block w-2 h-2 rounded-full bg-emerald-500 mr-1"></span> You save ₹ 1.2L annually
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
                    <Button size="lg" className="bg-white text-slate-950 hover:bg-slate-200">
                        <Download className="mr-2 w-4 h-4" /> Download Full Report
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
        </div>
    );
}
