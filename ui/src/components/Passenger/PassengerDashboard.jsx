import { useState, useEffect } from 'react';
import { MapPin, Navigation } from 'lucide-react';
import * as api from '../../services/api';

const PassengerDashboard = () => {
    const [rides, setRides] = useState([]);
    const [origin, setOrigin] = useState('');
    const [destination, setDestination] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        loadRides();

        // Poll for ride updates every 3 seconds
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

    const handleRequestRide = async () => {
        if (!origin || !destination) {
            setError('Both origin and destination are required');
            return;
        }

        setError('');
        setLoading(true);

        try {
            await api.createRide(origin, destination);
            setOrigin('');
            setDestination('');
            loadRides();
        } catch (error) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    const handleCancelRide = async (rideId) => {
        try {
            await api.cancelRide(rideId, 'Passenger cancelled');
            loadRides();
        } catch (error) {
            console.error('Failed to cancel ride:', error);
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
            <h2 className="text-3xl font-bold mb-8">Passenger Dashboard</h2>

            {/* Request Ride Card */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-8">
                <h3 className="text-xl font-semibold mb-4">Request a Ride</h3>

                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium mb-1">
                            <MapPin className="w-4 h-4 inline mr-1" />
                            Pickup Location
                        </label>
                        <input
                            type="text"
                            value={origin}
                            onChange={(e) => setOrigin(e.target.value)}
                            placeholder="Enter pickup address"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-1">
                            <Navigation className="w-4 h-4 inline mr-1" />
                            Destination
                        </label>
                        <input
                            type="text"
                            value={destination}
                            onChange={(e) => setDestination(e.target.value)}
                            placeholder="Enter destination"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md"
                        />
                    </div>

                    {error && (
                        <div className="text-red-600 text-sm">{error}</div>
                    )}

                    <button
                        onClick={handleRequestRide}
                        disabled={loading}
                        className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
                    >
                        {loading ? 'Requesting...' : 'Request Ride'}
                    </button>
                </div>
            </div>

            {/* My Rides */}
            <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-xl font-semibold mb-4">My Rides</h3>

                {rides.length === 0 ? (
                    <p className="text-gray-500 text-center py-8">No rides yet</p>
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

                                        {ride.driver && (
                                            <p className="text-sm text-gray-600 mt-2">
                                                Driver: #{ride.driver}
                                            </p>
                                        )}

                                        {ride.price && (
                                            <p className="text-lg font-bold text-green-600 mt-2">
                                                ${ride.price}
                                            </p>
                                        )}
                                    </div>

                                    {ride.status === 'requested' && (
                                        <button
                                            onClick={() => handleCancelRide(ride.id)}
                                            className="text-red-600 hover:text-red-700 text-sm"
                                        >
                                            Cancel
                                        </button>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default PassengerDashboard;