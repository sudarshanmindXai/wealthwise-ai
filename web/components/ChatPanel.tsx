'use client';

import { useState, useRef, useEffect } from 'react';

interface Message {
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

interface ChatPanelProps {
    sessionId?: string;
    userContext?: {
        gross_income: number;
        tax_old: number;
        tax_new: number;
        recommended: string;
        potential_savings: number;
    };
}

export default function ChatPanel({ sessionId: initialSessionId, userContext }: ChatPanelProps) {
    const [messages, setMessages] = useState<Message[]>([
        {
            role: 'assistant',
            content: `👋 I'm **WealthWise**, your AI Tax Assistant.

I can help you:
- Explain your tax calculations
- Answer "What If" scenarios
- Clarify Income Tax Act sections

*Note: I cite relevant sections to ensure accuracy. For complex cases, please consult a CA.*`,
            timestamp: new Date(),
        },
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId, setSessionId] = useState(initialSessionId || '');
    const [isOpen, setIsOpen] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const sendMessage = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage: Message = {
            role: 'user',
            content: input.trim(),
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await fetch('/api/v1/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: userMessage.content,
                    session_id: sessionId || undefined,
                    user_context: userContext,
                }),
            });

            if (!response.ok) throw new Error('Chat failed');

            const data = await response.json();
            setSessionId(data.session_id);

            setMessages((prev) => [
                ...prev,
                {
                    role: 'assistant',
                    content: data.response,
                    timestamp: new Date(),
                },
            ]);
        } catch (err) {
            // Fallback response for demo
            const fallbackResponses: Record<string, string> = {
                hra: `Your HRA exemption is calculated under **Section 10(13A)**.

The exemption is the **minimum** of:
1. Actual HRA received
2. Rent paid - 10% of Basic
3. 50% of Basic (Metro)

**Action:** To increase HRA, pay higher rent or restructure salary.`,
                nps: `NPS has excellent tax benefits:

- **80CCD(1)**: Your contribution (within ₹1.5L 80C limit)
- **80CCD(1B)**: Additional ₹50,000
- **80CCD(2)**: Employer contribution (14% of Basic) - **works in BOTH regimes!**

**Action:** Ask HR to increase employer NPS contribution.`,
                crypto: `Crypto is taxed under **Section 115BBH**:

⚠️ **Key Rules:**
- Flat 30% tax (no slab benefit)
- Losses CANNOT offset any income
- 1% TDS on transfers

Your crypto loss is a "dead loss" - no tax benefit.`,
            };

            let response = `I understand you're asking about tax. Could you be more specific?

I can help with:
- HRA exemption calculation
- NPS deductions (80CCD)
- Section 44ADA for freelancers
- Capital gains and crypto taxes`;

            for (const [key, value] of Object.entries(fallbackResponses)) {
                if (userMessage.content.toLowerCase().includes(key)) {
                    response = value;
                    break;
                }
            }

            setMessages((prev) => [
                ...prev,
                {
                    role: 'assistant',
                    content: response,
                    timestamp: new Date(),
                },
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    // Quick suggestion chips
    const suggestions = [
        'Explain my HRA calculation',
        'How can I save more tax?',
        'What if I increase NPS?',
        'Explain Section 44ADA',
    ];

    return (
        <>
            {/* Chat Toggle Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="fixed bottom-6 right-6 w-14 h-14 bg-emerald-600 hover:bg-emerald-700 rounded-full shadow-lg shadow-emerald-900/50 flex items-center justify-center transition-all z-50"
            >
                {isOpen ? (
                    <span className="text-2xl text-white">✕</span>
                ) : (
                    <span className="text-2xl">💬</span>
                )}
            </button>

            {/* Chat Panel */}
            {isOpen && (
                <div className="fixed bottom-24 right-6 w-96 h-[600px] bg-slate-900 rounded-2xl shadow-2xl border border-slate-700 flex flex-col z-40 overflow-hidden">
                    {/* Header */}
                    <div className="p-4 border-b border-slate-700 bg-slate-800">
                        <div className="flex items-center gap-3">
                            <span className="text-2xl">🤖</span>
                            <div>
                                <h3 className="font-semibold">CA Companion</h3>
                                <p className="text-xs text-white/50">Powered by RAG + Tax Act</p>
                            </div>
                        </div>
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-4">
                        {messages.map((msg, idx) => (
                            <div
                                key={idx}
                                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                <div
                                    className={`max-w-[85%] rounded-2xl px-4 py-3 ${msg.role === 'user'
                                        ? 'bg-emerald-600 text-white'
                                        : 'bg-slate-800 text-white/90'
                                        }`}
                                >
                                    <div className="text-sm whitespace-pre-wrap">{msg.content}</div>
                                </div>
                            </div>
                        ))}
                        {isLoading && (
                            <div className="flex justify-start">
                                <div className="bg-slate-800 rounded-2xl px-4 py-3">
                                    <span className="animate-pulse">Thinking...</span>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Suggestions */}
                    {messages.length <= 2 && (
                        <div className="px-4 pb-2 flex flex-wrap gap-2">
                            {suggestions.map((s, idx) => (
                                <button
                                    key={idx}
                                    onClick={() => setInput(s)}
                                    className="text-xs bg-white/5 hover:bg-white/10 px-3 py-1.5 rounded-full border border-white/10 transition-all"
                                >
                                    {s}
                                </button>
                            ))}
                        </div>
                    )}

                    {/* Input */}
                    <div className="p-4 border-t border-slate-700 bg-slate-900">
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyPress={handleKeyPress}
                                placeholder="Ask about your taxes..."
                                className="flex-1 bg-slate-800 rounded-xl px-4 py-3 text-sm text-white outline-none focus:ring-2 focus:ring-emerald-500 border border-slate-700"
                            />
                            <button
                                onClick={sendMessage}
                                disabled={isLoading || !input.trim()}
                                className="px-4 py-3 bg-emerald-600 rounded-xl hover:bg-emerald-700 disabled:opacity-50 transition-all text-white"
                            >
                                →
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
