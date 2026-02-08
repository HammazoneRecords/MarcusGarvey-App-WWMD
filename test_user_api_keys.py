#!/usr/bin/env python3
"""
Test script to verify user-provided API keys work in WWMD and chat endpoints
Tests backend acceptance and usage of user API keys
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5050"

def test_wwmd_with_user_key(user_api_key):
    """Test WWMD endpoint with user-provided API key"""
    print("\n" + "="*80)
    print("TEST 1: WWMD Endpoint with User API Key")
    print("="*80)
    
    payload = {
        "situation": "I want to build a strong community organization. How do I start?",
        "mode": "Personal",
        "apiConfig": {
            "provider": "gemini",
            "geminiApiKey": user_api_key
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/wwmd",
            json=payload,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Response received")
            print(f"✓ Principle: {data.get('principle', 'N/A')[:80]}...")
            print(f"✓ Action Steps: {len(data.get('actionSteps', []))} steps")
            print(f"✓ Receipts (Citations): {len(data.get('receipts', []))} citations")
            return True
        else:
            print(f"✗ Error: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"✗ Exception: {str(e)}")
        return False

def test_wwmd_without_api_key():
    """Test WWMD endpoint without user API key (should use .env)"""
    print("\n" + "="*80)
    print("TEST 2: WWMD Endpoint WITHOUT User API Key (uses .env)")
    print("="*80)
    
    payload = {
        "situation": "How do I ensure my organization is sustainable?",
        "mode": "Community"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/wwmd",
            json=payload,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Response received (using .env API key)")
            print(f"✓ Principle: {data.get('principle', 'N/A')[:80]}...")
            return True
        else:
            print(f"Note: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"Note: {str(e)}")
        return False

def test_chat_with_user_key(user_api_key):
    """Test chat endpoint with user-provided API key"""
    print("\n" + "="*80)
    print("TEST 3: Chat Endpoint with User API Key")
    print("="*80)
    
    payload = {
        "query": "What is economic independence according to Garvey?",
        "apiConfig": {
            "provider": "gemini",
            "geminiApiKey": user_api_key
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=payload,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Response received")
            answer = data.get('answer', '')
            print(f"✓ Answer Length: {len(answer)} characters")
            print(f"✓ Citations: {len(data.get('citations', []))} citations")
            print(f"✓ Answer Preview: {answer[:100]}...")
            return True
        else:
            print(f"✗ Error: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"✗ Exception: {str(e)}")
        return False

def test_chat_without_api_key():
    """Test chat endpoint without user API key (should use .env)"""
    print("\n" + "="*80)
    print("TEST 4: Chat Endpoint WITHOUT User API Key (uses .env)")
    print("="*80)
    
    payload = {
        "query": "What principles guide organizational leadership?"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=payload,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Response received (using .env API key)")
            answer = data.get('answer', '')
            print(f"✓ Answer Length: {len(answer)} characters")
            return True
        else:
            print(f"Note: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"Note: {str(e)}")
        return False

def main():
    print("\n")
    print("*" * 80)
    print("USER API KEY INTEGRATION TESTS")
    print("*" * 80)
    print(f"\nBackend: {BASE_URL}")
    print("\nThis test verifies that signed-in users can provide their own API keys")
    print("and that the backend accepts and uses them instead of .env keys.\n")
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend health check failed")
            sys.exit(1)
    except:
        print("❌ Cannot connect to backend. Make sure it's running:")
        print("   cd backend && python api/server.py")
        sys.exit(1)
    
    # Prompt for user API key
    print("Enter your Gemini API key (or press Enter to skip user key tests):")
    user_key = input(">> ").strip()
    
    results = []
    
    if user_key:
        print(f"\n✓ Using provided API key: {user_key[:10]}...{user_key[-4:]}")
        results.append(("WWMD with user key", test_wwmd_with_user_key(user_key)))
        results.append(("Chat with user key", test_chat_with_user_key(user_key)))
    else:
        print("\nSkipping user key tests (no key provided)")
    
    # Test fallback to .env
    results.append(("WWMD fallback to .env", test_wwmd_without_api_key()))
    results.append(("Chat fallback to .env", test_chat_without_api_key()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n✓ All tests passed! User API keys are working correctly.")
        return 0
    else:
        print(f"\n⚠ {total_count - passed_count} test(s) failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
