import { useState, useEffect } from 'react';
import { MapPin, Navigation, Check, X } from 'lucide-react';
import * as api from '../../services/api';

const DriverDashboard = () => {
    const [rides, setRides] = useState([]);

    useEffect(() => {
        loadRides();

        // Poll for new ride offers every 3 seconds
        const interval = setInterval(loadRides, 3000);
        return () => clearInterval(interval);
    }, []);

    const loadRides = async () => {
        try {
            const data = await api.getRides();
            setRides(Array.isArray(data) ? data : []);
        } catch (error) {
            console.error('Failed to load rides:', error);
        }
    };

    const handleAcceptRide = async (rideId) => {
        try {
            await api.acceptRide(rideId);
            loadRides();
        } catch (error) {
            console.error('Failed to accept ride:', error);
        }
    };

    const handleRejectRide = async (rideId) => {
        try {
            await api.rejectRide(rideId);
            loadRides();
        } catch (error) {
            console.error('Failed to reject ride:', error);
        }
    };

    const handleCompleteRide = async (rideId) => {
        try {
            await api.completeRide(rideId);
            loadRides();
        } catch (error) {
            console.error('Failed to complete ride:', error);
        }
    };

    const getStatusColor = (status) => {
        const colors = {
            requested: 'bg-yellow-100 text-yellow-800',
            offered: 'bg-blue-100 text-blue-800',
            accepted: 'bg-green-100 text-green-800',
            completed: 'bg-gray-100 text-gray-800',
            cancelled: 'bg-red-100 text-red-800'
        };
        return colors[status] || 'bg-gray-100 text-gray-800';
    };

    return (
        <div className="max-w-7xl mx-auto px-4 py-8">
            <h2 className="text-3xl font-bold mb-8">Driver Dashboard</h2>

            {/* Ride Offers */}
            <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-xl font-semibold mb-4">Available Rides</h3>

                {rides.length === 0 ? (
                    <p className="text-gray-500 text-center py-8">No rides available</p>
                ) : (
                    <div className="space-y-4">
                        {rides.map(ride => (
                            <div key={ride.id} className="border border-gray-200 rounded-lg p-4">
                                <div className="flex justify-between items-start">
                                    <div className="flex-1">
                                        <div className="flex items-center space-x-2 mb-2">
                                            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(ride.status)}`}>
                                                {ride.status}
                                            </span>
                                            <span className="text-sm text-gray-500">
                                                Ride #{ride.id}
                                            </span>
                                        </div>

                                        <div className="space-y-1">
                                            <p className="flex items-center text-sm">
                                                <MapPin className="w-4 h-4 mr-2 text-green-600" />
                                                <strong>From:</strong> <span className="ml-2">{ride.origin}</span>
                                            </p>
                                            <p className="flex items-center text-sm">
                                                <Navigation className="w-4 h-4 mr-2 text-red-600" />
                                                <strong>To:</strong> <span className="ml-2">{ride.destination}</span>
                                            </p>
                                        </div>

                                        <p className="text-sm text-gray-600 mt-2">
                                            Passenger: #{ride.passenger}
                                        </p>

                                        {ride.price && (
                                            <p className="text-lg font-bold text-green-600 mt-2">
                                                ${ride.price}
                                            </p>
                                        )}
                                    </div>

                                    <div className="flex flex-col space-y-2 ml-4">
                                        {ride.status === 'offered' && (
                                            <>
                                                <button
                                                    onClick={() => handleAcceptRide(ride.id)}
                                                    className="flex items-center space-x-1 bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
                                                >
                                                    <Check className="w-4 h-4" />
                                                    <span>Accept</span>
                                                </button>
                                                <button
                                                    onClick={() => handleRejectRide(ride.id)}
                                                    className="flex items-center space-x-1 bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
                                                >
                                                    <X className="w-4 h-4" />
                                                    <span>Reject</span>
                                                </button>
                                            </>
                                        )}

                                        {ride.status === 'accepted' && (
                                            <button
                                                onClick={() => handleCompleteRide(ride.id)}
                                                className="flex items-center space-x-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                                            >
                                                <Check className="w-4 h-4" />
                                                <span>Complete</span>
                                            </button>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default DriverDashboard;