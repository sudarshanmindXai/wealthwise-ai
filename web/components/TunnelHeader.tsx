"use client";

import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

interface TunnelHeaderProps {
    title: string;
    step?: number;
    totalSteps?: number;
    progressText?: string;
    showBack?: boolean;
    backHref?: string;
    isDemo?: boolean;
}

export function TunnelHeader({
    title,
    step,
    totalSteps,
    progressText,
    showBack = true,
    backHref = "/",
    isDemo = false,
}: TunnelHeaderProps) {
    const progressValue = step && totalSteps ? (step / totalSteps) * 100 : 0;

    return (
        <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-md">
            <div className="container flex h-14 items-center justify-between px-4">
                <div className="flex items-center gap-4">
                    {showBack && (
                        <Link href={backHref}>
                            <Button
                                variant="ghost"
                                size="sm"
                                className="h-8 px-2 text-slate-400 hover:text-white hover:bg-slate-800"
                            >
                                <ArrowLeft className="h-4 w-4 mr-1" />
                                Back
                            </Button>
                        </Link>
                    )}
                </div>

                <div className="flex items-center gap-4">
                    {isDemo && (
                        <div className="flex items-center gap-2 bg-amber-500/20 px-2.5 py-1 rounded text-amber-400 text-xs font-medium">
                            <span className="text-sm">📊</span>
                            DEMO MODE
                        </div>
                    )}
                    <span className="text-sm font-medium text-slate-200">{title}</span>
                    {progressText && (
                        <span className="text-sm text-slate-400">{progressText}</span>
                    )}
                    {step && totalSteps && (
                        <div className="flex items-center gap-3">
                            <span className="text-sm text-slate-400">
                                Step {step} of {totalSteps}
                            </span>
                            <Progress value={progressValue} className="w-20 h-1.5" />
                        </div>
                    )}
                </div>

                <div className="w-24 text-right text-sm text-slate-500">
                    Identity Sieve
                </div>
            </div>
        </header>
    );
}
