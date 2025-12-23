'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
    LayoutDashboard,
    Inbox,
    AlertTriangle,
    CheckCircle,
    BarChart3,
    Settings,
    Mail,
    MessageSquare,
    Twitter,
    Phone,
} from 'lucide-react';

const navigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Inbox', href: '/inbox', icon: Inbox },
    { name: 'Critical', href: '/inbox?priority=critical', icon: AlertTriangle },
    { name: 'Resolved', href: '/inbox?status=resolved', icon: CheckCircle },
];

const channels = [
    { name: 'Email', href: '/inbox?channel=email', icon: Mail },
    { name: 'Chat', href: '/inbox?channel=chat', icon: MessageSquare },
    { name: 'Social', href: '/inbox?channel=social', icon: Twitter },
    { name: 'Phone', href: '/inbox?channel=phone', icon: Phone },
];

const analytics = [
    { name: 'Reports', href: '/analytics', icon: BarChart3 },
];

export function Sidebar() {
    const pathname = usePathname();

    return (
        <div className="flex h-full w-64 flex-col bg-gray-900 text-white">
            {/* Logo */}
            <div className="flex h-16 items-center px-6 border-b border-gray-800">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                        <span className="text-lg font-bold">CR</span>
                    </div>
                    <span className="font-semibold text-lg">Complaint Resolver</span>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 overflow-y-auto p-4">
                {/* Main Navigation */}
                <div className="space-y-1">
                    {navigation.map((item) => {
                        const isActive = pathname === item.href ||
                            (item.href !== '/' && pathname.startsWith(item.href.split('?')[0]));
                        return (
                            <Link
                                key={item.name}
                                href={item.href}
                                className={cn(
                                    'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                                    isActive
                                        ? 'bg-blue-600 text-white'
                                        : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                                )}
                            >
                                <item.icon className="w-5 h-5" />
                                {item.name}
                            </Link>
                        );
                    })}
                </div>

                {/* Channels */}
                <div className="mt-8">
                    <h3 className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                        Channels
                    </h3>
                    <div className="mt-2 space-y-1">
                        {channels.map((item) => (
                            <Link
                                key={item.name}
                                href={item.href}
                                className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
                            >
                                <item.icon className="w-5 h-5" />
                                {item.name}
                            </Link>
                        ))}
                    </div>
                </div>

                {/* Analytics */}
                <div className="mt-8">
                    <h3 className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                        Analytics
                    </h3>
                    <div className="mt-2 space-y-1">
                        {analytics.map((item) => (
                            <Link
                                key={item.name}
                                href={item.href}
                                className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
                            >
                                <item.icon className="w-5 h-5" />
                                {item.name}
                            </Link>
                        ))}
                    </div>
                </div>
            </nav>

            {/* Settings */}
            <div className="p-4 border-t border-gray-800">
                <Link
                    href="/settings"
                    className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
                >
                    <Settings className="w-5 h-5" />
                    Settings
                </Link>
            </div>
        </div>
    );
}
