#!/usr/bin/env python3
"""
Test script to verify Daytona-deployed API endpoints
Replace {sandbox-url} with your actual Daytona sandbox URL
"""

import requests
import json

# Replace this with your actual Daytona sandbox URL
SANDBOX_URL = "https://your-sandbox-url:8000"  # Get this from Daytona Dashboard

def test_api_endpoints():
    """Test all available API endpoints"""
    
    print("🧪 Testing IBM Sales Pipeline Analytics API on Daytona")
    print("=" * 60)
    
    endpoints = [
        ("Root", "/"),
        ("Health Check", "/health"), 
        ("System Info", "/info"),
        ("API Docs", "/docs")
    ]
    
    for name, endpoint in endpoints:
        try:
            url = f"{SANDBOX_URL}{endpoint}"
            print(f"\n🔍 Testing {name}: {url}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {name}: SUCCESS")
                if endpoint != "/docs":  # docs returns HTML
                    try:
                        data = response.json()
                        print(f"   Response: {json.dumps(data, indent=2)}")
                    except:
                        print(f"   Response: {response.text[:100]}...")
                else:
                    print(f"   Response: API documentation loaded")
            else:
                print(f"❌ {name}: FAILED (Status: {response.status_code})")
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️ {name}: CONNECTION ERROR - {e}")
    
    print(f"\n🎯 Next Steps:")
    print(f"1. Update SANDBOX_URL in this script with your actual URL")
    print(f"2. Configure LLM API keys for full functionality")
    print(f"3. Test the query generation endpoints")

if __name__ == "__main__":
    test_api_endpoints()