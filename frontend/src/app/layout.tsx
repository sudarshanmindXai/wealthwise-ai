import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
    title: 'WealthWise AI - Tax Optimization',
    description: 'Agentic Tax Auditor & Optimization Engine for Indian Income Tax FY 2025-26',
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en" className="dark">
            <head>
                <link rel="preconnect" href="https://fonts.googleapis.com" />
                <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
            </head>
            <body className="min-h-screen">
                {children}
            </body>
        </html>
    );
}
