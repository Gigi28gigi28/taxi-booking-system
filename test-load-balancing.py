"""
Script de test du Load Balancing via Traefik
Envoie plusieurs requêtes et vérifie la distribution
"""
import requests
import time
from collections import Counter

TRAEFIK_URL = "http://localhost:8080"
NUM_REQUESTS = 20

def test_load_balancing():
    print("=" * 60)
    print(" TEST DE LOAD BALANCING via TRAEFIK")
    print("=" * 60)
    print()
    
    # Test 1: Vérifier que Traefik est actif
    print(" Vérification de Traefik...")
    try:
        response = requests.get(f"{TRAEFIK_URL}/", timeout=2)
        print("    Traefik accessible")
    except:
        print("    Traefik non accessible sur", TRAEFIK_URL)
        print("    Lancez: start-traefik.bat")
        return
    
    print()
    
    # Test 2: Health check via Traefik
    print(" Test de routing vers services...")
    
    endpoints = [
        ("/accounts/api/verify/", "Auth Service"),
        ("/api/rides/", "Ride Service")
    ]
    
    for endpoint, service_name in endpoints:
        try:
            url = f"{TRAEFIK_URL}{endpoint}"
            response = requests.get(url, timeout=3)
            
            # On s'attend à une 401 (pas de token) ou 200
            if response.status_code in [200, 401, 400]:
                print(f"    {service_name}: Routing OK")
            else:
                print(f"    {service_name}: Status {response.status_code}")
        except Exception as e:
            print(f"    {service_name}: {e}")
    
    print()
    
    # Test 3: Load Balancing (Auth Service)
    print(f" Test de Load Balancing (Auth Service)")
    print(f"   Envoi de {NUM_REQUESTS} requêtes...")
    print()
    
    server_responses = []
    errors = 0
    
    for i in range(NUM_REQUESTS):
        try:
            # On fait une requête simple qui ne nécessite pas d'auth
            response = requests.post(
                f"{TRAEFIK_URL}/accounts/api/login/",
                json={"email": "test@test.com", "password": "test"},
                timeout=2
            )
            
            # Extraire le port du serveur qui a répondu (si disponible dans les headers)
            server = response.headers.get('X-Forwarded-Server', 'unknown')
            server_responses.append(server)
            
            # Afficher un point pour montrer la progression
            print(".", end="", flush=True)
            
            time.sleep(0.1)  # Petit délai entre requêtes
            
        except Exception as e:
            errors += 1
            print("x", end="", flush=True)
    
    print()
    print()
    
    # Analyse des résultats
    print(" RÉSULTATS:")
    print()
    
    if errors > 0:
        print(f"    Erreurs: {errors}/{NUM_REQUESTS}")
    
    # Compter les réponses par serveur
    counter = Counter(server_responses)
    
    if len(counter) > 1:
        print("    LOAD BALANCING ACTIF!")
        print()
        print("   Distribution des requêtes:")
        for server, count in counter.items():
            percentage = (count / NUM_REQUESTS) * 100
            bar = "█" * int(percentage / 5)
            print(f"      {server}: {count} requêtes ({percentage:.1f}%) {bar}")
    else:
        print("    Une seule instance détectée")
        print("    Lancez une réplica avec:")
        print("      start-auth-service-replica.bat")
    
    print()
    
    # Test 4: Vérifier dans Consul
    print(" Vérification dans Consul...")
    try:
        response = requests.get("http://localhost:8500/v1/catalog/service/auth-service", timeout=2)
        services = response.json()
        
        print(f"    {len(services)} instance(s) enregistrée(s)")
        
        for service in services:
            port = service['ServicePort']
            status = "" if service.get('Checks', [{}])[0].get('Status') == 'passing' else ""
            print(f"      {status} Port {port}")
    except:
        print("   Consul non accessible")
    
    print()
    print("=" * 60)
    print()
    
    # Recommandations
    print(" POUR TESTER LE LOAD BALANCING:")
    print()
    print("1. Lancez une 2ème instance d'Auth Service:")
    print("   > start-auth-service-replica.bat")
    print()
    print("2. Vérifiez dans Consul UI:")
    print("   http://localhost:8500")
    print()
    print("3. Re-lancez ce test:")
    print("   > python test-load-balancing.py")
    print()
    print("4. Observez la distribution sur 2 serveurs!")
    print()

if __name__ == "__main__":
    test_load_balancing()