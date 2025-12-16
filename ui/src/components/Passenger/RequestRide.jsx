import { useState } from 'react';
import { MapPin, Navigation, DollarSign, Clock, Send, Car } from 'lucide-react';

const RequestRide = ({ onRideCreated }) => {
    const [origin, setOrigin] = useState('');
    const [destination, setDestination] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [estimatedPrice, setEstimatedPrice] = useState(null);

    const calculateEstimatedPrice = () => {
        if (!origin || !destination) return;

        // Simple price estimation (mock)
        const basePrice = 5.00;
        const pricePerKm = 2.50;
        const estimatedKm = Math.floor(Math.random() * 10) + 2;
        const total = basePrice + (pricePerKm * estimatedKm);

        setEstimatedPrice({
            distance: estimatedKm,
            price: total.toFixed(2)
        });
    };

    const handleRequestRide = async () => {
        if (!origin || !destination) {
            setError('Please enter both pickup and destination');
            return;
        }

        setError('');
        setLoading(true);

        try {
            const token = localStorage.getItem('access_token');

            const response = await fetch('http://localhost:8080/api/rides/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    origin,
                    destination
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to create ride');
            }

            const ride = await response.json();

            // Clear form
            setOrigin('');
            setDestination('');
            setEstimatedPrice(null);

            // Callback to parent
            if (onRideCreated) {
                onRideCreated(ride);
            }

        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center space-x-2 mb-6">
                <Car className="w-6 h-6 text-blue-600" />
                <h3 className="text-xl font-semibold">Request a Ride</h3>
            </div>

            <div className="space-y-4">
                {/* Pickup Location */}
                <div>
                    <label className="block text-sm font-medium mb-2">
                        <MapPin className="w-4 h-4 inline mr-2 text-green-600" />
                        Pickup Location
                    </label>
                    <input
                        type="text"
                        value={origin}
                        onChange={(e) => {
                            setOrigin(e.target.value);
                            setEstimatedPrice(null);
                        }}
                        onBlur={calculateEstimatedPrice}
                        placeholder="e.g., 123 Main Street, Downtown"
                        className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>

                {/* Destination */}
                <div>
                    <label className="block text-sm font-medium mb-2">
                        <Navigation className="w-4 h-4 inline mr-2 text-red-600" />
                        Destination
                    </label>
                    <input
                        type="text"
                        value={destination}
                        onChange={(e) => {
                            setDestination(e.target.value);
                            setEstimatedPrice(null);
                        }}
                        onBlur={calculateEstimatedPrice}
                        placeholder="e.g., Airport Terminal 2"
                        className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>

                {/* Estimated Price */}
                {estimatedPrice && (
                    <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                                <Clock className="w-5 h-5 text-blue-600" />
                                <span className="text-sm text-gray-700">
                                    Estimated: {estimatedPrice.distance} km
                                </span>
                            </div>
                            <div className="flex items-center space-x-1 text-lg font-bold text-blue-600">
                                <DollarSign className="w-5 h-5" />
                                <span>{estimatedPrice.price}</span>
                            </div>
                        </div>
                    </div>
                )}

                {/* Error Message */}
                {error && (
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
                        {error}
                    </div>
                )}

                {/* Submit Button */}
                <button
                    onClick={handleRequestRide}
                    disabled={loading || !origin || !destination}
                    className="w-full bg-blue-600 text-white py-3 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 font-medium"
                >
                    {loading ? (
                        <>
                            <Clock className="w-5 h-5 animate-spin" />
                            <span>Requesting...</span>
                        </>
                    ) : (
                        <>
                            <Send className="w-5 h-5" />
                            <span>Request Ride Now</span>
                        </>
                    )}
                </button>

                {/* Info Text */}
                <p className="text-xs text-gray-500 text-center mt-2">
                    Your ride will be matched with a nearby driver. You'll receive a notification when a driver accepts.
                </p>
            </div>
        </div>
    );
};

export default RequestRide;