"use client";

import Link from "next/link";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";

interface DemoBannerProps {
    userName?: string;
}

export function DemoBanner({ userName = "Rohan Sharma", isDemo = true }: DemoBannerProps & { isDemo?: boolean }) {
    if (!isDemo) return null;

    return (
        <div className="bg-gradient-to-r from-amber-600/20 to-orange-600/10 border-b border-amber-500/20">
            <div className="container flex items-center justify-between py-2 px-4">
                <div className="flex items-center gap-3">
                    <div className="flex items-center gap-2 bg-amber-500/20 px-2 py-0.5 rounded text-amber-400 text-xs font-medium">
                        <span className="text-base">📊</span>
                        DEMO MODE
                    </div>
                    <span className="text-sm text-slate-300">
                        Viewing sample results for <span className="text-amber-400">{userName}</span>. This is not your real data.
                    </span>
                </div>
                <Link href="/">
                    <Button
                        variant="outline"
                        size="sm"
                        className="h-7 px-3 text-xs border-slate-700 hover:bg-slate-800 hover:text-white"
                    >
                        <X className="h-3 w-3 mr-1" />
                        Exit Demo
                    </Button>
                </Link>
            </div>
        </div>
    );
}
