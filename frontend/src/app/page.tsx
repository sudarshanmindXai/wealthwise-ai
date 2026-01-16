'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function LandingPage() {
    const router = useRouter();

    const startDemo = () => {
        // Set demo mode flag
        localStorage.setItem('demoMode', 'true');
        // Pre-select all guardians for demo
        localStorage.setItem('activeGuardians', JSON.stringify(['sentinel', 'shield', 'architect', 'warden']));
        router.push('/onboarding?demo=true');
    };

    const startReal = () => {
        // Clear demo mode
        localStorage.removeItem('demoMode');
        localStorage.removeItem('activeGuardians');
        localStorage.removeItem('extractedData');
        router.push('/onboarding');
    };

    return (
        <div className="min-h-screen flex flex-col">
            {/* Nav */}
            <nav className="border-b border-slate-800 px-6 py-4">
                <div className="max-w-7xl mx-auto flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <span className="text-2xl">💰</span>
                        <span className="text-xl font-bold">WealthWise AI</span>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-slate-400">
                        <span>🔒 Ephemeral Session</span>
                        <span className="text-slate-600">|</span>
                        <span>FY 2025-26</span>
                    </div>
                </div>
            </nav>

            {/* Hero */}
            <main className="flex-1 flex flex-col items-center justify-center px-6 py-20">
                <div className="max-w-3xl text-center space-y-8">
                    {/* Headline */}
                    <h1 className="text-5xl md:text-7xl font-bold leading-tight">
                        Use your <span className="text-gradient">Past</span>
                        <br />
                        to Fix your <span className="text-gradient">Future</span>
                    </h1>

                    {/* Subheading */}
                    <p className="text-xl text-slate-400 max-w-2xl mx-auto">
                        WealthWise AI audits your financial year and unlocks hidden tax savings.
                        No jargon. No guesswork. Just optimized wealth.
                    </p>

                    {/* Terminal Preview */}
                    <div className="terminal-log text-left max-w-lg mx-auto">
                        <p>&gt; Scanning Form 16... <span className="text-emerald-300">Done.</span></p>
                        <p>&gt; Identifying Income Heads... Salary (Found), Crypto (Found).</p>
                        <p>&gt; Running Sec 115BBH Check...</p>
                        <p>&gt; <span className="text-yellow-400">⚠️ Efficiency Gap Detected: ₹45,000</span></p>
                    </div>

                    {/* CTA Buttons */}
                    <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
                        <button
                            onClick={startReal}
                            className="btn-primary text-lg px-8 py-4 hover-lift"
                        >
                            🚀 Start Retro-Audit
                        </button>
                        <button
                            onClick={startDemo}
                            className="btn-secondary text-lg px-8 py-4 hover-lift border-blue-500/50 text-blue-400 hover:bg-blue-500/10"
                        >
                            👀 Try Demo (No Login)
                        </button>
                    </div>

                    {/* Demo Description */}
                    <p className="text-sm text-slate-500 max-w-md mx-auto">
                        <span className="text-blue-400">Demo mode:</span> Experience the full flow with pre-filled sample data.
                        No documents needed.
                    </p>

                    {/* Trust Signals */}
                    <div className="flex justify-center gap-8 pt-4 text-sm text-slate-500">
                        <div className="flex items-center gap-2">
                            <span>🔒</span>
                            <span>256-bit Encryption</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <span>⏱️</span>
                            <span>Data Wiped After Session</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <span>📜</span>
                            <span>IT Act 1961 Compliant</span>
                        </div>
                    </div>
                </div>
            </main>

            {/* Footer */}
            <footer className="border-t border-slate-800 px-6 py-6">
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
                    <div className="text-sm text-slate-500">
                        © 2026 WealthWise AI. Not a substitute for professional CA advice.
                    </div>
                    <div className="flex gap-6 text-sm text-slate-400">
                        <a href="#" className="hover:text-white">Privacy</a>
                        <a href="#" className="hover:text-white">Security</a>
                        <a href="#" className="hover:text-white">Terms</a>
                    </div>
                </div>
            </footer>
        </div>
    );
}
