'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
    BarChart3,
    TrendingUp,
    TrendingDown,
    Clock,
    Bot,
    Users,
    CheckCircle,
    AlertTriangle,
    ArrowUpRight,
    ArrowDownRight,
} from 'lucide-react';

// Demo analytics data
const weeklyData = [
    { day: 'Mon', complaints: 145, resolved: 132 },
    { day: 'Tue', complaints: 189, resolved: 175 },
    { day: 'Wed', complaints: 167, resolved: 160 },
    { day: 'Thu', complaints: 198, resolved: 185 },
    { day: 'Fri', complaints: 234, resolved: 210 },
    { day: 'Sat', complaints: 156, resolved: 148 },
    { day: 'Sun', complaints: 112, resolved: 108 },
];

const sentimentData = [
    { sentiment: 'Positive', count: 234, percentage: 18.8, color: 'bg-green-500' },
    { sentiment: 'Neutral', count: 456, percentage: 36.5, color: 'bg-gray-400' },
    { sentiment: 'Frustrated', count: 389, percentage: 31.2, color: 'bg-yellow-500' },
    { sentiment: 'Angry', count: 168, percentage: 13.5, color: 'bg-red-500' },
];

const channelData = [
    { channel: 'Email', count: 523, percentage: 42 },
    { channel: 'Chat', count: 312, percentage: 25 },
    { channel: 'Social', count: 198, percentage: 16 },
    { channel: 'Phone', count: 214, percentage: 17 },
];

const agentMetrics = [
    { name: 'Classification Accuracy', value: 94.2, trend: 'up', change: '+2.1%' },
    { name: 'Response Quality Score', value: 87.5, trend: 'up', change: '+3.4%' },
    { name: 'Auto-Resolution Rate', value: 67.0, trend: 'up', change: '+5.2%' },
    { name: 'Escalation Rate', value: 18.0, trend: 'down', change: '-2.8%' },
    { name: 'Avg Response Time', value: 18, trend: 'down', change: '-23%', unit: 'min' },
    { name: 'First Contact Resolution', value: 72.5, trend: 'up', change: '+4.1%' },
];

export default function AnalyticsPage() {
    const maxComplaints = Math.max(...weeklyData.map(d => d.complaints));

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
                    <p className="text-gray-500">Detailed insights into complaint resolution performance</p>
                </div>
                <div className="flex gap-2">
                    <Button variant="outline">Export Report</Button>
                    <Button>
                        <Clock className="w-4 h-4 mr-2" />
                        Last 7 days
                    </Button>
                </div>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
                {agentMetrics.map((metric) => (
                    <Card key={metric.name}>
                        <CardContent className="pt-4">
                            <p className="text-xs text-gray-500 mb-1">{metric.name}</p>
                            <div className="flex items-end gap-1">
                                <span className="text-2xl font-bold">{metric.value}</span>
                                {metric.unit && <span className="text-sm text-gray-500">{metric.unit}</span>}
                                {!metric.unit && <span className="text-sm text-gray-500">%</span>}
                            </div>
                            <div className={`text-xs flex items-center mt-1 ${metric.trend === 'up' ? 'text-green-600' : 'text-red-600'
                                }`}>
                                {metric.trend === 'up' ? (
                                    <ArrowUpRight className="w-3 h-3 mr-1" />
                                ) : (
                                    <ArrowDownRight className="w-3 h-3 mr-1" />
                                )}
                                {metric.change}
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Weekly Trend */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <BarChart3 className="w-5 h-5 text-blue-600" />
                            Weekly Complaint Volume
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-64 flex items-end justify-between gap-2">
                            {weeklyData.map((day) => (
                                <div key={day.day} className="flex-1 flex flex-col items-center gap-1">
                                    <div className="w-full flex flex-col gap-1">
                                        <div
                                            className="w-full bg-blue-500 rounded-t transition-all"
                                            style={{ height: `${(day.complaints / maxComplaints) * 180}px` }}
                                        />
                                        <div
                                            className="w-full bg-green-400 rounded-b"
                                            style={{ height: `${(day.resolved / maxComplaints) * 180}px` }}
                                        />
                                    </div>
                                    <span className="text-xs text-gray-500">{day.day}</span>
                                </div>
                            ))}
                        </div>
                        <div className="flex justify-center gap-6 mt-4">
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 bg-blue-500 rounded" />
                                <span className="text-sm text-gray-600">Received</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 bg-green-400 rounded" />
                                <span className="text-sm text-gray-600">Resolved</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Sentiment Distribution */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Users className="w-5 h-5 text-purple-600" />
                            Sentiment Distribution
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {sentimentData.map((item) => (
                                <div key={item.sentiment} className="space-y-2">
                                    <div className="flex justify-between items-center">
                                        <span className="text-sm font-medium">{item.sentiment}</span>
                                        <span className="text-sm text-gray-500">{item.count} ({item.percentage}%)</span>
                                    </div>
                                    <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                                        <div
                                            className={`h-full ${item.color} rounded-full transition-all`}
                                            style={{ width: `${item.percentage}%` }}
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Bottom Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Channel Distribution */}
                <Card>
                    <CardHeader>
                        <CardTitle>Channel Distribution</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {channelData.map((item) => (
                                <div key={item.channel} className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                                            <span className="text-blue-600 text-xs font-bold">
                                                {item.channel.charAt(0)}
                                            </span>
                                        </div>
                                        <span className="text-sm font-medium">{item.channel}</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <span className="text-sm text-gray-500">{item.count}</span>
                                        <Badge variant="secondary">{item.percentage}%</Badge>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>

                {/* AI Performance Summary */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Bot className="w-5 h-5 text-blue-600" />
                            AI Agent Summary
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div className="p-4 bg-green-50 rounded-lg">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-sm text-green-700">Auto-Resolved</span>
                                    <CheckCircle className="w-5 h-5 text-green-600" />
                                </div>
                                <p className="text-3xl font-bold text-green-700">847</p>
                                <p className="text-xs text-green-600">67% of total complaints</p>
                            </div>

                            <div className="p-4 bg-orange-50 rounded-lg">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-sm text-orange-700">Escalated to Human</span>
                                    <AlertTriangle className="w-5 h-5 text-orange-600" />
                                </div>
                                <p className="text-3xl font-bold text-orange-700">228</p>
                                <p className="text-xs text-orange-600">18% of total complaints</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Response Time Breakdown */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Clock className="w-5 h-5 text-purple-600" />
                            Response Time Breakdown
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                <div>
                                    <p className="text-sm font-medium">Critical Priority</p>
                                    <p className="text-xs text-gray-500">Target: 1 hour</p>
                                </div>
                                <div className="text-right">
                                    <p className="text-lg font-bold text-green-600">42 min</p>
                                    <p className="text-xs text-green-600">✓ On target</p>
                                </div>
                            </div>

                            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                <div>
                                    <p className="text-sm font-medium">High Priority</p>
                                    <p className="text-xs text-gray-500">Target: 4 hours</p>
                                </div>
                                <div className="text-right">
                                    <p className="text-lg font-bold text-green-600">2.1 hrs</p>
                                    <p className="text-xs text-green-600">✓ On target</p>
                                </div>
                            </div>

                            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                <div>
                                    <p className="text-sm font-medium">Medium Priority</p>
                                    <p className="text-xs text-gray-500">Target: 8 hours</p>
                                </div>
                                <div className="text-right">
                                    <p className="text-lg font-bold text-green-600">5.4 hrs</p>
                                    <p className="text-xs text-green-600">✓ On target</p>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
