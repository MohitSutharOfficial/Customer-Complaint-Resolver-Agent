'use client';

import { useState } from 'react';
import { ComplaintDetail } from '@/lib/api';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import {
    Clock,
    User,
    AlertTriangle,
    CheckCircle,
    Edit,
    RefreshCw,
    Send,
    ChevronRight,
    Bot,
    Sparkles,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface ComplaintDetailViewProps {
    complaint: ComplaintDetail;
    onClose: () => void;
}

const priorityColors: Record<string, string> = {
    critical: 'text-red-600 bg-red-50 border-red-200',
    high: 'text-orange-600 bg-orange-50 border-orange-200',
    medium: 'text-yellow-600 bg-yellow-50 border-yellow-200',
    low: 'text-green-600 bg-green-50 border-green-200',
    minimal: 'text-gray-600 bg-gray-50 border-gray-200',
};

export function ComplaintDetailView({ complaint, onClose }: ComplaintDetailViewProps) {
    const [isEditing, setIsEditing] = useState(false);
    const [response, setResponse] = useState(complaint.ai_response || '');

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleString();
    };

    const getSLATimeRemaining = () => {
        if (!complaint.sla_deadline) return null;
        const deadline = new Date(complaint.sla_deadline);
        const now = new Date();
        const diff = deadline.getTime() - now.getTime();

        if (diff < 0) return { text: 'Breached', isOverdue: true };

        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(minutes / 60);

        if (hours > 0) {
            return { text: `${hours}h ${minutes % 60}m remaining`, isOverdue: false };
        }
        return { text: `${minutes}m remaining`, isOverdue: false };
    };

    const slaStatus = getSLATimeRemaining();

    return (
        <div className="h-full flex flex-col">
            {/* Header */}
            <div className="p-4 border-b bg-white">
                <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                        <Badge className={cn('font-semibold', priorityColors[complaint.priority_level])}>
                            {complaint.priority_level.toUpperCase()}
                        </Badge>
                        {slaStatus && (
                            <Badge variant={slaStatus.isOverdue ? 'destructive' : 'secondary'}>
                                <Clock className="w-3 h-3 mr-1" />
                                {slaStatus.text}
                            </Badge>
                        )}
                    </div>
                    <span className="text-sm text-gray-500">
                        {complaint.external_id}
                    </span>
                </div>
                <h2 className="text-lg font-semibold">Complaint Details</h2>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {/* Customer Message */}
                <Card>
                    <CardHeader className="pb-2">
                        <div className="flex items-center gap-2">
                            <User className="w-5 h-5 text-gray-500" />
                            <CardTitle className="text-base">Customer Message</CardTitle>
                            <span className="text-xs text-gray-500 ml-auto">
                                {formatDate(complaint.received_at)}
                            </span>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <p className="text-gray-700 whitespace-pre-wrap">{complaint.raw_text}</p>
                        <div className="flex flex-wrap gap-2 mt-3">
                            {complaint.categories.map((cat) => (
                                <Badge key={cat} variant="outline">{cat}</Badge>
                            ))}
                            {complaint.sentiment && (
                                <Badge
                                    variant={complaint.sentiment === 'angry' ? 'destructive' :
                                        complaint.sentiment === 'frustrated' ? 'warning' : 'secondary'}
                                >
                                    {complaint.sentiment}
                                </Badge>
                            )}
                        </div>
                    </CardContent>
                </Card>

                {/* AI Analysis */}
                <Card className="border-blue-200 bg-blue-50/30">
                    <CardHeader className="pb-2">
                        <div className="flex items-center gap-2">
                            <Bot className="w-5 h-5 text-blue-600" />
                            <CardTitle className="text-base text-blue-900">AI Analysis</CardTitle>
                            {complaint.classification_confidence && (
                                <Badge variant="secondary" className="ml-auto">
                                    {Math.round(complaint.classification_confidence * 100)}% confidence
                                </Badge>
                            )}
                        </div>
                    </CardHeader>
                    <CardContent className="space-y-3">
                        <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                                <span className="text-gray-500">Intent:</span>
                                <span className="ml-2 font-medium">{complaint.intent || 'N/A'}</span>
                            </div>
                            <div>
                                <span className="text-gray-500">Priority Score:</span>
                                <span className="ml-2 font-medium">{complaint.priority_score}/5</span>
                            </div>
                        </div>

                        {complaint.priority_factors.length > 0 && (
                            <div>
                                <span className="text-sm text-gray-500">Priority Factors:</span>
                                <div className="flex flex-wrap gap-1 mt-1">
                                    {complaint.priority_factors.map((factor) => (
                                        <Badge key={factor} variant="outline" className="text-xs">
                                            {factor.replace(/_/g, ' ')}
                                        </Badge>
                                    ))}
                                </div>
                            </div>
                        )}

                        {complaint.escalated && (
                            <div className="flex items-center gap-2 text-orange-700 bg-orange-100 p-2 rounded">
                                <AlertTriangle className="w-4 h-4" />
                                <span className="text-sm font-medium">
                                    Escalated: {complaint.escalation_reason}
                                </span>
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Draft Response */}
                <Card className="border-green-200">
                    <CardHeader className="pb-2">
                        <div className="flex items-center gap-2">
                            <Sparkles className="w-5 h-5 text-green-600" />
                            <CardTitle className="text-base">AI Generated Response</CardTitle>
                            {complaint.response_confidence && (
                                <Badge variant="secondary" className="ml-auto">
                                    {Math.round(complaint.response_confidence * 100)}% confidence
                                </Badge>
                            )}
                        </div>
                    </CardHeader>
                    <CardContent>
                        {isEditing ? (
                            <textarea
                                value={response}
                                onChange={(e) => setResponse(e.target.value)}
                                className="w-full h-48 p-3 border rounded-lg text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        ) : (
                            <div className="bg-gray-50 p-3 rounded-lg">
                                <p className="text-gray-700 whitespace-pre-wrap text-sm">
                                    {complaint.ai_response || 'No response generated yet.'}
                                </p>
                            </div>
                        )}

                        {complaint.validation_passed !== null && (
                            <div className={cn(
                                'flex items-center gap-2 mt-3 p-2 rounded text-sm',
                                complaint.validation_passed
                                    ? 'bg-green-100 text-green-700'
                                    : 'bg-yellow-100 text-yellow-700'
                            )}>
                                {complaint.validation_passed ? (
                                    <>
                                        <CheckCircle className="w-4 h-4" />
                                        Validation Passed
                                    </>
                                ) : (
                                    <>
                                        <AlertTriangle className="w-4 h-4" />
                                        Validation: {complaint.validation_feedback || 'Needs review'}
                                    </>
                                )}
                            </div>
                        )}

                        <div className="flex gap-2 mt-3">
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setIsEditing(!isEditing)}
                            >
                                <Edit className="w-4 h-4 mr-1" />
                                {isEditing ? 'Cancel' : 'Edit'}
                            </Button>
                            <Button variant="outline" size="sm">
                                <RefreshCw className="w-4 h-4 mr-1" />
                                Regenerate
                            </Button>
                        </div>
                    </CardContent>
                </Card>

                {/* Recommended Actions */}
                {complaint.recommended_actions.length > 0 && (
                    <Card>
                        <CardHeader className="pb-2">
                            <CardTitle className="text-base">Recommended Actions</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <ul className="space-y-2">
                                {complaint.recommended_actions.map((action, idx) => (
                                    <li key={idx} className="flex items-center gap-2 text-sm">
                                        <ChevronRight className="w-4 h-4 text-blue-600" />
                                        {action}
                                    </li>
                                ))}
                            </ul>
                        </CardContent>
                    </Card>
                )}
            </div>

            {/* Action Bar */}
            <div className="p-4 border-t bg-white flex justify-between">
                <div className="flex gap-2">
                    <Button variant="outline" onClick={onClose}>
                        Close
                    </Button>
                    <Button variant="outline">
                        <User className="w-4 h-4 mr-1" />
                        Escalate
                    </Button>
                </div>
                <div className="flex gap-2">
                    <Button variant="default">
                        <CheckCircle className="w-4 h-4 mr-1" />
                        Approve & Send
                    </Button>
                </div>
            </div>
        </div>
    );
}
