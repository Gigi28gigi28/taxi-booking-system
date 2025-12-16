import React from 'react';
import authService from '../services/auth.service';

const ProtectedRoute = ({ children, requiredRole = null }) => {
    const user = authService.getCurrentUser();
    const isAuthenticated = authService.isAuthenticated();

    // Not authenticated - redirect to login
    if (!isAuthenticated || !user) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-100">
                <div className="bg-white p-8 rounded-lg shadow-md text-center">
                    <h2 className="text-2xl font-bold mb-4">Access Denied</h2>
                    <p className="text-gray-600 mb-4">Please login to continue</p>
                    <button
                        onClick={() => window.location.reload()}
                        className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700"
                    >
                        Go to Login
                    </button>
                </div>
            </div>
        );
    }

    // Check role if required
    if (requiredRole && user.role !== requiredRole) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-100">
                <div className="bg-white p-8 rounded-lg shadow-md text-center">
                    <h2 className="text-2xl font-bold mb-4">Access Denied</h2>
                    <p className="text-gray-600 mb-4">
                        You don't have permission to access this page
                    </p>
                    <p className="text-sm text-gray-500">
                        Required role: {requiredRole} | Your role: {user.role}
                    </p>
                </div>
            </div>
        );
    }

    return children;
};

export default ProtectedRoute;