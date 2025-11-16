#!/usr/bin/env python3
import requests
import json

def test_faceid_api():
    """Testa o endpoint de FaceID login"""
    url = "http://localhost:5000/api/faceid/login"
    
    # Teste com imagem inválida (1x1 pixel transparente)
    payload = {
        "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    }
    
    try:
        print("=== TESTANDO API FACEID ===")
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("\n✅ API respondendo corretamente!")
        else:
            print(f"\n❌ Erro na API: {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ Erro ao testar API: {e}")

if __name__ == "__main__":
    test_faceid_api()
