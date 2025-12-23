'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/components/toast';
import {
    ArrowLeft,
    Send,
    Bot,
    Loader2,
    CheckCircle,
    AlertTriangle,
    Clock,
    User,
    Mail,
    MessageSquare,
    Twitter,
    Phone,
    XCircle,
} from 'lucide-react';
import Link from 'next/link';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

type ProcessingStep = {
    name: string;
    status: 'pending' | 'processing' | 'completed' | 'error';
    result?: string;
};

interface ComplaintResult {
    id: string;
    categories: string[];
    sentiment: string;
    intent: string;
    priority_level: string;
    priority_score: number;
    ai_response: string;
    status: string;
    escalated: boolean;
    escalation_reason: string | null;
    validation_passed: boolean;
    validation_feedback: string | null;
    recommended_actions: string[];
}

export default function NewComplaintPage() {
    const router = useRouter();
    const { showToast } = useToast();

    const [formData, setFormData] = useState({
        customerName: '',
        customerEmail: '',
        channel: 'email',
        subject: '',
        content: '',
    });

    const [isProcessing, setIsProcessing] = useState(false);
    const [processingSteps, setProcessingSteps] = useState<ProcessingStep[]>([]);
    const [result, setResult] = useState<ComplaintResult | null>(null);
    const [error, setError] = useState<string | null>(null);
    const pollingRef = useRef<NodeJS.Timeout | null>(null);

    // Cleanup polling on unmount
    useEffect(() => {
        return () => {
            if (pollingRef.current) {
                clearInterval(pollingRef.current);
            }
        };
    }, []);

    const updateStep = (stepIndex: number, status: 'pending' | 'processing' | 'completed' | 'error') => {
        setProcessingSteps((prev) =>
            prev.map((step, idx) => ({
                ...step,
                status: idx < stepIndex ? 'completed' : idx === stepIndex ? status : step.status,
            }))
        );
    };

    const processComplaint = async () => {
        setIsProcessing(true);
        setResult(null);
        setError(null);

        const steps: ProcessingStep[] = [
            { name: 'Submitting to Backend API', status: 'processing' },
            { name: 'Intake Agent - Normalizing complaint', status: 'pending' },
            { name: 'Context Agent - Fetching customer history', status: 'pending' },
            { name: 'Classifier Agent - Categorizing & sentiment', status: 'pending' },
            { name: 'Priority Agent - Calculating urgency', status: 'pending' },
            { name: 'Response Agent - Generating response', status: 'pending' },
            { name: 'Validator Agent - Quality check', status: 'pending' },
        ];

        setProcessingSteps(steps);

        try {
            // Step 1: Submit complaint to backend
            const response = await fetch(`${API_BASE}/api/v1/complaints/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    raw_text: formData.subject ? `${formData.subject}\n\n${formData.content}` : formData.content,
                    channel: formData.channel,
                    customer_email: formData.customerEmail,
                    customer_name: formData.customerName,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to submit complaint');
            }

            const complaint = await response.json();
            updateStep(0, 'completed');
            updateStep(1, 'processing');

            // Step 2: Poll for processing completion
            const complaintId = complaint.complaint_id;
            let attempts = 0;
            const maxAttempts = 60; // 60 seconds max

            const pollForCompletion = async (): Promise<ComplaintResult> => {
                return new Promise((resolve, reject) => {
                    pollingRef.current = setInterval(async () => {
                        attempts++;

                        try {
                            const statusResponse = await fetch(`${API_BASE}/api/v1/complaints/${complaintId}`);
                            if (!statusResponse.ok) {
                                throw new Error('Failed to fetch complaint status');
                            }

                            const statusData = await statusResponse.json();

                            // Update steps based on what data is available
                            if (statusData.language) {
                                updateStep(1, 'completed');
                                updateStep(2, 'processing');
                            }
                            if (statusData.categories && statusData.categories.length > 0) {
                                updateStep(2, 'completed');
                                updateStep(3, 'completed');
                                updateStep(4, 'processing');
                            }
                            if (statusData.priority_score) {
                                updateStep(4, 'completed');
                                updateStep(5, 'processing');
                            }
                            if (statusData.ai_response) {
                                updateStep(5, 'completed');
                                updateStep(6, 'processing');
                            }

                            // Check if processing is complete
                            if (statusData.status !== 'new' && statusData.status !== 'in_progress') {
                                if (pollingRef.current) {
                                    clearInterval(pollingRef.current);
                                }
                                updateStep(6, 'completed');
                                resolve(statusData);
                            }

                            if (attempts >= maxAttempts) {
                                if (pollingRef.current) {
                                    clearInterval(pollingRef.current);
                                }
                                // Return whatever we have
                                resolve(statusData);
                            }
                        } catch (err) {
                            if (attempts >= maxAttempts) {
                                if (pollingRef.current) {
                                    clearInterval(pollingRef.current);
                                }
                                reject(err);
                            }
                        }
                    }, 1000);
                });
            };

            const finalResult = await pollForCompletion();
            setResult(finalResult);
            setIsProcessing(false);
            showToast('success', 'Complaint processed successfully by AI agents', 'Processing Complete');

        } catch (err) {
            console.error('Error processing complaint:', err);
            setError(err instanceof Error ? err.message : 'An error occurred');
            setIsProcessing(false);

            // Mark current step as error
            setProcessingSteps((prev) =>
                prev.map((step) => ({
                    ...step,
                    status: step.status === 'processing' ? 'error' : step.status,
                }))
            );

            showToast('error', err instanceof Error ? err.message : 'Failed to process complaint');
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        if (!formData.customerName || !formData.customerEmail || !formData.content) {
            showToast('error', 'Please fill in all required fields');
            return;
        }

        processComplaint();
    };

    const handleSendResponse = () => {
        showToast('success', 'Response sent to customer successfully!');
        router.push('/inbox');
    };

    const channelIcons = {
        email: Mail,
        chat: MessageSquare,
        social: Twitter,
        phone: Phone,
    };

    return (
        <div className="p-6 max-w-5xl mx-auto">
            {/* Header */}
            <div className="flex items-center gap-4 mb-6">
                <Link href="/inbox">
                    <Button variant="ghost" size="sm">
                        <ArrowLeft className="w-4 h-4 mr-2" />
                        Back to Inbox
                    </Button>
                </Link>
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">New Complaint</h1>
                    <p className="text-gray-500">Submit and process a customer complaint through AI agents</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Complaint Form */}
                <Card>
                    <CardHeader>
                        <CardTitle>Complaint Details</CardTitle>
                        <CardDescription>Enter the customer complaint information</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Customer Name *</label>
                                    <Input
                                        placeholder="John Doe"
                                        value={formData.customerName}
                                        onChange={(e) => setFormData({ ...formData, customerName: e.target.value })}
                                        disabled={isProcessing}
                                    />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Email Address *</label>
                                    <Input
                                        type="email"
                                        placeholder="john@example.com"
                                        value={formData.customerEmail}
                                        onChange={(e) => setFormData({ ...formData, customerEmail: e.target.value })}
                                        disabled={isProcessing}
                                    />
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Channel</label>
                                    <Select
                                        value={formData.channel}
                                        onChange={(e) => setFormData({ ...formData, channel: e.target.value })}
                                        disabled={isProcessing}
                                    >
                                        <option value="email">Email</option>
                                        <option value="chat">Live Chat</option>
                                        <option value="social">Social Media</option>
                                        <option value="phone">Phone Call</option>
                                    </Select>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Subject</label>
                                    <Input
                                        placeholder="Brief description"
                                        value={formData.subject}
                                        onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                                        disabled={isProcessing}
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium">Complaint Content *</label>
                                <Textarea
                                    placeholder="Enter the full complaint text from the customer..."
                                    rows={6}
                                    value={formData.content}
                                    onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                                    disabled={isProcessing}
                                />
                            </div>

                            <Button type="submit" className="w-full" disabled={isProcessing}>
                                {isProcessing ? (
                                    <>
                                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                        Processing with AI Agents...
                                    </>
                                ) : (
                                    <>
                                        <Bot className="w-4 h-4 mr-2" />
                                        Process Complaint
                                    </>
                                )}
                            </Button>
                        </form>
                    </CardContent>
                </Card>

                {/* Processing Status & Results */}
                <div className="space-y-6">
                    {/* Processing Steps */}
                    {processingSteps.length > 0 && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Bot className="w-5 h-5 text-blue-600" />
                                    AI Agent Pipeline
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3">
                                    {processingSteps.map((step, index) => (
                                        <div key={index} className="flex items-center gap-3">
                                            {step.status === 'completed' && (
                                                <CheckCircle className="w-5 h-5 text-green-500" />
                                            )}
                                            {step.status === 'processing' && (
                                                <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
                                            )}
                                            {step.status === 'pending' && (
                                                <Clock className="w-5 h-5 text-gray-300" />
                                            )}
                                            {step.status === 'error' && (
                                                <AlertTriangle className="w-5 h-5 text-red-500" />
                                            )}
                                            <span
                                                className={`text-sm ${step.status === 'completed'
                                                    ? 'text-green-700'
                                                    : step.status === 'processing'
                                                        ? 'text-blue-700 font-medium'
                                                        : 'text-gray-400'
                                                    }`}
                                            >
                                                {step.name}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {/* Results */}
                    {result && (
                        <>
                            <Card>
                                <CardHeader>
                                    <CardTitle>AI Analysis Results</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="grid grid-cols-3 gap-4 mb-4">
                                        <div className="text-center p-3 bg-gray-50 rounded-lg">
                                            <p className="text-xs text-gray-500 mb-1">Category</p>
                                            <Badge variant="secondary" className="capitalize">
                                                {result.categories?.[0] || 'general'}
                                            </Badge>
                                        </div>
                                        <div className="text-center p-3 bg-gray-50 rounded-lg">
                                            <p className="text-xs text-gray-500 mb-1">Sentiment</p>
                                            <Badge
                                                variant={
                                                    result.sentiment === 'positive'
                                                        ? 'default'
                                                        : result.sentiment === 'angry'
                                                            ? 'destructive'
                                                            : 'secondary'
                                                }
                                                className="capitalize"
                                            >
                                                {result.sentiment || 'neutral'}
                                            </Badge>
                                        </div>
                                        <div className="text-center p-3 bg-gray-50 rounded-lg">
                                            <p className="text-xs text-gray-500 mb-1">Priority</p>
                                            <Badge
                                                variant={
                                                    result.priority_score >= 4 ? 'destructive' : result.priority_score >= 3 ? 'secondary' : 'default'
                                                }
                                            >
                                                {result.priority_level || `P${result.priority_score}`}
                                            </Badge>
                                        </div>
                                    </div>

                                    {/* Additional Info */}
                                    <div className="grid grid-cols-2 gap-4 mt-4">
                                        <div className="p-3 bg-gray-50 rounded-lg">
                                            <p className="text-xs text-gray-500 mb-1">Intent</p>
                                            <p className="text-sm font-medium capitalize">{result.intent || 'N/A'}</p>
                                        </div>
                                        <div className="p-3 bg-gray-50 rounded-lg">
                                            <p className="text-xs text-gray-500 mb-1">Status</p>
                                            <p className="text-sm font-medium capitalize">{result.status?.replace('_', ' ') || 'N/A'}</p>
                                        </div>
                                    </div>

                                    {result.escalated && (
                                        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                                            <div className="flex items-center gap-2 text-red-700">
                                                <AlertTriangle className="w-4 h-4" />
                                                <span className="font-medium">Escalated</span>
                                            </div>
                                            {result.escalation_reason && (
                                                <p className="text-sm text-red-600 mt-1">{result.escalation_reason}</p>
                                            )}
                                        </div>
                                    )}

                                    {result.recommended_actions && result.recommended_actions.length > 0 && (
                                        <div className="mt-4">
                                            <p className="text-xs text-gray-500 mb-2">Recommended Actions</p>
                                            <ul className="text-sm space-y-1">
                                                {result.recommended_actions.map((action, idx) => (
                                                    <li key={idx} className="flex items-start gap-2">
                                                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                                                        <span>{action}</span>
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader>
                                    <CardTitle>Generated Response</CardTitle>
                                    <CardDescription>
                                        AI-generated response ready for review and sending
                                    </CardDescription>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                                        <p className="text-sm whitespace-pre-wrap">{result.ai_response || 'No response generated'}</p>
                                    </div>

                                    {result.validation_passed === false && result.validation_feedback && (
                                        <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                                            <p className="text-xs text-yellow-700 font-medium mb-1">Validation Feedback</p>
                                            <p className="text-sm text-yellow-600">{result.validation_feedback}</p>
                                        </div>
                                    )}

                                    <div className="flex gap-2">
                                        <Button onClick={handleSendResponse} className="flex-1">
                                            <Send className="w-4 h-4 mr-2" />
                                            Send Response
                                        </Button>
                                        <Button variant="outline" className="flex-1" onClick={() => router.push(`/inbox/${result.id}`)}>
                                            <User className="w-4 h-4 mr-2" />
                                            View Details
                                        </Button>
                                    </div>
                                </CardContent>
                            </Card>
                        </>
                    )}

                    {/* Error State */}
                    {error && (
                        <Card className="border-red-200 bg-red-50">
                            <CardContent className="py-6">
                                <div className="flex items-center gap-3 text-red-700">
                                    <XCircle className="w-6 h-6" />
                                    <div>
                                        <h3 className="font-medium">Processing Failed</h3>
                                        <p className="text-sm">{error}</p>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {/* Empty State */}
                    {processingSteps.length === 0 && !result && (
                        <Card>
                            <CardContent className="py-12 text-center">
                                <Bot className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                                <h3 className="text-lg font-medium text-gray-900 mb-2">
                                    AI Agents Ready
                                </h3>
                                <p className="text-gray-500 text-sm">
                                    Fill in the complaint details and click &quot;Process Complaint&quot; to run it through the AI agent pipeline.
                                </p>
                            </CardContent>
                        </Card>
                    )}
                </div>
            </div>
        </div>
    );
}
