import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Sidebar } from '@/components/sidebar';
import { Header } from '@/components/header';
import { ToastProvider } from '@/components/toast';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
    title: 'Customer Complaint Resolver Agent',
    description: 'AI-powered multi-agent system for automated customer complaint resolution',
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <body className={inter.className}>
                <ToastProvider>
                    <div className="flex h-screen">
                        <Sidebar />
                        <div className="flex-1 flex flex-col overflow-hidden">
                            <Header />
                            <main className="flex-1 overflow-y-auto bg-gray-50">
                                {children}
                            </main>
                        </div>
                    </div>
                </ToastProvider>
            </body>
        </html>
    );
}
