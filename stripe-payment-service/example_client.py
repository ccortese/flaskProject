#!/usr/bin/env python3
"""
Example client for Stripe Payment Service

This demonstrates how to integrate with the payment service from another application.
"""

import requests
import json
import time
from typing import Dict, Optional

class PaymentClient:
    """Client for interacting with the Stripe Payment Service"""
    
    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url.rstrip('/')
    
    def create_payment(self, amount: int, currency: str = "usd", 
                      customer_email: Optional[str] = None, 
                      metadata: Optional[Dict] = None) -> Dict:
        """
        Create a new payment intent
        
        Args:
            amount: Amount in cents (e.g., 2000 for $20.00)
            currency: Currency code (default: 'usd')
            customer_email: Customer email address
            metadata: Additional metadata
            
        Returns:
            dict: Payment intent data or error
        """
        payload = {
            "amount": amount,
            "currency": currency
        }
        
        if customer_email:
            payload["customer_email"] = customer_email
            
        if metadata:
            payload["metadata"] = metadata
        
        try:
            response = requests.post(
                f"{self.base_url}/create-payment-intent",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            return response.json()
            
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "type": "client_error",
                    "message": str(e)
                }
            }
    
    def get_payment_status(self, payment_intent_id: str) -> Dict:
        """
        Get payment status
        
        Args:
            payment_intent_id: Payment intent ID
            
        Returns:
            dict: Payment status data or error
        """
        try:
            response = requests.get(f"{self.base_url}/payment-status/{payment_intent_id}")
            return response.json()
            
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "type": "client_error",
                    "message": str(e)
                }
            }
    
    def list_payments(self) -> Dict:
        """
        List all payments
        
        Returns:
            dict: List of payments or error
        """
        try:
            response = requests.get(f"{self.base_url}/payments")
            return response.json()
            
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "type": "client_error",
                    "message": str(e)
                }
            }
    
    def health_check(self) -> Dict:
        """
        Check service health
        
        Returns:
            dict: Health status or error
        """
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.json()
            
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "type": "client_error",
                    "message": str(e)
                }
            }


def example_usage():
    """Example of how to use the PaymentClient"""
    
    # Initialize client
    client = PaymentClient()
    
    print("🚀 Payment Service Client Example")
    print("=" * 40)
    
    # Check service health
    print("1. Checking service health...")
    health = client.health_check()
    if health.get('status') == 'healthy':
        print(f"✅ Service is healthy: {health['service']} v{health['version']}")
    else:
        print("❌ Service is not healthy")
        return
    
    # Create a payment
    print("\n2. Creating payment intent...")
    payment_result = client.create_payment(
        amount=2500,  # $25.00
        currency="usd",
        customer_email="customer@example.com",
        metadata={
            "order_id": "ORD-12345",
            "product": "Premium Widget",
            "customer_id": "CUST-67890"
        }
    )
    
    if payment_result.get('success'):
        payment_intent = payment_result['payment_intent']
        print(f"✅ Payment intent created:")
        print(f"   ID: {payment_intent['id']}")
        print(f"   Amount: ${payment_intent['amount']/100:.2f}")
        print(f"   Status: {payment_intent['status']}")
        print(f"   Client Secret: {payment_intent['client_secret'][:20]}...")
        
        payment_id = payment_intent['id']
        
        # Check payment status
        print("\n3. Checking payment status...")
        status_result = client.get_payment_status(payment_id)
        
        if status_result.get('success'):
            payment = status_result['payment']
            print(f"✅ Payment status: {payment['status']}")
        else:
            print(f"❌ Failed to get payment status: {status_result.get('error', {}).get('message')}")
        
    else:
        print(f"❌ Failed to create payment: {payment_result.get('error', {}).get('message')}")
        return
    
    # List all payments
    print("\n4. Listing all payments...")
    payments_result = client.list_payments()
    
    if payments_result.get('success'):
        payments = payments_result['payments']
        print(f"✅ Found {len(payments)} payments:")
        for payment in payments[-3:]:  # Show last 3 payments
            print(f"   - {payment['id']}: ${payment['amount']/100:.2f} ({payment['status']})")
    else:
        print(f"❌ Failed to list payments: {payments_result.get('error', {}).get('message')}")
    
    print("\n" + "=" * 40)
    print("🎉 Example completed!")
    print("\n💡 In a real application, you would:")
    print("   1. Use the client_secret with Stripe.js on the frontend")
    print("   2. Handle payment confirmation on the client side")
    print("   3. Use webhooks to update your database")
    print("   4. Implement proper error handling and retry logic")


if __name__ == "__main__":
    example_usage()
