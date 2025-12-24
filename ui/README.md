# TaxiBook Frontend

Modern React-based single-page application for the TaxiBook ride-sharing platform.

##  Overview

The frontend provides separate interfaces for:
- **Passengers**: Request rides, track status, view ride history
- **Drivers**: View ride offers, accept/reject rides, complete rides
- **Both**: Authentication, profile management, real-time notifications

##  Architecture

```
┌─────────────────────────────────────┐
│         React Application           │
│          (Port 3000)                │
├─────────────────────────────────────┤
│  Components                         │
│  • Auth (Login/Register)            │
│  • Passenger Dashboard              │
│  • Driver Dashboard                 │
│  • Notification Bell                │
│  • Navbar                           │
├─────────────────────────────────────┤
│  Context                            │
│  • AuthContext (User state)         │
├─────────────────────────────────────┤
│  Services                           │
│  • api.js (HTTP calls)              │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│       Traefik API Gateway           │
│        (Port 8080)                  │
│                                     │
│  Routes to:                         │
│  • Auth Service                     │
│  • Ride Service                     │
└─────────────────────────────────────┘
```

##  Features

### Authentication
-  User registration (passengers only)
-  Login (passenger/driver toggle)
-  JWT token management
-  Auto-login from stored tokens
-  Logout with token blacklisting

### Passenger Features
-  Request rides with origin/destination
-  Real-time ride status updates
-  View ride history
-  Cancel pending rides
-  Notification system

### Driver Features
-  View available ride offers
-  Accept/reject ride requests
-  Complete rides
-  Real-time ride updates
-  Earnings tracking

### Shared Features
-  Real-time notification bell
-  Polling-based updates (3-5 seconds)
-  Profile management
-  Responsive design
-  Status badges and indicators

##  Tech Stack

- **Framework**: React 18.2.0
- **Build Tool**: Vite 4.3.9
- **Styling**: Tailwind CSS 4.1.18
- **Icons**: Lucide React 0.263.1
- **HTTP Client**: Fetch API
- **State Management**: React Context API
- **Routing**: Conditional rendering (no react-router)

## Installation

### Prerequisites
- Node.js 18+
- npm or yarn
- Backend services running (Auth + Ride + Traefik)

### Setup

1. **Navigate to frontend directory**
```bash
cd ui
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure API endpoints**

Edit `src/services/api.js`:
```javascript
// For local development
export const AUTH_URL = 'http://localhost:8080';
export const RIDE_URL = 'http://localhost:8080';

// For multi-PC deployment
export const AUTH_URL = 'http://10.70.95.95:8080';  // PC1 (Leader)
export const RIDE_URL = 'http://10.70.95.95:8080';
```

4. **Run development server**
```bash
npm run dev
```

5. **Access application**
```
http://localhost:3000
```

##  Project Structure

```
ui/
├── public/
├── src/
│   ├── components/
│   │   ├── Auth/
│   │   │   ├── Login.jsx
│   │   │   └── Register.jsx
│   │   ├── Passenger/
│   │   │   ├── PassengerDashboard.jsx
│   │   │   └── RequestRide.jsx
│   │   ├── Driver/
│   │   │   ├── DriverDashboard.jsx
│   │   │   └── RideOffers.jsx
│   │   └── Shared/
│   │       ├── Navbar.jsx
│   │       └── Notifications.jsx
│   ├── context/
│   │   └── AuthContext.jsx
│   ├── services/
│   │   ├── api.js
│   │   ├── auth.service.js
│   │   ├── ride.service.js
│   │   └── notification.service.js
│   ├── utils/
│   │   ├── validators.js
│   │   └── websocket.js
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

##  State Management

### AuthContext
Manages user authentication state:

```javascript
const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const login = async (email, password, isDriver) => {
    // Call API, store tokens, update user state
  };

  const logout = () => {
    // Clear tokens and user state
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
```

### Local Storage
```javascript
// Token storage
localStorage.setItem('access_token', token);
localStorage.setItem('refresh_token', refreshToken);
localStorage.setItem('user_data', JSON.stringify(user));

// Token retrieval
const token = localStorage.getItem('access_token');
const user = JSON.parse(localStorage.getItem('user_data'));
```

##  API Integration

### API Service (`src/services/api.js`)

