'use client';

import { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { api, CreateComplaintRequest } from '@/lib/api';
import { X, Send, Loader2 } from 'lucide-react';

interface NewComplaintFormProps {
    onClose: () => void;
    onSuccess: () => void;
}

export function NewComplaintForm({ onClose, onSuccess }: NewComplaintFormProps) {
    const [isLoading, setIsLoading] = useState(false);
    const [formData, setFormData] = useState<CreateComplaintRequest>({
        raw_text: '',
        channel: 'email',
        customer_email: '',
        customer_name: '',
    });
    const [result, setResult] = useState<any>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);

        try {
            const response = await api.createComplaint(formData);
            setResult(response);
            onSuccess();
        } catch (error) {
            console.error('Failed to create complaint:', error);
        } finally {
            setIsLoading(false);
        }
    };

    if (result) {
        return (
            <Card className="w-full max-w-2xl mx-auto">
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <CardTitle>Complaint Processed</CardTitle>
                        <Button variant="ghost" size="icon" onClick={onClose}>
                            <X className="w-4 h-4" />
                        </Button>
                    </div>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="bg-green-50 p-4 rounded-lg">
                        <p className="text-green-700 font-medium">
                            Complaint {result.external_id} has been processed successfully!
                        </p>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <span className="text-gray-500">Status:</span>
                            <span className="ml-2 font-medium">{result.status}</span>
                        </div>
                        <div>
                            <span className="text-gray-500">Priority:</span>
                            <span className="ml-2 font-medium">{result.priority?.level?.toUpperCase()}</span>
                        </div>
                        <div>
                            <span className="text-gray-500">Sentiment:</span>
                            <span className="ml-2 font-medium">{result.classification?.sentiment}</span>
                        </div>
                        <div>
                            <span className="text-gray-500">Confidence:</span>
                            <span className="ml-2 font-medium">
                                {Math.round((result.classification?.confidence || 0) * 100)}%
                            </span>
                        </div>
                    </div>

                    {result.classification?.categories && (
                        <div>
                            <span className="text-sm text-gray-500">Categories:</span>
                            <div className="flex flex-wrap gap-1 mt-1">
                                {result.classification.categories.map((cat: string) => (
                                    <span key={cat} className="px-2 py-1 bg-gray-100 rounded text-xs">
                                        {cat}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}

                    {result.response?.draft && (
                        <div>
                            <span className="text-sm text-gray-500">AI Generated Response:</span>
                            <div className="mt-1 p-3 bg-gray-50 rounded-lg text-sm whitespace-pre-wrap">
                                {result.response.draft}
                            </div>
                        </div>
                    )}

                    <div className="flex justify-end">
                        <Button onClick={onClose}>Close</Button>
                    </div>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className="w-full max-w-2xl mx-auto">
            <CardHeader>
                <div className="flex items-center justify-between">
                    <CardTitle>Submit New Complaint</CardTitle>
                    <Button variant="ghost" size="icon" onClick={onClose}>
                        <X className="w-4 h-4" />
                    </Button>
                </div>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Customer Name
                            </label>
                            <input
                                type="text"
                                value={formData.customer_name}
                                onChange={(e) => setFormData({ ...formData, customer_name: e.target.value })}
                                className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="John Doe"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Customer Email
                            </label>
                            <input
                                type="email"
                                value={formData.customer_email}
                                onChange={(e) => setFormData({ ...formData, customer_email: e.target.value })}
                                className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="john@example.com"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Channel
                        </label>
                        <select
                            value={formData.channel}
                            onChange={(e) => setFormData({ ...formData, channel: e.target.value })}
                            className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="email">Email</option>
                            <option value="chat">Chat</option>
                            <option value="social">Social Media</option>
                            <option value="phone">Phone</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Complaint Text *
                        </label>
                        <textarea
                            required
                            value={formData.raw_text}
                            onChange={(e) => setFormData({ ...formData, raw_text: e.target.value })}
                            rows={6}
                            className="w-full px-3 py-2 border rounded-lg text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Enter the customer's complaint here..."
                        />
                    </div>

                    <div className="flex justify-end gap-2">
                        <Button type="button" variant="outline" onClick={onClose}>
                            Cancel
                        </Button>
                        <Button type="submit" disabled={isLoading || !formData.raw_text}>
                            {isLoading ? (
                                <>
                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                    Processing...
                                </>
                            ) : (
                                <>
                                    <Send className="w-4 h-4 mr-2" />
                                    Submit & Analyze
                                </>
                            )}
                        </Button>
                    </div>
                </form>
            </CardContent>
        </Card>
    );
}
