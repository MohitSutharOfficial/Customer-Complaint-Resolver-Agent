'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
    Settings as SettingsIcon,
    Bot,
    Bell,
    Shield,
    Database,
    Key,
    Save,
    RefreshCw,
    CheckCircle,
    AlertCircle,
} from 'lucide-react';

export default function SettingsPage() {
    const [aiSettings, setAiSettings] = useState({
        autoResolve: true,
        confidenceThreshold: 85,
        maxRetries: 3,
        enableEscalation: true,
        responseReview: 'auto', // 'auto', 'manual', 'mixed'
    });

    const [notifications, setNotifications] = useState({
        emailAlerts: true,
        slackIntegration: false,
        criticalOnly: false,
        dailyDigest: true,
    });

    const [saved, setSaved] = useState(false);

    const handleSave = () => {
        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
    };

    return (
        <div className="p-6 space-y-6 max-w-4xl">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
                    <p className="text-gray-500">Configure your complaint resolution system</p>
                </div>
                <Button onClick={handleSave}>
                    {saved ? (
                        <>
                            <CheckCircle className="w-4 h-4 mr-2" />
                            Saved!
                        </>
                    ) : (
                        <>
                            <Save className="w-4 h-4 mr-2" />
                            Save Changes
                        </>
                    )}
                </Button>
            </div>

            {/* AI Agent Settings */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Bot className="w-5 h-5 text-blue-600" />
                        AI Agent Configuration
                    </CardTitle>
                    <CardDescription>
                        Configure how AI agents process and respond to complaints
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    {/* Auto-resolve toggle */}
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="font-medium">Auto-resolve complaints</p>
                            <p className="text-sm text-gray-500">
                                Automatically send AI-generated responses for high-confidence classifications
                            </p>
                        </div>
                        <button
                            onClick={() => setAiSettings({ ...aiSettings, autoResolve: !aiSettings.autoResolve })}
                            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${aiSettings.autoResolve ? 'bg-blue-600' : 'bg-gray-200'
                                }`}
                        >
                            <span
                                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${aiSettings.autoResolve ? 'translate-x-6' : 'translate-x-1'
                                    }`}
                            />
                        </button>
                    </div>

                    {/* Confidence Threshold */}
                    <div className="space-y-2">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="font-medium">Confidence Threshold</p>
                                <p className="text-sm text-gray-500">
                                    Minimum confidence score required for auto-resolution
                                </p>
                            </div>
                            <span className="text-lg font-semibold text-blue-600">
                                {aiSettings.confidenceThreshold}%
                            </span>
                        </div>
                        <input
                            type="range"
                            min="50"
                            max="100"
                            value={aiSettings.confidenceThreshold}
                            onChange={(e) =>
                                setAiSettings({ ...aiSettings, confidenceThreshold: parseInt(e.target.value) })
                            }
                            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                        />
                        <div className="flex justify-between text-xs text-gray-400">
                            <span>50% (More auto-resolution)</span>
                            <span>100% (More human review)</span>
                        </div>
                    </div>

                    {/* Response Review Mode */}
                    <div className="space-y-2">
                        <p className="font-medium">Response Review Mode</p>
                        <p className="text-sm text-gray-500 mb-3">
                            Choose how AI-generated responses are handled before sending
                        </p>
                        <div className="grid grid-cols-3 gap-3">
                            {[
                                { value: 'auto', label: 'Automatic', desc: 'Send without review' },
                                { value: 'mixed', label: 'Smart', desc: 'Review critical only' },
                                { value: 'manual', label: 'Manual', desc: 'Review all responses' },
                            ].map((mode) => (
                                <button
                                    key={mode.value}
                                    onClick={() => setAiSettings({ ...aiSettings, responseReview: mode.value })}
                                    className={`p-3 rounded-lg border-2 text-left transition-colors ${aiSettings.responseReview === mode.value
                                            ? 'border-blue-600 bg-blue-50'
                                            : 'border-gray-200 hover:border-gray-300'
                                        }`}
                                >
                                    <p className="font-medium">{mode.label}</p>
                                    <p className="text-xs text-gray-500">{mode.desc}</p>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Enable Escalation */}
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="font-medium">Enable escalation routing</p>
                            <p className="text-sm text-gray-500">
                                Route complex or high-priority complaints to human agents
                            </p>
                        </div>
                        <button
                            onClick={() => setAiSettings({ ...aiSettings, enableEscalation: !aiSettings.enableEscalation })}
                            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${aiSettings.enableEscalation ? 'bg-blue-600' : 'bg-gray-200'
                                }`}
                        >
                            <span
                                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${aiSettings.enableEscalation ? 'translate-x-6' : 'translate-x-1'
                                    }`}
                            />
                        </button>
                    </div>
                </CardContent>
            </Card>

            {/* Notification Settings */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Bell className="w-5 h-5 text-purple-600" />
                        Notifications
                    </CardTitle>
                    <CardDescription>
                        Configure how you receive alerts and updates
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    {[
                        { key: 'emailAlerts', label: 'Email alerts', desc: 'Receive email notifications for new complaints' },
                        { key: 'slackIntegration', label: 'Slack integration', desc: 'Send notifications to Slack channel' },
                        { key: 'criticalOnly', label: 'Critical only', desc: 'Only notify for critical priority complaints' },
                        { key: 'dailyDigest', label: 'Daily digest', desc: 'Receive a daily summary of complaint activity' },
                    ].map((setting) => (
                        <div key={setting.key} className="flex items-center justify-between py-2">
                            <div>
                                <p className="font-medium">{setting.label}</p>
                                <p className="text-sm text-gray-500">{setting.desc}</p>
                            </div>
                            <button
                                onClick={() =>
                                    setNotifications({
                                        ...notifications,
                                        [setting.key]: !notifications[setting.key as keyof typeof notifications],
                                    })
                                }
                                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${notifications[setting.key as keyof typeof notifications] ? 'bg-blue-600' : 'bg-gray-200'
                                    }`}
                            >
                                <span
                                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${notifications[setting.key as keyof typeof notifications] ? 'translate-x-6' : 'translate-x-1'
                                        }`}
                                />
                            </button>
                        </div>
                    ))}
                </CardContent>
            </Card>

            {/* API & Integration Status */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Key className="w-5 h-5 text-green-600" />
                        API & Integrations
                    </CardTitle>
                    <CardDescription>
                        Status of connected services and APIs
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        {[
                            { name: 'OpenAI API', status: 'connected', model: 'GPT-4o-mini' },
                            { name: 'PostgreSQL Database', status: 'demo', model: 'Demo Mode' },
                            { name: 'Redis Cache', status: 'disconnected', model: 'Not configured' },
                            { name: 'Email Service', status: 'demo', model: 'Mock Mode' },
                        ].map((service) => (
                            <div key={service.name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                <div className="flex items-center gap-3">
                                    {service.status === 'connected' ? (
                                        <CheckCircle className="w-5 h-5 text-green-500" />
                                    ) : service.status === 'demo' ? (
                                        <AlertCircle className="w-5 h-5 text-yellow-500" />
                                    ) : (
                                        <AlertCircle className="w-5 h-5 text-red-500" />
                                    )}
                                    <div>
                                        <p className="font-medium">{service.name}</p>
                                        <p className="text-xs text-gray-500">{service.model}</p>
                                    </div>
                                </div>
                                <Badge
                                    variant={
                                        service.status === 'connected'
                                            ? 'default'
                                            : service.status === 'demo'
                                                ? 'secondary'
                                                : 'destructive'
                                    }
                                >
                                    {service.status === 'connected'
                                        ? 'Connected'
                                        : service.status === 'demo'
                                            ? 'Demo Mode'
                                            : 'Disconnected'}
                                </Badge>
                            </div>
                        ))}
                    </div>
                    <div className="mt-4 flex gap-2">
                        <Button variant="outline" className="flex-1">
                            <RefreshCw className="w-4 h-4 mr-2" />
                            Test Connections
                        </Button>
                        <Button variant="outline" className="flex-1">
                            <Database className="w-4 h-4 mr-2" />
                            Configure Database
                        </Button>
                    </div>
                </CardContent>
            </Card>

            {/* Security */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Shield className="w-5 h-5 text-red-600" />
                        Security & Compliance
                    </CardTitle>
                    <CardDescription>
                        Security settings and audit configuration
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                            <div className="flex items-center gap-3">
                                <CheckCircle className="w-5 h-5 text-green-600" />
                                <div>
                                    <p className="font-medium text-green-800">Audit Logging Enabled</p>
                                    <p className="text-xs text-green-600">All agent actions are being recorded</p>
                                </div>
                            </div>
                            <Badge>Active</Badge>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                            <div className="flex items-center gap-3">
                                <CheckCircle className="w-5 h-5 text-green-600" />
                                <div>
                                    <p className="font-medium text-green-800">Data Encryption</p>
                                    <p className="text-xs text-green-600">All data encrypted at rest and in transit</p>
                                </div>
                            </div>
                            <Badge>Active</Badge>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div className="flex items-center gap-3">
                                <AlertCircle className="w-5 h-5 text-gray-400" />
                                <div>
                                    <p className="font-medium">PII Redaction</p>
                                    <p className="text-xs text-gray-500">Automatically redact sensitive information</p>
                                </div>
                            </div>
                            <Button variant="outline" size="sm">Enable</Button>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