```javascript
// Base URLs
export const AUTH_URL = 'http://localhost:8080';
export const RIDE_URL = 'http://localhost:8080';

// Helper function
const getAuthHeaders = () => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${localStorage.getItem('access_token')}`
});

// Login
export const login = async (email, password) => {
  const response = await fetch(`${AUTH_URL}/accounts/api/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  return response.json();
};

// Get rides
export const getRides = async () => {
  const response = await fetch(`${RIDE_URL}/api/rides/`, {
    headers: getAuthHeaders()
  });
  return response.json();
};

// Create ride
export const createRide = async (origin, destination) => {
  const response = await fetch(`${RIDE_URL}/api/rides/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ origin, destination })
  });
  return response.json();
};
```

##  Real-time Updates

### Polling Strategy

Instead of WebSockets, we use polling for simplicity:

```javascript
// Poll for ride updates every 3 seconds
useEffect(() => {
  loadRides();
  const interval = setInterval(loadRides, 3000);
  return () => clearInterval(interval);
}, []);

// Poll for new notifications every 5 seconds
useEffect(() => {
  const interval = setInterval(() => {
    pollNewNotifications();
  }, 5000);
  return () => clearInterval(interval);
}, []);
```

### Notification System

```javascript
const [notifications, setNotifications] = useState([]);
const [lastPoll, setLastPoll] = useState(new Date().toISOString());

const pollNewNotifications = async () => {
  try {
    const data = await api.pollNotifications(lastPoll);
    if (data.count > 0) {
      setNotifications(prev => [...data.notifications, ...prev]);
      setLastPoll(data.timestamp);
    }
  } catch (error) {
    console.error('Failed to poll notifications:', error);
  }
};
```

## Styling

### Tailwind CSS Classes

Common patterns used throughout:

```jsx
// Buttons
<button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
  Click Me
</button>

// Cards
<div className="bg-white rounded-lg shadow-md p-6">
  Content
</div>

// Status badges
<span className="px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
  Accepted
</span>

// Input fields
<input 
  type="text"
  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
/>
```

### Responsive Design

```jsx
// Mobile-first approach
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* Responsive grid */}
</div>

// Responsive text
<h1 className="text-2xl md:text-3xl lg:text-4xl font-bold">
  Title
</h1>
```

## Testing

### Manual Testing Flow

1. **Register as Passenger**
   - Open http://localhost:3000
   - Click "Register here"
   - Fill form and submit
   - Should auto-login

2. **Request a Ride**
   - Enter pickup location
   - Enter destination
   - Click "Request Ride Now"
   - Watch status change from "requested" → "offered" → "accepted"

3. **Test Notifications**
   - Click notification bell (top right)
   - Should show ride status updates
   - Click notification to mark as read

4. **Test Driver Interface**
   - Logout
   - Login with driver account (check "Login as Driver")
   - Should see available ride offers
   - Click "Accept" on a ride
   - Click "Complete" when done

### Browser Console Testing

```javascript
// Check stored tokens
console.log(localStorage.getItem('access_token'));

// Check user data
console.log(JSON.parse(localStorage.getItem('user_data')));

// Test API call
fetch('http://localhost:8080/api/rides/', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
}).then(r => r.json()).then(console.log);
```

##  Deployment

### Build for Production

```bash
npm run build
```

Output will be in `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

### Deploy to Static Hosting

```bash
# Example: Deploy to Netlify
npm run build
netlify deploy --prod --dir=dist

# Example: Deploy to Vercel
npm run build
vercel --prod
```

### Environment-specific Configuration

Create `.env.production`:
```env
VITE_API_URL=https://api.taxibook.com
VITE_AUTH_URL=https://api.taxibook.com
```

Update `vite.config.js`:
```javascript
export default defineConfig({
  plugins: [react()],
  define: {
    'import.meta.env.VITE_API_URL': JSON.stringify(process.env.VITE_API_URL)
  }
});
```

## 📝 Configuration Files

### vite.config.js
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/accounts': {
        target: 'http://10.70.95.95:8080',
        changeOrigin: true
      },
      '/api': {
        target: 'http://10.70.95.95:8080',
        changeOrigin: true
      }
    }
  }
})
```

### tailwind.config.js
```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          500: '#3b82f6',
          600: '#2563eb',
        }
      }
    },
  },
  plugins: [],
}
```

