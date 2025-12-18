// Base URLs
export const AUTH_URL = 'http://10.70.95.95:8080';  // Traefik gateway → auth-service
export const RIDE_URL = 'http://10.70.95.95:8080';  // Traefik gateway → ride-service

const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token');
    return {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
    };
};

// ================= AUTH =================

export const login = async (email, password) => {
    const response = await fetch(`${AUTH_URL}/accounts/api/login/`, {
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

export const register = async (email, password, nom, prenom) => {
    const response = await fetch(`${AUTH_URL}/accounts/api/register/`, {
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

// ================= RIDE =================

export const getRides = async () => {
    const response = await fetch(`${RIDE_URL}/api/rides/`, { headers: getAuthHeaders() });
    if (!response.ok) throw new Error('Failed to fetch rides');
    return response.json();
};

export const createRide = async (origin, destination) => {
    const response = await fetch(`${RIDE_URL}/api/rides/`, {
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

// ================= NOTIFICATIONS =================

export const getNotifications = async () => {
    const response = await fetch(`${RIDE_URL}/api/notifications/`, { headers: getAuthHeaders() });
    if (!response.ok) throw new Error('Failed to fetch notifications');
    return response.json();
};
