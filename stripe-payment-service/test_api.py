#!/usr/bin/env python3
"""
Test script for Stripe Payment Service API

This script tests the basic functionality of the payment service
without requiring actual Stripe API calls (for demo purposes).
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:5001"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to service. Make sure it's running on port 5001")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_create_payment_intent():
    """Test creating a payment intent"""
    print("\n💳 Testing payment intent creation...")
    
    payload = {
        "amount": 2000,  # $20.00
        "currency": "usd",
        "customer_email": "test@example.com",
        "metadata": {
            "order_id": "test-12345",
            "product": "Test Product"
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/create-payment-intent",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            data = response.json()
            if data['success']:
                payment_intent = data['payment_intent']
                print(f"✅ Payment intent created: {payment_intent['id']}")
                print(f"   Amount: ${payment_intent['amount']/100:.2f}")
                print(f"   Status: {payment_intent['status']}")
                return payment_intent['id']
            else:
                print(f"❌ Payment intent creation failed: {data.get('error', {}).get('message')}")
                return None
        else:
            print(f"❌ Payment intent creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Payment intent creation error: {e}")
        return None

def test_payment_status(payment_intent_id):
    """Test getting payment status"""
    print(f"\n📊 Testing payment status for {payment_intent_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/payment-status/{payment_intent_id}")
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                payment = data['payment']
                print(f"✅ Payment status retrieved:")
                print(f"   ID: {payment['id']}")
                print(f"   Status: {payment['status']}")
                print(f"   Amount: ${payment['amount']/100:.2f}")
                return True
            else:
                print(f"❌ Payment status retrieval failed: {data.get('error', {}).get('message')}")
                return False
        else:
            print(f"❌ Payment status retrieval failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Payment status error: {e}")
        return False

def test_list_payments():
    """Test listing all payments"""
    print("\n📋 Testing payment list...")
    
    try:
        response = requests.get(f"{BASE_URL}/payments")
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                payments = data['payments']
                print(f"✅ Payment list retrieved: {len(payments)} payments")
                for payment in payments:
                    print(f"   - {payment['id']}: ${payment['amount']/100:.2f} ({payment['status']})")
                return True
            else:
                print(f"❌ Payment list retrieval failed: {data.get('error', {}).get('message')}")
                return False
        else:
            print(f"❌ Payment list retrieval failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Payment list error: {e}")
        return False

def test_invalid_requests():
    """Test error handling with invalid requests"""
    print("\n🚫 Testing error handling...")
    
    # Test missing amount
    try:
        response = requests.post(
            f"{BASE_URL}/create-payment-intent",
            json={"currency": "usd"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print("✅ Correctly rejected request with missing amount")
        else:
            print(f"❌ Should have rejected missing amount: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing invalid request: {e}")
    
    # Test invalid payment intent ID
    try:
        response = requests.get(f"{BASE_URL}/payment-status/invalid_id")
        
        if response.status_code == 404:
            print("✅ Correctly returned 404 for invalid payment intent ID")
        else:
            print(f"❌ Should have returned 404 for invalid ID: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing invalid payment ID: {e}")

def main():
    """Run all tests"""
    print("🧪 Starting Stripe Payment Service API Tests")
    print("=" * 50)
    
    # Test health check first
    if not test_health_check():
        print("\n❌ Service is not running. Please start the service first:")
        print("   python app.py")
        return
    
    # Test payment creation
    payment_intent_id = test_create_payment_intent()
    
    if payment_intent_id:
        # Test payment status
        test_payment_status(payment_intent_id)
    
    # Test payment listing
    test_list_payments()
    
    # Test error handling
    test_invalid_requests()
    
    print("\n" + "=" * 50)
    print("🎉 API tests completed!")
    print("\n💡 Next steps:")
    print("   1. Set up your Stripe test keys in .env")
    print("   2. Test with real Stripe API calls")
    print("   3. Integrate with a frontend application")

if __name__ == "__main__":
    main()
