import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Shield, BarChart3, Wrench, ArrowRight, Zap, Lock } from "lucide-react";

export default function LandingPage() {
    return (
        <div className="flex flex-col min-h-screen">
            {/* Header */}
            <header className="sticky top-0 z-50 w-full border-b border-white/5 bg-background/60 backdrop-blur-xl supports-[backdrop-filter]:bg-background/40">
                <div className="container flex h-16 items-center justify-between">
                    <div className="flex items-center gap-2 font-bold text-lg tracking-tight">
                        <div className="h-8 w-8 rounded-lg bg-primary/20 flex items-center justify-center">
                            <Shield className="h-5 w-5 text-primary" />
                        </div>
                        WealthWise AI
                    </div>
                    <nav className="flex items-center gap-4">
                        <Button variant="ghost" size="sm" className="hidden sm:flex">
                            Sign In
                        </Button>
                        <Button size="sm" className="font-semibold shadow-glow">
                            Get Started
                        </Button>
                    </nav>
                </div>
            </header>

            <main className="flex-1">
                {/* Hero Section */}
                <section className="relative pt-24 pb-32 overflow-hidden">
                    <div className="absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/20 via-background to-background opacity-40" />

                    <div className="container flex flex-col items-center text-center gap-8 max-w-4xl">
                        <div className="inline-flex items-center rounded-full border border-primary/20 bg-primary/10 px-3 py-1 text-sm text-primary backdrop-blur-sm">
                            <Zap className="mr-2 h-3.5 w-3.5" />
                            <span>v2.0 Now Live: The Twin-Engine Simulator</span>
                        </div>

                        <h1 className="text-5xl sm:text-7xl font-bold tracking-tight bg-gradient-to-b from-white to-white/70 bg-clip-text text-transparent">
                            Your Personal <br /> Financial Auditor
                        </h1>

                        <p className="text-xl text-muted-foreground max-w-2xl leading-relaxed">
                            WealthWise AI doesn't just calculate tax. It audits your financial life,
                            finds leakages, and constructs a fortress around your wealth
                            using advanced AI analysis.
                        </p>

                        <div className="flex flex-wrap items-center gap-4 mt-4">
                            <Link href="/ingest">
                                <Button size="lg" className="bg-emerald-600 hover:bg-emerald-700 text-white px-8 py-6 text-lg rounded-xl shadow-lg shadow-emerald-900/20 transition-all hover:scale-105">
                                    Start Audit
                                    <ArrowRight className="ml-2 h-5 w-5" />
                                </Button>
                            </Link>
                            <Link href="/demo">
                                <Button size="lg" variant="outline" className="h-14 px-8 text-base backdrop-blur-sm bg-background/50 border-white/10 hover:bg-white/5">
                                    Try Demo (No Login)
                                </Button>
                            </Link>
                        </div>
                    </div>
                </section>

                {/* Features Grid */}
                <section className="container py-24">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        <Card className="bg-white/5 border-white/10 backdrop-blur-sm hover:bg-white/10 transition-colors">
                            <CardHeader>
                                <div className="w-12 h-12 rounded-lg bg-blue-500/20 flex items-center justify-center mb-4 text-blue-400">
                                    <Shield className="h-6 w-6" />
                                </div>
                                <CardTitle>Salary Sentinel</CardTitle>
                                <CardDescription>
                                    Automated Form 16 analysis to detect missed HRA, LTA, and 80C opportunities instantly.
                                </CardDescription>
                            </CardHeader>
                        </Card>

                        <Card className="bg-white/5 border-white/10 backdrop-blur-sm hover:bg-white/10 transition-colors">
                            <CardHeader>
                                <div className="w-12 h-12 rounded-lg bg-purple-500/20 flex items-center justify-center mb-4 text-purple-400">
                                    <BarChart3 className="h-6 w-6" />
                                </div>
                                <CardTitle>Portfolio Architect</CardTitle>
                                <CardDescription>
                                    Smart balancing of Loss Harvesting and Capital Gains to minimize your tax liability.
                                </CardDescription>
                            </CardHeader>
                        </Card>

                        <Card className="bg-white/5 border-white/10 backdrop-blur-sm hover:bg-white/10 transition-colors">
                            <CardHeader>
                                <div className="w-12 h-12 rounded-lg bg-orange-500/20 flex items-center justify-center mb-4 text-orange-400">
                                    <Wrench className="h-6 w-6" />
                                </div>
                                <CardTitle>Hustle Shield</CardTitle>
                                <CardDescription>
                                    Optimized for freelancers using Section 44ADA presumptive taxation protections.
                                </CardDescription>
                            </CardHeader>
                        </Card>
                    </div>
                </section>

                {/* Footer */}
                <footer className="border-t border-white/5 py-12 bg-black/20">
                    <div className="container flex flex-col md:flex-row justify-between items-center gap-6">
                        <div className="flex items-center gap-2 text-muted-foreground text-sm">
                            <Lock className="h-4 w-4" />
                            <span>Local-First Processing. Your data never leaves your device.</span>
                        </div>
                        <div className="text-muted-foreground text-sm">
                            © 2026 WealthWise AI. Built for the Future of Finance.
                        </div>
                    </div>
                </footer>
            </main>
        </div>
    );
}
