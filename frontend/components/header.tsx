'use client';

import { Bell, User, Search, Plus } from 'lucide-react';
import { Button } from './ui/button';
import Link from 'next/link';

export function Header() {
    return (
        <header className="h-16 border-b bg-white flex items-center justify-between px-6">
            {/* Search */}
            <div className="flex items-center gap-4 flex-1">
                <div className="relative max-w-md w-full">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Search complaints..."
                        className="w-full pl-10 pr-4 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-4">
                <Link href="/new">
                    <Button>
                        <Plus className="w-4 h-4 mr-2" />
                        New Complaint
                    </Button>
                </Link>

                <Button variant="ghost" size="icon" className="relative">
                    <Bell className="w-5 h-5" />
                    <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full text-white text-xs flex items-center justify-center">
                        3
                    </span>
                </Button>

                <div className="flex items-center gap-3">
                    <div className="text-right">
                        <p className="text-sm font-medium">Sarah Chen</p>
                        <p className="text-xs text-gray-500">Support Agent</p>
                    </div>
                    <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                        <User className="w-5 h-5 text-white" />
                    </div>
                </div>
            </div>
        </header>
    );
}
