import authService from './auth.service';

const API_BASE_URL = 'http://localhost:8001';

const rideService = {
    /**
     * Get all rides for current user
     */
    getRides: async () => {
        const response = await fetch(`${API_BASE_URL}/api/rides/`, {
            headers: authService.getAuthHeaders()
        });

        if (!response.ok) {
            throw new Error('Failed to fetch rides');
        }

        return response.json();
    },

    /**
     * Get specific ride by ID
     */
    getRide: async (rideId) => {
        const response = await fetch(`${API_BASE_URL}/api/rides/${rideId}/`, {
            headers: authService.getAuthHeaders()
        });

        if (!response.ok) {
            throw new Error('Failed to fetch ride');
        }

        return response.json();
    },

    /**
     * Create new ride request (passenger only)
     */
    createRide: async (origin, destination) => {
        const response = await fetch(`${API_BASE_URL}/api/rides/`, {
            method: 'POST',
            headers: authService.getAuthHeaders(),
            body: JSON.stringify({ origin, destination })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create ride');
        }

        return response.json();
    },

    /**
     * Accept ride (driver only)
     */
    acceptRide: async (rideId) => {
        const response = await fetch(`${API_BASE_URL}/api/rides/${rideId}/accept/`, {
            method: 'POST',
            headers: authService.getAuthHeaders()
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to accept ride');
        }

        return response.json();
    },

    /**
     * Reject ride (driver only)
     */
    rejectRide: async (rideId) => {
        const response = await fetch(`${API_BASE_URL}/api/rides/${rideId}/reject/`, {
            method: 'POST',
            headers: authService.getAuthHeaders()
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to reject ride');
        }

        return response.json();
    },

    /**
     * Complete ride (driver only)
     */
    completeRide: async (rideId) => {
        const response = await fetch(`${API_BASE_URL}/api/rides/${rideId}/complete/`, {
            method: 'POST',
            headers: authService.getAuthHeaders()
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to complete ride');
        }

        return response.json();
    },

    /**
     * Cancel ride (passenger or driver)
     */
    cancelRide: async (rideId, reason = '') => {
        const response = await fetch(`${API_BASE_URL}/api/rides/${rideId}/cancel/`, {
            method: 'POST',
            headers: authService.getAuthHeaders(),
            body: JSON.stringify({ reason })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to cancel ride');
        }

        return response.json();
    },

    /**
     * Get ride status (for polling)
     */
    getRideStatus: async (rideId) => {
        const response = await fetch(`${API_BASE_URL}/api/rides/${rideId}/status/`, {
            headers: authService.getAuthHeaders()
        });

        if (!response.ok) {
            throw new Error('Failed to fetch ride status');
        }

        return response.json();
    },

    /**
     * Poll for ride updates
     * Returns rides that have been updated since lastPollTime
     */
    pollRides: async (lastPollTime = null) => {
        let url = `${API_BASE_URL}/api/rides/`;

        if (lastPollTime) {
            url += `?since=${lastPollTime}`;
        }

        const response = await fetch(url, {
            headers: authService.getAuthHeaders()
        });

        if (!response.ok) {
            throw new Error('Failed to poll rides');
        }

        return response.json();
    },

    /**
     * Get ride history
     */
    getRideHistory: async (status = null) => {
        let url = `${API_BASE_URL}/api/rides/`;

        if (status) {
            url += `?status=${status}`;
        }

        const response = await fetch(url, {
            headers: authService.getAuthHeaders()
        });

        if (!response.ok) {
            throw new Error('Failed to fetch ride history');
        }

        return response.json();
    }
};

export default rideService;

