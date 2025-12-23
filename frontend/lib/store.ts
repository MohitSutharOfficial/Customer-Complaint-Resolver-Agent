import { create } from 'zustand';
import { Complaint, ComplaintDetail, AnalyticsOverview, AgentPerformance, api } from './api';

interface AppState {
    // Complaints
    complaints: Complaint[];
    selectedComplaint: ComplaintDetail | null;
    isLoadingComplaints: boolean;

    // Analytics
    analytics: AnalyticsOverview | null;
    agentPerformance: AgentPerformance | null;
    isLoadingAnalytics: boolean;

    // Filters
    statusFilter: string | null;
    priorityFilter: string | null;

    // Actions
    fetchComplaints: () => Promise<void>;
    fetchComplaint: (id: string) => Promise<void>;
    fetchAnalytics: (days?: number) => Promise<void>;
    fetchAgentPerformance: (days?: number) => Promise<void>;
    setStatusFilter: (status: string | null) => void;
    setPriorityFilter: (priority: string | null) => void;
    clearSelectedComplaint: () => void;
}

export const useStore = create<AppState>((set, get) => ({
    // Initial state
    complaints: [],
    selectedComplaint: null,
    isLoadingComplaints: false,
    analytics: null,
    agentPerformance: null,
    isLoadingAnalytics: false,
    statusFilter: null,
    priorityFilter: null,

    // Actions
    fetchComplaints: async () => {
        set({ isLoadingComplaints: true });
        try {
            const { statusFilter, priorityFilter } = get();
            const complaints = await api.getComplaints({
                status: statusFilter || undefined,
                priority: priorityFilter || undefined,
            });
            set({ complaints, isLoadingComplaints: false });
        } catch (error) {
            console.error('Failed to fetch complaints:', error);
            set({ isLoadingComplaints: false });
        }
    },

    fetchComplaint: async (id: string) => {
        try {
            const complaint = await api.getComplaint(id);
            set({ selectedComplaint: complaint });
        } catch (error) {
            console.error('Failed to fetch complaint:', error);
        }
    },

    fetchAnalytics: async (days = 7) => {
        set({ isLoadingAnalytics: true });
        try {
            const analytics = await api.getAnalyticsOverview(days);
            set({ analytics, isLoadingAnalytics: false });
        } catch (error) {
            console.error('Failed to fetch analytics:', error);
            set({ isLoadingAnalytics: false });
        }
    },

    fetchAgentPerformance: async (days = 7) => {
        try {
            const agentPerformance = await api.getAgentPerformance(days);
            set({ agentPerformance });
        } catch (error) {
            console.error('Failed to fetch agent performance:', error);
        }
    },

    setStatusFilter: (status) => {
        set({ statusFilter: status });
        get().fetchComplaints();
    },

    setPriorityFilter: (priority) => {
        set({ priorityFilter: priority });
        get().fetchComplaints();
    },

    clearSelectedComplaint: () => {
        set({ selectedComplaint: null });
    },
}));
