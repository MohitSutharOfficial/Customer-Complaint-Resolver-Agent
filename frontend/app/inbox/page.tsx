'use client';

import { useState, useEffect } from 'react';
import { ComplaintList } from '@/components/complaint-list';
import { ComplaintDetailView } from '@/components/complaint-detail';
import { NewComplaintForm } from '@/components/new-complaint-form';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Plus, Filter, RefreshCw } from 'lucide-react';
import { Complaint, ComplaintDetail } from '@/lib/api';

// Demo complaints data
const demoComplaints: Complaint[] = [
    {
        id: '1',
        external_id: 'C-A1B2C3D4',
        customer_name: 'John Doe',
        raw_text: 'I ordered a laptop 10 days ago, paid for express shipping, and it still hasn\'t arrived. This is the THIRD time I\'m contacting you. I want a full refund AND compensation, or I\'m disputing the charge and posting everywhere.',
        channel: 'email',
        priority_level: 'critical',
        priority_score: 5,
        sentiment: 'angry',
        status: 'pending_review',
        categories: ['Shipping', 'Billing'],
        received_at: new Date(Date.now() - 2 * 60000).toISOString(),
        sla_deadline: new Date(Date.now() + 45 * 60000).toISOString(),
        sla_breached: false,
    },
    {
        id: '2',
        external_id: 'C-E5F6G7H8',
        customer_name: 'Mary Smith',
        raw_text: 'I received a blender instead of the headphones I ordered. This is really frustrating as I needed these for a trip this weekend. Please help!',
        channel: 'chat',
        priority_level: 'high',
        priority_score: 4,
        sentiment: 'frustrated',
        status: 'in_progress',
        categories: ['Shipping', 'Product'],
        received_at: new Date(Date.now() - 15 * 60000).toISOString(),
        sla_deadline: new Date(Date.now() + 3 * 3600000).toISOString(),
        sla_breached: false,
    },
    {
        id: '3',
        external_id: 'C-I9J0K1L2',
        customer_name: 'Alex Thompson',
        raw_text: 'Could you please update me on my refund status? I returned a product 2 weeks ago and haven\'t received my money back yet. Order #12345.',
        channel: 'email',
        priority_level: 'medium',
        priority_score: 3,
        sentiment: 'neutral',
        status: 'new',
        categories: ['Billing'],
        received_at: new Date(Date.now() - 60 * 60000).toISOString(),
        sla_deadline: new Date(Date.now() + 7 * 3600000).toISOString(),
        sla_breached: false,
    },
    {
        id: '4',
        external_id: 'C-M3N4O5P6',
        customer_name: '@user123',
        raw_text: 'Would be great if you could add more color options for the wireless earbuds. Love the product quality but the black color doesn\'t match my style.',
        channel: 'social',
        priority_level: 'low',
        priority_score: 2,
        sentiment: 'positive',
        status: 'resolved',
        categories: ['Feedback'],
        received_at: new Date(Date.now() - 3 * 3600000).toISOString(),
        sla_deadline: undefined,
        sla_breached: false,
    },
    {
        id: '5',
        external_id: 'C-Q7R8S9T0',
        customer_name: 'Sarah Johnson',
        raw_text: 'My subscription was charged twice this month. I need an immediate refund for the duplicate charge. This is unacceptable!',
        channel: 'phone',
        priority_level: 'high',
        priority_score: 4,
        sentiment: 'angry',
        status: 'escalated',
        categories: ['Billing'],
        received_at: new Date(Date.now() - 30 * 60000).toISOString(),
        sla_deadline: new Date(Date.now() + 2 * 3600000).toISOString(),
        sla_breached: false,
    },
];

// Demo detail data
const demoDetail: ComplaintDetail = {
    id: '1',
    external_id: 'C-A1B2C3D4',
    customer_id: 'cust-123',
    raw_text: 'I ordered a laptop 10 days ago, paid for express shipping, and it still hasn\'t arrived. This is the THIRD time I\'m contacting you. I want a full refund AND compensation, or I\'m disputing the charge and posting everywhere.',
    channel: 'email',
    language: 'en',
    categories: ['Shipping', 'Billing'],
    sentiment: 'angry',
    intent: 'Refund',
    priority_level: 'critical',
    priority_score: 5,
    priority_factors: ['repeat_complaint', 'chargeback_threat', 'angry_sentiment', 'social_media_threat'],
    status: 'pending_review',
    assigned_to: 'supervisor_team',
    escalated: true,
    escalation_reason: 'Critical priority complaint, Legal/compliance concern',
    ai_response: `Dear John,

I sincerely apologize for this incredibly frustrating experience. You are absolutely right to be upset—having to contact us three times for the same issue is completely unacceptable, and I take full responsibility for this failure in our service.

I have taken the following immediate actions on your behalf:

✅ Full refund of $1,299 has been initiated and will arrive in your account within 3-5 business days
✅ $100 store credit has been added to your account as compensation for the inconvenience
✅ Your case has been escalated to our shipping manager for a full investigation
✅ A replacement laptop will be shipped today with overnight delivery at no additional cost (if you still want the product)

I understand that this experience has damaged your trust in us, and I want to personally ensure we make this right. You will receive a follow-up call from me within 24 hours to confirm everything has been resolved to your satisfaction.

Please don't hesitate to reply directly to this email or call me at [direct line] if you have any questions.

With sincere apologies,
Customer Support Team`,
    final_response: undefined,
    recommended_actions: [
        'Process full refund immediately',
        'Apply compensation credit',
        'Escalate to supervisor for review',
        'Schedule follow-up call',
        'Investigate shipping delay',
    ],
    classification_confidence: 0.94,
    response_confidence: 0.87,
    validation_passed: true,
    sla_deadline: new Date(Date.now() + 45 * 60000).toISOString(),
    sla_breached: false,
    received_at: new Date(Date.now() - 2 * 60000).toISOString(),
    first_response_at: undefined,
    resolved_at: undefined,
};

