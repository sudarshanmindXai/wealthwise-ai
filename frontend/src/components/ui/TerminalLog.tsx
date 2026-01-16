'use client';

import { useEffect, useState } from 'react';

interface TerminalLogProps {
    lines: string[];
    speed?: number;
}

export default function TerminalLog({ lines, speed = 50 }: TerminalLogProps) {
    const [displayedLines, setDisplayedLines] = useState<string[]>([]);
    const [currentLineIndex, setCurrentLineIndex] = useState(0);
    const [currentCharIndex, setCurrentCharIndex] = useState(0);

    useEffect(() => {
        if (currentLineIndex >= lines.length) return;

        const currentLine = lines[currentLineIndex];

        if (currentCharIndex < currentLine.length) {
            const timeout = setTimeout(() => {
                setDisplayedLines(prev => {
                    const newLines = [...prev];
                    if (newLines.length === currentLineIndex) {
                        newLines.push('');
                    }
                    newLines[currentLineIndex] = currentLine.slice(0, currentCharIndex + 1);
                    return newLines;
                });
                setCurrentCharIndex(prev => prev + 1);
            }, speed);

            return () => clearTimeout(timeout);
        } else {
            // Move to next line
            const timeout = setTimeout(() => {
                setCurrentLineIndex(prev => prev + 1);
                setCurrentCharIndex(0);
            }, 300);

            return () => clearTimeout(timeout);
        }
    }, [currentLineIndex, currentCharIndex, lines, speed]);

    return (
        <div className="terminal-log">
            {displayedLines.map((line, index) => (
                <p key={index} className="leading-relaxed">
                    <span className="text-slate-500">&gt; </span>
                    <span dangerouslySetInnerHTML={{ __html: formatLine(line) }} />
                    {index === displayedLines.length - 1 && currentLineIndex < lines.length && (
                        <span className="animate-pulse ml-1">▋</span>
                    )}
                </p>
            ))}
            {currentLineIndex >= lines.length && displayedLines.length > 0 && (
                <p className="text-emerald-400 mt-2">✓ Complete</p>
            )}
        </div>
    );
}

function formatLine(line: string): string {
    // Add color formatting
    return line
        .replace(/Done\.?/gi, '<span class="text-emerald-400">Done.</span>')
        .replace(/Found\.?/gi, '<span class="text-emerald-400">Found.</span>')
        .replace(/Verified\.?/gi, '<span class="text-emerald-400">Verified.</span>')
        .replace(/Error:?/gi, '<span class="text-red-400">Error:</span>')
        .replace(/Warning:?/gi, '<span class="text-yellow-400">Warning:</span>')
        .replace(/₹[\d,]+/g, '<span class="text-emerald-400 fiscal-num">$&</span>');
}
