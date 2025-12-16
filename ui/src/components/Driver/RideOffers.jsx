import { useState, useEffect } from 'react';
import { MapPin, Navigation, DollarSign, User, Check, X, Clock } from 'lucide-react';

const RideOffers = () => {
    const [rides, setRides] = useState([]);
    const [loading, setLoading] = useState(false);
    const [actionLoading, setActionLoading] = useState(null);

    useEffect(() => {
        loadRides();

        // Poll for new rides every 3 seconds
        const interval = setInterval(loadRides, 3000);
        return () => clearInterval(interval);
    }, []);

    const loadRides = async () => {
        try {
            const token = localStorage.getItem('access_token');

            const response = await fetch('http://localhost:8080/api/rides/', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) throw new Error('Failed to load rides');

            const data = await response.json();
            setRides(Array.isArray(data) ? data : []);
        } catch (error) {
            console.error('Failed to load rides:', error);
        }
    };

    const handleAcceptRide = async (rideId) => {
        setActionLoading(rideId);

        try {
            const token = localStorage.getItem('access_token');

            const response = await fetch(`http://localhost:8080/api/rides/${rideId}/accept/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to accept ride');
            }

            // Reload rides
            await loadRides();
        } catch (error) {
            alert(`Error: ${error.message}`);
        } finally {
            setActionLoading(null);
        }
    };

    const handleRejectRide = async (rideId) => {
        setActionLoading(rideId);

        try {
            const token = localStorage.getItem('access_token');

            const response = await fetch(`http://localhost:8080/api/rides/${rideId}/reject/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to reject ride');
            }

            // Reload rides
            await loadRides();
        } catch (error) {
            alert(`Error: ${error.message}`);
        } finally {
            setActionLoading(null);
        }
    };

    const handleCompleteRide = async (rideId) => {
        setActionLoading(rideId);

        try {
            const token = localStorage.getItem('access_token');

            const response = await fetch(`http://localhost:8080/api/rides/${rideId}/complete/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to complete ride');
            }

            // Reload rides
            await loadRides();
        } catch (error) {
            alert(`Error: ${error.message}`);
        } finally {
            setActionLoading(null);
        }
    };

    const getStatusBadge = (status) => {
        const statusConfig = {
            requested: { color: 'bg-yellow-100 text-yellow-800', text: 'Requested' },
            offered: { color: 'bg-blue-100 text-blue-800', text: 'Offered to You' },
            accepted: { color: 'bg-green-100 text-green-800', text: 'Accepted' },
            completed: { color: 'bg-gray-100 text-gray-800', text: 'Completed' },
            cancelled: { color: 'bg-red-100 text-red-800', text: 'Cancelled' }
        };

        const config = statusConfig[status] || statusConfig.requested;

        return (
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${config.color}`}>
                {config.text}
            </span>
        );
    };

    return (
        <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold">Available Rides</h3>
                <button
                    onClick={loadRides}
                    disabled={loading}
                    className="text-blue-600 hover:text-blue-700 text-sm"
                >
                    {loading ? 'Refreshing...' : 'Refresh'}
                </button>
            </div>

            {rides.length === 0 ? (
                <div className="text-center py-12">
                    <Clock className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-500">No rides available at the moment</p>
                    <p className="text-sm text-gray-400 mt-2">New ride requests will appear here</p>
                </div>
            ) : (
                <div className="space-y-4">
                    {rides.map(ride => (
                        <div key={ride.id} className="border border-gray-200 rounded-lg p-5 hover:border-blue-300 transition">
                            {/* Header */}
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center space-x-3">
                                    {getStatusBadge(ride.status)}
                                    <span className="text-sm text-gray-500">Ride #{ride.id}</span>
                                </div>
                                {ride.price && (
                                    <div className="flex items-center space-x-1 text-lg font-bold text-green-600">
                                        <DollarSign className="w-5 h-5" />
                                        <span>{ride.price}</span>
                                    </div>
                                )}
                            </div>

                            {/* Route Details */}
                            <div className="space-y-3 mb-4">
                                <div className="flex items-start space-x-3">
                                    <MapPin className="w-5 h-5 text-green-600 mt-0.5" />
                                    <div className="flex-1">
                                        <p className="text-xs text-gray-500 mb-1">PICKUP</p>
                                        <p className="text-sm font-medium">{ride.origin}</p>
                                    </div>
                                </div>

                                <div className="border-l-2 border-dashed border-gray-300 ml-2 h-4"></div>

                                <div className="flex items-start space-x-3">
                                    <Navigation className="w-5 h-5 text-red-600 mt-0.5" />
                                    <div className="flex-1">
                                        <p className="text-xs text-gray-500 mb-1">DESTINATION</p>
                                        <p className="text-sm font-medium">{ride.destination}</p>
                                    </div>
                                </div>
                            </div>

                            {/* Passenger Info */}
                            <div className="flex items-center space-x-2 mb-4 text-sm text-gray-600">
                                <User className="w-4 h-4" />
                                <span>Passenger #{ride.passenger}</span>
                            </div>

                            {/* Action Buttons */}
                            <div className="flex space-x-3">
                                {ride.status === 'offered' && (
                                    <>
                                        <button
                                            onClick={() => handleAcceptRide(ride.id)}
                                            disabled={actionLoading === ride.id}
                                            className="flex-1 bg-green-600 text-white py-2 rounded-md hover:bg-green-700 disabled:opacity-50 flex items-center justify-center space-x-2"
                                        >
                                            <Check className="w-4 h-4" />
                                            <span>Accept</span>
                                        </button>
                                        <button
                                            onClick={() => handleRejectRide(ride.id)}
                                            disabled={actionLoading === ride.id}
                                            className="flex-1 bg-red-600 text-white py-2 rounded-md hover:bg-red-700 disabled:opacity-50 flex items-center justify-center space-x-2"
                                        >
                                            <X className="w-4 h-4" />
                                            <span>Reject</span>
                                        </button>
                                    </>
                                )}

                                {ride.status === 'accepted' && (
                                    <button
                                        onClick={() => handleCompleteRide(ride.id)}
                                        disabled={actionLoading === ride.id}
                                        className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center space-x-2"
                                    >
                                        <Check className="w-4 h-4" />
                                        <span>Complete Ride</span>
                                    </button>
                                )}

                                {ride.status === 'completed' && (
                                    <div className="w-full text-center py-2 text-gray-500 text-sm">
                                        ✓ Ride completed
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default RideOffers;