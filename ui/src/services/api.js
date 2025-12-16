// API Configuration - Route through Traefik Gateway
const GATEWAY_URL = 'http://localhost:8080';  // Traefik routes everything

const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token');
    return {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
    };
};

// ============================================
// AUTH ENDPOINTS (via Traefik → Auth Service)
// ============================================

export const login = async (email, password) => {
    const response = await fetch(`${GATEWAY_URL}/accounts/api/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || error.message || 'Login failed');
    }

    return response.json();
};

export const chauffeurLogin = async (email, password) => {
    const response = await fetch(`${GATEWAY_URL}/accounts/api/chauffeur/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || error.message || 'Chauffeur login failed');
    }

    return response.json();
};

export const register = async (email, password, nom, prenom) => {
    const response = await fetch(`${GATEWAY_URL}/accounts/api/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, password2: password, nom, prenom }),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || error.email?.[0] || 'Registration failed');
    }

    return response.json();
};

// ============================================
// RIDE ENDPOINTS (via Traefik → Ride Service)
// ============================================

export const getRides = async () => {
    const response = await fetch(`${GATEWAY_URL}/api/rides/`, {
        headers: getAuthHeaders(),
    });

    if (!response.ok) {
        throw new Error('Failed to fetch rides');
    }

    return response.json();
};

export const createRide = async (origin, destination) => {
    const response = await fetch(`${GATEWAY_URL}/api/rides/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ origin, destination }),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create ride');
    }

    return response.json();
};

export const acceptRide = async (rideId) => {
    const response = await fetch(`${GATEWAY_URL}/api/rides/${rideId}/accept/`, {
        method: 'POST',
        headers: getAuthHeaders(),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to accept ride');
    }

    return response.json();
};

export const rejectRide = async (rideId) => {
    const response = await fetch(`${GATEWAY_URL}/api/rides/${rideId}/reject/`, {
        method: 'POST',
        headers: getAuthHeaders(),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to reject ride');
    }

    return response.json();
};

export const completeRide = async (rideId) => {
    const response = await fetch(`${GATEWAY_URL}/api/rides/${rideId}/complete/`, {
        method: 'POST',
        headers: getAuthHeaders(),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to complete ride');
    }

    return response.json();
};

export const cancelRide = async (rideId, reason) => {
    const response = await fetch(`${GATEWAY_URL}/api/rides/${rideId}/cancel/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ reason }),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to cancel ride');
    }

    return response.json();
};

// ============================================
// NOTIFICATION ENDPOINTS (via Traefik → Ride Service)
// ============================================

export const getNotifications = async () => {
    const response = await fetch(`${GATEWAY_URL}/api/notifications/`, {
        headers: getAuthHeaders(),
    });

    if (!response.ok) {
        throw new Error('Failed to fetch notifications');
    }

    return response.json();
};

export const pollNotifications = async (since) => {
    const response = await fetch(`${GATEWAY_URL}/api/notifications/poll/?since=${since}`, {
        headers: getAuthHeaders(),
    });

    if (!response.ok) {
        throw new Error('Failed to poll notifications');
    }

    return response.json();
};

export const markNotificationRead = async (notificationId) => {
    const response = await fetch(`${GATEWAY_URL}/api/notifications/${notificationId}/mark_as_read/`, {
        method: 'POST',
        headers: getAuthHeaders(),
    });

    if (!response.ok) {
        throw new Error('Failed to mark notification as read');
    }

    return response.json();
};