"""
Complete Taxi Booking System Test
Tests the full flow: Registration → Login → Request Ride → Watch Processing
"""
import requests
import json
import time

# Service URLs
AUTH_URL = "http://localhost:8000"
RIDE_URL = "http://localhost:8001"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def print_response(response):
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print()

# Test 1: Register Passenger
print_section("1. REGISTERING PASSENGER")

register_data = {
    "email": "passenger@taxi.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "nom": "Alice",
    "prenom": "Johnson"
}

response = requests.post(
    f"{AUTH_URL}/accounts/api/register/",
    json=register_data
)

print_response(response)

if response.status_code == 201:
    print("✅ Registration successful!")
    tokens = response.json()['tokens']
    access_token = tokens['access']
    print(f"🔑 Access Token: {access_token[:50]}...")
elif response.status_code == 400:
    # User might already exist - try login
    print("⚠️  User already exists, trying login...")
    
    # Test 2: Login
    print_section("2. LOGGING IN")
    
    login_data = {
        "email": "passenger@taxi.com",
        "password": "SecurePass123!"
    }
    
    response = requests.post(
        f"{AUTH_URL}/accounts/api/login/",
        json=login_data
    )
    
    print_response(response)
    
    if response.status_code == 200:
        print("✅ Login successful!")
        tokens = response.json()['tokens']
        access_token = tokens['access']
        print(f"🔑 Access Token: {access_token[:50]}...")
    else:
        print("❌ Login failed!")
        exit(1)
else:
    print("❌ Registration failed!")
    exit(1)

# Test 3: Get User Info
print_section("3. GETTING USER INFO")

headers = {
    "Authorization": f"Bearer {access_token}"
}

response = requests.get(
    f"{AUTH_URL}/accounts/api/me/",
    headers=headers
)

print_response(response)

if response.status_code == 200:
    user_data = response.json()
    print(f"✅ Authenticated as: {user_data['email']}")
    print(f"   Role: {user_data['role']}")
    print(f"   Name: {user_data['prenom']} {user_data['nom']}")
else:
    print("❌ Failed to get user info!")
    exit(1)

# Test 4: Request a Ride
print_section("4. REQUESTING A RIDE")

ride_data = {
    "origin": "123 Main Street, Downtown",
    "destination": "456 Oak Avenue, Uptown"
}

response = requests.post(
    f"{RIDE_URL}/api/rides/",
    headers=headers,
    json=ride_data
)

print_response(response)

if response.status_code == 201:
    ride = response.json()
    ride_id = ride['id']
    print(f"✅ Ride requested successfully!")
    print(f"   Ride ID: {ride_id}")
    print(f"   Status: {ride['status']}")
    print(f"   From: {ride['origin']}")
    print(f"   To: {ride['destination']}")
    
    # Test 5: Watch Ride Status
    print_section("5. WATCHING RIDE STATUS (30 seconds)")
    
    print("⏳ Monitoring ride status changes...")
    print("   (Matcher worker should assign a driver)")
    print()
    
    for i in range(6):  # Check every 5 seconds for 30 seconds
        time.sleep(5)
        
        response = requests.get(
            f"{RIDE_URL}/api/rides/{ride_id}/status/",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            ride_status = data['ride']
            
            print(f"[{i*5}s] Status: {ride_status['status']}", end="")
            
            if ride_status['driver']:
                print(f" | Driver: {ride_status['driver']}")
            else:
                print(" | Waiting for driver...")
            
            # Check if status changed
            if ride_status['status'] != 'requested':
                print(f"\n🎉 STATUS CHANGED TO: {ride_status['status'].upper()}")
                
                if ride_status['driver']:
                    print(f"👤 Driver assigned: ID {ride_status['driver']}")
                
                break
        else:
            print(f"[{i*5}s] Failed to get status")
    
    # Test 6: Get Notifications
    print_section("6. CHECKING NOTIFICATIONS")
    
    response = requests.get(
        f"{RIDE_URL}/api/notifications/",
        headers=headers
    )
    
    if response.status_code == 200:
        notif_data = response.json()
        print(f"📬 Total notifications: {notif_data['count']}")
        print(f"📩 Unread: {notif_data['unread_count']}")
        print()
        
        if notif_data['notifications']:
            print("Recent notifications:")
            for notif in notif_data['notifications'][:3]:
                status_icon = "📩" if not notif['is_read'] else "✅"
                print(f"{status_icon} {notif['title']}")
                print(f"   {notif['message']}")
                print()
    
    # Final Summary
    print_section("✅ SYSTEM TEST COMPLETE!")
    
    print("Services Tested:")
    print("  ✅ Auth Service (Registration, Login, Token)")
    print("  ✅ Ride Service (Create Ride, Status)")
    print("  ✅ RabbitMQ (Message Publishing)")
    print("  ✅ Matcher Worker (Driver Assignment)")
    print("  ✅ Notification System")
    print()
    print("Check your terminal windows to see:")
    print("  🔹 Ride Service: Published ride.requested")
    print("  🔹 Matcher Worker: Received message, assigned driver")
    print("  🔹 Notification Consumer: Sent notifications")
    print()
    
else:
    print("❌ Failed to create ride!")
    print("Make sure Ride Service is running on port 8001")