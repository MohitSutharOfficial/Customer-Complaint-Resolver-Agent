'use client';

import { cn } from '@/lib/utils';
import { Badge } from './ui/badge';
import { Mail, MessageSquare, Twitter, Phone, Clock } from 'lucide-react';
import { Complaint } from '@/lib/api';

interface ComplaintListProps {
    complaints: Complaint[];
    selectedId?: string;
    onSelect: (complaint: Complaint) => void;
}

const channelIcons: Record<string, React.ElementType> = {
    email: Mail,
    chat: MessageSquare,
    social: Twitter,
    phone: Phone,
};

const priorityColors: Record<string, string> = {
    critical: 'bg-red-500',
    high: 'bg-orange-500',
    medium: 'bg-yellow-500',
    low: 'bg-green-500',
    minimal: 'bg-gray-400',
};

const priorityBadgeVariants: Record<string, 'destructive' | 'warning' | 'secondary' | 'success' | 'default'> = {
    critical: 'destructive',
    high: 'warning',
    medium: 'secondary',
    low: 'success',
    minimal: 'default',
};

function formatTimeAgo(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();

    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
}

export function ComplaintList({ complaints, selectedId, onSelect }: ComplaintListProps) {
    if (complaints.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-64 text-gray-500">
                <Mail className="w-12 h-12 mb-4 opacity-50" />
                <p>No complaints found</p>
            </div>
        );
    }

    return (
        <div className="divide-y">
            {complaints.map((complaint) => {
                const ChannelIcon = channelIcons[complaint.channel] || Mail;
                const isSelected = complaint.id === selectedId;

                return (
                    <div
                        key={complaint.id}
                        onClick={() => onSelect(complaint)}
                        className={cn(
                            'p-4 cursor-pointer transition-colors hover:bg-gray-50',
                            isSelected && 'bg-blue-50 border-l-4 border-l-blue-600'
                        )}
                    >
                        <div className="flex items-start gap-3">
                            {/* Priority indicator */}
                            <div className={cn(
                                'w-2 h-2 rounded-full mt-2 flex-shrink-0',
                                priorityColors[complaint.priority_level]
                            )} />

                            <div className="flex-1 min-w-0">
                                {/* Header */}
                                <div className="flex items-center justify-between gap-2 mb-1">
                                    <div className="flex items-center gap-2">
                                        <Badge variant={priorityBadgeVariants[complaint.priority_level]}>
                                            {complaint.priority_level.toUpperCase()}
                                        </Badge>
                                        {complaint.categories.slice(0, 2).map((cat) => (
                                            <Badge key={cat} variant="outline" className="text-xs">
                                                {cat}
                                            </Badge>
                                        ))}
                                    </div>
                                    <div className="flex items-center gap-2 text-xs text-gray-500">
                                        <Clock className="w-3 h-3" />
                                        {formatTimeAgo(complaint.received_at)}
                                    </div>
                                </div>

                                {/* Customer & Preview */}
                                <p className="font-medium text-sm text-gray-900 truncate">
                                    {complaint.customer_name || 'Unknown Customer'}
                                </p>
                                <p className="text-sm text-gray-600 line-clamp-2 mt-1">
                                    {complaint.raw_text}
                                </p>

                                {/* Footer */}
                                <div className="flex items-center justify-between mt-2">
                                    <div className="flex items-center gap-2">
                                        <ChannelIcon className="w-4 h-4 text-gray-400" />
                                        {complaint.sentiment && (
                                            <Badge
                                                variant={complaint.sentiment === 'angry' ? 'destructive' :
                                                    complaint.sentiment === 'frustrated' ? 'warning' : 'secondary'}
                                                className="text-xs"
                                            >
                                                {complaint.sentiment}
                                            </Badge>
                                        )}
                                    </div>
                                    <Badge
                                        variant={complaint.status === 'resolved' ? 'success' :
                                            complaint.status === 'escalated' ? 'destructive' : 'secondary'}
                                        className="text-xs"
                                    >
                                        {complaint.status.replace('_', ' ')}
                                    </Badge>
                                </div>

                                {/* SLA Warning */}
                                {complaint.sla_breached && (
                                    <div className="mt-2 text-xs text-red-600 flex items-center gap-1">
                                        <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                                        SLA Breached
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