export default function InboxPage() {
    const [complaints, setComplaints] = useState<Complaint[]>(demoComplaints);
    const [selectedComplaint, setSelectedComplaint] = useState<ComplaintDetail | null>(null);
    const [showNewForm, setShowNewForm] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [statusFilter, setStatusFilter] = useState<string | null>(null);

    const handleSelectComplaint = (complaint: Complaint) => {
        // In real app, fetch full details
        if (complaint.id === '1') {
            setSelectedComplaint(demoDetail);
        } else {
            // Mock detail for other complaints
            setSelectedComplaint({
                ...demoDetail,
                id: complaint.id,
                external_id: complaint.external_id,
                raw_text: complaint.raw_text,
                channel: complaint.channel,
                categories: complaint.categories,
                sentiment: complaint.sentiment,
                priority_level: complaint.priority_level,
                priority_score: complaint.priority_score,
                status: complaint.status,
                received_at: complaint.received_at,
                sla_deadline: complaint.sla_deadline,
                sla_breached: complaint.sla_breached,
            });
        }
    };

    const handleRefresh = () => {
        setIsLoading(true);
        setTimeout(() => {
            setIsLoading(false);
        }, 1000);
    };

    const filteredComplaints = statusFilter
        ? complaints.filter(c => c.status === statusFilter)
        : complaints;

    return (
        <div className="h-full flex">
            {/* Complaint List Panel */}
            <div className="w-1/2 border-r flex flex-col bg-white">
                {/* Toolbar */}
                <div className="p-4 border-b flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <h2 className="font-semibold">Inbox</h2>
                        <Badge variant="secondary">{filteredComplaints.length}</Badge>
                    </div>
                    <div className="flex items-center gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={handleRefresh}
                            disabled={isLoading}
                        >
                            <RefreshCw className={`w-4 h-4 mr-1 ${isLoading ? 'animate-spin' : ''}`} />
                            Refresh
                        </Button>
                        <Button size="sm" onClick={() => setShowNewForm(true)}>
                            <Plus className="w-4 h-4 mr-1" />
                            New
                        </Button>
                    </div>
                </div>

                {/* Filters */}
                <div className="p-4 border-b flex items-center gap-2 overflow-x-auto">
                    <Button
                        variant={statusFilter === null ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setStatusFilter(null)}
                    >
                        All
                    </Button>
                    <Button
                        variant={statusFilter === 'new' ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setStatusFilter('new')}
                    >
                        New
                    </Button>
                    <Button
                        variant={statusFilter === 'in_progress' ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setStatusFilter('in_progress')}
                    >
                        In Progress
                    </Button>
                    <Button
                        variant={statusFilter === 'pending_review' ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setStatusFilter('pending_review')}
                    >
                        Pending Review
                    </Button>
                    <Button
                        variant={statusFilter === 'escalated' ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setStatusFilter('escalated')}
                    >
                        Escalated
                    </Button>
                    <Button
                        variant={statusFilter === 'resolved' ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setStatusFilter('resolved')}
                    >
                        Resolved
                    </Button>
                </div>

                {/* List */}
                <div className="flex-1 overflow-y-auto">
                    <ComplaintList
                        complaints={filteredComplaints}
                        selectedId={selectedComplaint?.id}
                        onSelect={handleSelectComplaint}
                    />
                </div>
            </div>

            {/* Detail Panel */}
            <div className="w-1/2 bg-gray-50">
                {showNewForm ? (
                    <div className="h-full flex items-center justify-center p-6">
                        <NewComplaintForm
                            onClose={() => setShowNewForm(false)}
                            onSuccess={() => {
                                setShowNewForm(false);
                                handleRefresh();
                            }}
                        />
                    </div>
                ) : selectedComplaint ? (
                    <ComplaintDetailView
                        complaint={selectedComplaint}
                        onClose={() => setSelectedComplaint(null)}
                    />
                ) : (
                    <div className="h-full flex flex-col items-center justify-center text-gray-400">
                        <Filter className="w-16 h-16 mb-4 opacity-50" />
                        <p className="text-lg">Select a complaint to view details</p>
                        <p className="text-sm">or create a new one to see AI analysis</p>
                    </div>
                )}
            </div>
        </div>
    );
}
