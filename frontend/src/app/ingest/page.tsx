'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

// Demo data for each guardian
const DEMO_EXTRACTED_DATA: Record<string, Record<string, string | number>> = {
    sentinel: {
        gross_salary: 1850000,
        basic: 925000,
        hra: 370000,
        tds: 185000,
        employer_nps: 0,
    },
    shield: {
        total_credits: 1400000,
        business_income: 1200000,
        ambiguous: 5,
        personal: 150000,
    },
    architect: {
        ltcg: 80000,
        stcg: 45000,
        crypto_gains: 50000,
        crypto_losses: 20000,
    },
    warden: {
        gross_rent: 0,
        net_taxable: 0,
        gifts: 0,
    },
};

interface UploadBlock {
    id: string;
    guardianId: string;
    title: string;
    description: string;
    fileTypes: string;
    icon: string;
    required: boolean;
    status: 'empty' | 'uploading' | 'processing' | 'success' | 'error';
    file?: File;
    extractedData?: Record<string, string | number>;
    error?: string;
}

const UPLOAD_BLOCKS: Record<string, Omit<UploadBlock, 'status'>> = {
    sentinel: {
        id: 'salary',
        guardianId: 'sentinel',
        title: 'Salary Documents',
        description: 'Form 16 Part B from your employer',
        fileTypes: '.pdf',
        icon: '💼',
        required: true,
    },
    shield: {
        id: 'hustle',
        guardianId: 'shield',
        title: 'Bank Statement',
        description: 'Primary account statement (PDF or CSV)',
        fileTypes: '.pdf,.csv',
        icon: '🔧',
        required: true,
    },
    architect: {
        id: 'portfolio',
        guardianId: 'architect',
        title: 'Portfolio P&L',
        description: 'Zerodha, Groww, or CoinDCX report',
        fileTypes: '.pdf,.xlsx,.csv',
        icon: '📊',
        required: true,
    },
    warden: {
        id: 'windfall',
        guardianId: 'warden',
        title: 'Rental & Gift Docs',
        description: 'Rent receipts, gift declarations (optional)',
        fileTypes: '.pdf,.jpg,.png',
        icon: '🎁',
        required: false,
    },
};

