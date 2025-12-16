import { Car, User, LogOut } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import Notification from './Notifications';

const Navbar = () => {
    const { user, logout } = useAuth();

    return (
        <nav className="bg-white shadow-md">
            <div className="max-w-7xl mx-auto px-4 py-4">
                <div className="flex justify-between items-center">
                    <div className="flex items-center space-x-2">
                        <Car className="w-8 h-8 text-blue-600" />
                        <h1 className="text-2xl font-bold text-gray-800">TaxiBook</h1>
                    </div>

                    {user && (
                        <div className="flex items-center space-x-4">
                            <Notification />

                            <div className="flex items-center space-x-2">
                                <User className="w-6 h-6" />
                                <span className="text-sm font-medium">{user.email}</span>
                                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                                    {user.role}
                                </span>
                            </div>

                            <button
                                onClick={logout}
                                className="flex items-center space-x-1 text-red-600 hover:text-red-700"
                            >
                                <LogOut className="w-5 h-5" />
                                <span>Logout</span>
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </nav>
    );
};

export default Navbar;