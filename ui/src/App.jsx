import { Clock } from 'lucide-react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import Navbar from './components/Shared/Navbar';
import PassengerDashboard from './components/Passenger/PassengerDashboard';
import DriverDashboard from './components/Driver/DriverDashboard';
import { useState } from 'react';

const App = () => {
  const { user, loading } = useAuth();
  const [showRegister, setShowRegister] = useState(false);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Clock className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!user) {
    // Show Register or Login based on state
    return showRegister ? (
      <Register onSwitchToLogin={() => setShowRegister(false)} />
    ) : (
      <Login onSwitchToRegister={() => setShowRegister(true)} />
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar />
      {user.role === 'passager' || user.role === 'passenger' ? (
        <PassengerDashboard />
      ) : (
        <DriverDashboard />
      )}
    </div>
  );
};

const Root = () => (
  <AuthProvider>
    <App />
  </AuthProvider>
);

export default Root;