export default function DocumentHubPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const isDemo = searchParams.get('demo') === 'true' || (typeof window !== 'undefined' && localStorage.getItem('demoMode') === 'true');

    const [activeGuardians, setActiveGuardians] = useState<string[]>([]);
    const [blocks, setBlocks] = useState<UploadBlock[]>([]);
    const [hasAmbiguousTransactions, setHasAmbiguousTransactions] = useState(false);
    const [isAutoFilling, setIsAutoFilling] = useState(false);

    useEffect(() => {
        const stored = localStorage.getItem('activeGuardians');
        if (stored) {
            const guardians = JSON.parse(stored);
            setActiveGuardians(guardians);

            // Initialize blocks based on selected guardians
            const initialBlocks = guardians
                .map((g: string) => UPLOAD_BLOCKS[g])
                .filter(Boolean)
                .map((block: Omit<UploadBlock, 'status'>) => ({
                    ...block,
                    status: 'empty' as const,
                }));
            setBlocks(initialBlocks);

            // In demo mode, auto-fill all blocks with sample data
            if (isDemo) {
                autoFillDemoData(initialBlocks, guardians);
            }
        } else {
            router.push('/onboarding');
        }
    }, [router, isDemo]);

    const autoFillDemoData = async (initialBlocks: UploadBlock[], guardians: string[]) => {
        setIsAutoFilling(true);

        // Simulate sequential upload for each guardian
        for (let i = 0; i < guardians.length; i++) {
            const guardianId = guardians[i];
            const demoData = DEMO_EXTRACTED_DATA[guardianId];

            // Set to processing
            setBlocks(prev => prev.map(b =>
                b.guardianId === guardianId
                    ? { ...b, status: 'processing' as const }
                    : b
            ));

            await new Promise(resolve => setTimeout(resolve, 800));

            // Set to success with extracted data
            setBlocks(prev => prev.map(b =>
                b.guardianId === guardianId
                    ? { ...b, status: 'success' as const, extractedData: demoData }
                    : b
            ));

            // Check for ambiguous transactions
            if (guardianId === 'shield' && demoData.ambiguous && Number(demoData.ambiguous) > 0) {
                setHasAmbiguousTransactions(true);
            }
        }

        setIsAutoFilling(false);
    };

    const formatCurrency = (amount: number) => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0,
        }).format(amount);
    };

    const handleFileUpload = async (guardianId: string, file: File) => {
        setBlocks(prev => prev.map(b =>
            b.guardianId === guardianId
                ? { ...b, status: 'uploading' as const, file }
                : b
        ));

        await new Promise(resolve => setTimeout(resolve, 1000));

        setBlocks(prev => prev.map(b =>
            b.guardianId === guardianId
                ? { ...b, status: 'processing' as const }
                : b
        ));

        await new Promise(resolve => setTimeout(resolve, 1500));

        const mockData = DEMO_EXTRACTED_DATA[guardianId] || {};

        if (guardianId === 'shield') {
            setHasAmbiguousTransactions(true);
        }

        setBlocks(prev => prev.map(b =>
            b.guardianId === guardianId
                ? { ...b, status: 'success' as const, extractedData: mockData }
                : b
        ));
    };

    const handleRemoveFile = (guardianId: string) => {
        setBlocks(prev => prev.map(b =>
            b.guardianId === guardianId
                ? { ...b, status: 'empty' as const, file: undefined, extractedData: undefined }
                : b
        ));
    };

    const completedCount = blocks.filter(b => b.status === 'success').length;
    const requiredCount = blocks.filter(b => b.required).length;
    const requiredCompleted = blocks.filter(b => b.required && b.status === 'success').length;
    const canProceed = requiredCompleted === requiredCount && !isAutoFilling;

    const handleContinue = () => {
        const extractedData = blocks.reduce((acc, b) => {
            if (b.extractedData) {
                acc[b.guardianId] = b.extractedData;
            }
            return acc;
        }, {} as Record<string, Record<string, string | number>>);
        localStorage.setItem('extractedData', JSON.stringify(extractedData));

        if (hasAmbiguousTransactions) {
            router.push('/review' + (isDemo ? '?demo=true' : ''));
        } else {
            router.push('/dashboard' + (isDemo ? '?demo=true' : ''));
        }
    };

    return (
        <div className="min-h-screen flex flex-col">
            {/* Header */}
            <header className="border-b border-slate-800 px-6 py-4">
                <div className="max-w-5xl mx-auto flex items-center justify-between">
                    <button
                        onClick={() => router.back()}
                        className="text-slate-400 hover:text-white flex items-center gap-2"
                    >
                        ← Back
                    </button>

                    <div className="flex items-center gap-3">
                        {isDemo && (
                            <span className="px-3 py-1 bg-blue-500/20 text-blue-400 text-xs rounded-full">
                                📊 DEMO MODE
                            </span>
                        )}
                        <span className="font-bold">Document Collection Hub</span>
                        <span className="text-sm text-slate-400">({completedCount}/{blocks.length})</span>
                    </div>

                    <div className="w-20" />
                </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 px-6 py-8">
                {/* Demo Banner (Full Width - Edge to Edge) */}
                {isDemo && (
                    <div className="w-full mb-6">
                        <div className="bg-blue-500/20 border-y border-blue-500/30 px-6 py-3 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <span className="text-2xl">📊</span>
                                <div>
                                    <p className="font-bold text-blue-400">DEMO MODE</p>
                                    <p className="text-sm text-slate-400">
                                        Viewing sample results for Rohan Sharma. This is not your real data.
                                    </p>
                                </div>
                            </div>
                            <button
                                onClick={() => {
                                    localStorage.removeItem('demoMode');
                                    localStorage.removeItem('activeGuardians');
                                    localStorage.removeItem('extractedData');
                                    router.push('/');
                                }}
                                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm transition-colors"
                            >
                                ✕ Exit Demo
                            </button>
                        </div>
                    </div>
                )}

                <div className="max-w-5xl mx-auto space-y-8">
                    {/* Demo Info */}
                    {isDemo && (
                        <div className="card bg-blue-500/10 border-blue-500/30">
                            <div className="flex items-start gap-4">
                                <span className="text-2xl">📊</span>
                                <div>
                                    <h2 className="font-bold text-lg">Demo Mode: Auto-Filling Documents</h2>
                                    <p className="text-slate-400 text-sm mt-1">
                                        We're loading sample documents for <span className="text-blue-400 font-medium">Rohan Sharma</span>.
                                        In the real app, you'd upload your own files here.
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Regular Info */}
                    {!isDemo && (
                        <div className="card bg-slate-800/50">
                            <div className="flex items-start gap-4">
                                <span className="text-2xl">📋</span>
                                <div>
                                    <h2 className="font-bold text-lg">Gather Your Documents</h2>
                                    <p className="text-slate-400 text-sm mt-1">
                                        All upload blocks are shown below. Required documents are marked with *.
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Upload Blocks Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {blocks.map((block) => (
                            <UploadBlockCard
                                key={block.guardianId}
                                block={block}
                                onUpload={(file) => handleFileUpload(block.guardianId, file)}
                                onRemove={() => handleRemoveFile(block.guardianId)}
                                formatCurrency={formatCurrency}
                                isDemo={isDemo}
                            />
                        ))}
                    </div>

                    {/* Continue Button */}
                    <div className="flex items-center justify-between pt-4">
                        <div className="text-sm text-slate-400">
                            {isAutoFilling ? (
                                <span className="text-blue-400">⏳ Loading demo data...</span>
                            ) : requiredCompleted === requiredCount ? (
                                <span className="text-emerald-400">✓ All required documents ready</span>
                            ) : (
                                <span>Required: {requiredCompleted}/{requiredCount}</span>
                            )}
                        </div>

                        <button
                            onClick={handleContinue}
                            disabled={!canProceed}
                            className="btn-primary disabled:opacity-50"
                        >
                            {hasAmbiguousTransactions ? 'Review Transactions →' : 'Go to Dashboard →'}
                        </button>
                    </div>
                </div>
            </main>
        </div>
    );
}

// Upload Block Card Component
function UploadBlockCard({
    block,
    onUpload,
    onRemove,
    formatCurrency,
    isDemo,
}: {
    block: UploadBlock;
    onUpload: (file: File) => void;
    onRemove: () => void;
    formatCurrency: (n: number) => string;
    isDemo: boolean;
}) {
    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) onUpload(file);
    };

    const getStatusClass = () => {
        switch (block.status) {
            case 'success': return 'border-emerald-500/50 bg-emerald-500/5';
            case 'error': return 'border-red-500/50 bg-red-500/5';
            case 'uploading':
            case 'processing': return 'border-blue-500/50 bg-blue-500/5 animate-pulse';
            default: return 'border-slate-700 hover:border-slate-600';
        }
    };

    return (
        <div className={`card ${getStatusClass()} transition-all`}>
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                    <span className="text-3xl">{block.icon}</span>
                    <div>
                        <h3 className="font-bold flex items-center gap-2">
                            {block.title}
                            {block.required && <span className="text-red-400 text-sm">*</span>}
                        </h3>
                        <p className="text-sm text-slate-400">{block.description}</p>
                    </div>
                </div>

                {block.status === 'success' && (
                    <span className="px-2 py-1 bg-emerald-500/20 text-emerald-400 text-xs rounded-full">
                        ✓ {isDemo ? 'Loaded' : 'Done'}
                    </span>
                )}
            </div>

            {/* Content based on status */}
            {block.status === 'empty' && !isDemo && (
                <label className="block cursor-pointer">
                    <div className="border-2 border-dashed border-slate-700 rounded-xl p-6 text-center hover:border-emerald-500/50 transition-all">
                        <span className="text-2xl">⬆️</span>
                        <p className="text-sm text-slate-400 mt-2">Drop file or click to browse</p>
                    </div>
                    <input type="file" accept={block.fileTypes} onChange={handleFileChange} className="hidden" />
                </label>
            )}

            {block.status === 'processing' && (
                <div className="terminal-log text-xs">
                    <p>&gt; {isDemo ? 'Loading sample data' : 'Parsing document'}...</p>
                    <p>&gt; Extracting values...</p>
                    <p className="animate-pulse">&gt; Processing...</p>
                </div>
            )}

            {block.status === 'success' && block.extractedData && (
                <div className="space-y-3">
                    <div className="grid grid-cols-2 gap-2">
                        {Object.entries(block.extractedData).slice(0, 4).map(([key, value]) => (
                            <div key={key} className="bg-slate-800/50 rounded-lg p-2">
                                <p className="text-xs text-slate-500 capitalize">{key.replace(/_/g, ' ')}</p>
                                <p className="font-bold fiscal-num text-sm">
                                    {typeof value === 'number' && value > 1000 ? formatCurrency(value) : value}
                                </p>
                            </div>
                        ))}
                    </div>

                    {block.extractedData.ambiguous && Number(block.extractedData.ambiguous) > 0 && (
                        <div className="flex items-center gap-2 text-yellow-400 text-sm bg-yellow-500/10 rounded-lg p-2">
                            <span>⚠️</span>
                            <span>{block.extractedData.ambiguous} transactions need your review</span>
                        </div>
                    )}

                    {!isDemo && (
                        <button onClick={onRemove} className="text-sm text-slate-500 hover:text-red-400 transition-colors">
                            ✕ Remove and re-upload
                        </button>
                    )}
                </div>
            )}
        </div>
    );
}
