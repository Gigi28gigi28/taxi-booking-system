const API_BASE_URL = 'http://localhost:8000';

const authService = {
    /**
     * Login user (passenger)
     */
    login: async (email, password) => {
        const response = await fetch(`${API_BASE_URL}/accounts/api/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }

        const data = await response.json();

        // Store tokens and user data
        localStorage.setItem('access_token', data.tokens.access);
        localStorage.setItem('refresh_token', data.tokens.refresh);
        localStorage.setItem('user_data', JSON.stringify(data.user));

        return data;
    },

    /**
     * Login chauffeur
     */
    chauffeurLogin: async (email, password) => {
        const response = await fetch(`${API_BASE_URL}/accounts/api/chauffeur/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Chauffeur login failed');
        }

        const data = await response.json();

        // Store tokens and user data
        localStorage.setItem('access_token', data.tokens.access);
        localStorage.setItem('refresh_token', data.tokens.refresh);
        localStorage.setItem('user_data', JSON.stringify(data.user));

        return data;
    },

    /**
     * Register new user (passenger)
     */
    register: async (email, password, nom, prenom) => {
        const response = await fetch(`${API_BASE_URL}/accounts/api/register/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email,
                password,
                password2: password,
                nom,
                prenom
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.email?.[0] || error.detail || 'Registration failed');
        }

        const data = await response.json();

        // Store tokens and user data
        localStorage.setItem('access_token', data.tokens.access);
        localStorage.setItem('refresh_token', data.tokens.refresh);
        localStorage.setItem('user_data', JSON.stringify(data.user));

        return data;
    },

    /**
     * Logout user
     */
    logout: async () => {
        const refreshToken = localStorage.getItem('refresh_token');

        if (refreshToken) {
            try {
                await fetch(`${API_BASE_URL}/accounts/api/logout/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ refresh: refreshToken })
                });
            } catch (error) {
                console.error('Logout error:', error);
            }
        }

        // Clear local storage
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_data');
    },

    /**
     * Get current user from localStorage
     */
    getCurrentUser: () => {
        const userData = localStorage.getItem('user_data');
        return userData ? JSON.parse(userData) : null;
    },

    /**
     * Get access token
     */
    getAccessToken: () => {
        return localStorage.getItem('access_token');
    },

    /**
     * Check if user is authenticated
     */
    isAuthenticated: () => {
        return !!localStorage.getItem('access_token');
    },

    /**
     * Refresh access token
     */
    refreshToken: async () => {
        const refreshToken = localStorage.getItem('refresh_token');

        if (!refreshToken) {
            throw new Error('No refresh token available');
        }

        const response = await fetch(`${API_BASE_URL}/api/token/refresh/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh: refreshToken })
        });

        if (!response.ok) {
            throw new Error('Token refresh failed');
        }

        const data = await response.json();
        localStorage.setItem('access_token', data.access);

        return data.access;
    },

    /**
     * Get auth headers for API calls
     */
    getAuthHeaders: () => {
        const token = authService.getAccessToken();
        return {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
        };
    }
};

export default authService;
