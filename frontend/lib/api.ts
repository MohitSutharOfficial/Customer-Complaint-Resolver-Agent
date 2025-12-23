// API client for backend communication

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface Complaint {
    id: string;
    external_id: string;
    customer_name?: string;
    raw_text: string;
    channel: string;
    priority_level: string;
    priority_score: number;
    sentiment?: string;
    status: string;
    categories: string[];
    received_at: string;
    sla_deadline?: string;
    sla_breached: boolean;
}

export interface ComplaintDetail {
    id: string;
    external_id: string;
    customer_id: string;
    raw_text: string;
    channel: string;
    language: string;
    categories: string[];
    sentiment?: string;
    intent?: string;
    priority_level: string;
    priority_score: number;
    priority_factors: string[];
    status: string;
    assigned_to?: string;
    escalated: boolean;
    escalation_reason?: string;
    ai_response?: string;
    final_response?: string;
    recommended_actions: string[];
    classification_confidence?: number;
    response_confidence?: number;
    validation_passed?: boolean;
    sla_deadline?: string;
    sla_breached: boolean;
    received_at: string;
    first_response_at?: string;
    resolved_at?: string;
}

export interface CreateComplaintRequest {
    raw_text: string;
    channel: string;
    customer_id?: string;
    customer_email?: string;
    customer_name?: string;
}

export interface AnalyticsOverview {
    total_complaints: number;
    open_complaints: number;
    resolved_today: number;
    avg_response_time_minutes: number;
    sla_compliance_rate: number;
    avg_satisfaction_score: number;
    complaints_trend: { date: string; count: number }[];
    category_distribution: Record<string, number>;
    sentiment_distribution: Record<string, number>;
    priority_distribution: Record<string, number>;
}

export interface AgentPerformance {
    auto_resolved_rate: number;
    human_escalation_rate: number;
    avg_confidence_score: number;
    false_positive_rate: number;
    avg_iterations: number;
}

class ApiClient {
    private baseUrl: string;

    constructor() {
        this.baseUrl = API_BASE_URL;
    }

    private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options?.headers,
            },
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        return response.json();
    }

    // Complaints
    async getComplaints(params?: {
        status?: string;
        priority?: string;
        limit?: number;
        offset?: number;
    }): Promise<Complaint[]> {
        const searchParams = new URLSearchParams();
        if (params?.status) searchParams.set('status', params.status);
        if (params?.priority) searchParams.set('priority', params.priority);
        if (params?.limit) searchParams.set('limit', params.limit.toString());
        if (params?.offset) searchParams.set('offset', params.offset.toString());

        const query = searchParams.toString();
        return this.request<Complaint[]>(`/complaints${query ? `?${query}` : ''}`);
    }

    async getComplaint(id: string): Promise<ComplaintDetail> {
        return this.request<ComplaintDetail>(`/complaints/${id}`);
    }

    async createComplaint(data: CreateComplaintRequest): Promise<any> {
        return this.request('/complaints/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async updateComplaint(id: string, data: Partial<ComplaintDetail>): Promise<ComplaintDetail> {
        return this.request<ComplaintDetail>(`/complaints/${id}`, {
            method: 'PATCH',
            body: JSON.stringify(data),
        });
    }

    async getComplaintAudit(id: string): Promise<any[]> {
        return this.request<any[]>(`/complaints/${id}/audit`);
    }

    // Analytics
    async getAnalyticsOverview(days?: number): Promise<AnalyticsOverview> {
        const query = days ? `?days=${days}` : '';
        return this.request<AnalyticsOverview>(`/analytics/overview${query}`);
    }

    async getAgentPerformance(days?: number): Promise<AgentPerformance> {
        const query = days ? `?days=${days}` : '';
        return this.request<AgentPerformance>(`/analytics/agent-performance${query}`);
    }
}

export const api = new ApiClient();
