#!/usr/bin/env python3
"""
Stripe Payment Processing Backend API

A Flask-based REST API service for handling Stripe payments.
This is a proof-of-concept implementation for testing purposes.

Endpoints:
- POST /create-payment-intent - Create a new payment intent
- POST /confirm-payment - Confirm a payment
- GET /payment-status/<payment_intent_id> - Get payment status
- POST /webhook - Handle Stripe webhooks
- GET /health - Health check endpoint
"""

import os
import sys
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Add the stripe SDK to the path
sys.path.append('../payment-integrations/stripe-python-sdk')
import stripe

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Stripe configuration
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_...')  # Use test key for POC
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')

# In-memory storage for demo purposes (use database in production)
payment_records = {}


class PaymentProcessor:
    """Handles Stripe payment operations"""
    
    @staticmethod
    def create_payment_intent(amount, currency='usd', customer_email=None, metadata=None):
        """
        Create a Stripe Payment Intent
        
        Args:
            amount (int): Amount in cents (e.g., 2000 for $20.00)
            currency (str): Currency code (default: 'usd')
            customer_email (str): Customer email address
            metadata (dict): Additional metadata
            
        Returns:
            dict: Payment intent data or error
        """
        try:
            payment_intent_data = {
                'amount': amount,
                'currency': currency,
                'automatic_payment_methods': {
                    'enabled': True,
                },
            }
            
            if customer_email:
                payment_intent_data['receipt_email'] = customer_email
                
            if metadata:
                payment_intent_data['metadata'] = metadata
            
            payment_intent = stripe.PaymentIntent.create(**payment_intent_data)
            
            # Store in our demo database
            payment_records[payment_intent.id] = {
                'id': payment_intent.id,
                'amount': amount,
                'currency': currency,
                'status': payment_intent.status,
                'client_secret': payment_intent.client_secret,
                'customer_email': customer_email,
                'metadata': metadata or {},
                'created_at': payment_intent.created
            }
            
            logger.info(f"Created payment intent: {payment_intent.id}")
            return {
                'success': True,
                'payment_intent': {
                    'id': payment_intent.id,
                    'client_secret': payment_intent.client_secret,
                    'amount': amount,
                    'currency': currency,
                    'status': payment_intent.status
                }
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating payment intent: {str(e)}")
            return {
                'success': False,
                'error': {
                    'type': 'stripe_error',
                    'message': str(e)
                }
            }
        except Exception as e:
            logger.error(f"Unexpected error creating payment intent: {str(e)}")
            return {
                'success': False,
                'error': {
                    'type': 'server_error',
                    'message': 'An unexpected error occurred'
                }
            }
    
    @staticmethod
    def confirm_payment(payment_intent_id, payment_method_id=None):
        """
        Confirm a payment intent
        
        Args:
            payment_intent_id (str): Payment intent ID
            payment_method_id (str): Payment method ID (optional)
            
        Returns:
            dict: Confirmation result
        """
        try:
            confirm_data = {}
            if payment_method_id:
                confirm_data['payment_method'] = payment_method_id
            
            payment_intent = stripe.PaymentIntent.confirm(
                payment_intent_id,
                **confirm_data
            )
            
            # Update our demo database
            if payment_intent_id in payment_records:
                payment_records[payment_intent_id]['status'] = payment_intent.status
            
            logger.info(f"Confirmed payment intent: {payment_intent_id}")
            return {
                'success': True,
                'payment_intent': {
                    'id': payment_intent.id,
                    'status': payment_intent.status,
                    'amount': payment_intent.amount,
                    'currency': payment_intent.currency
                }
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error confirming payment: {str(e)}")
            return {
                'success': False,
                'error': {
                    'type': 'stripe_error',
                    'message': str(e)
                }
            }
        except Exception as e:
            logger.error(f"Unexpected error confirming payment: {str(e)}")
            return {
                'success': False,
                'error': {
                    'type': 'server_error',
                    'message': 'An unexpected error occurred'
                }
            }
    
    @staticmethod
    def get_payment_status(payment_intent_id):
        """
        Get payment status
        
        Args:
            payment_intent_id (str): Payment intent ID
            
        Returns:
            dict: Payment status data
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            # Update our demo database
            if payment_intent_id in payment_records:
                payment_records[payment_intent_id]['status'] = payment_intent.status
            
            return {
                'success': True,
                'payment': {
                    'id': payment_intent.id,
                    'status': payment_intent.status,
                    'amount': payment_intent.amount,
                    'currency': payment_intent.currency,
                    'created': payment_intent.created
                }
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving payment: {str(e)}")
            return {
                'success': False,
                'error': {
                    'type': 'stripe_error',
                    'message': str(e)
                }
            }
        except Exception as e:
            logger.error(f"Unexpected error retrieving payment: {str(e)}")
            return {
                'success': False,
                'error': {
                    'type': 'server_error',
                    'message': 'An unexpected error occurred'
                }
            }


# Initialize payment processor
processor = PaymentProcessor()


# API Routes
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'stripe-payment-service',
        'version': '1.0.0'
    })


@app.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    """
    Create a new payment intent
    
    Expected JSON payload:
    {
        "amount": 2000,  # Amount in cents
        "currency": "usd",  # Optional, defaults to USD
        "customer_email": "customer@example.com",  # Optional
        "metadata": {  # Optional
            "order_id": "12345",
            "product": "Test Product"
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': {
                    'type': 'validation_error',
                    'message': 'Request body must be valid JSON'
                }
            }), 400
        
        # Validate required fields
        if 'amount' not in data:
            return jsonify({
                'success': False,
                'error': {
                    'type': 'validation_error',
                    'message': 'Amount is required'
                }
            }), 400
        
        amount = data['amount']
        if not isinstance(amount, int) or amount <= 0:
            return jsonify({
                'success': False,
                'error': {
                    'type': 'validation_error',
                    'message': 'Amount must be a positive integer (in cents)'
                }
            }), 400
        
        # Extract optional fields
        currency = data.get('currency', 'usd')
        customer_email = data.get('customer_email')
        metadata = data.get('metadata')
        
        # Create payment intent
        result = processor.create_payment_intent(
            amount=amount,
            currency=currency,
            customer_email=customer_email,
            metadata=metadata
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in create_payment_intent: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'type': 'server_error',
                'message': 'An unexpected error occurred'
            }
        }), 500


@app.route('/confirm-payment', methods=['POST'])
def confirm_payment():
    """
    Confirm a payment intent

    Expected JSON payload:
    {
        "payment_intent_id": "pi_1234567890",
        "payment_method_id": "pm_1234567890"  # Optional
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': {
                    'type': 'validation_error',
                    'message': 'Request body must be valid JSON'
                }
            }), 400

        # Validate required fields
        if 'payment_intent_id' not in data:
            return jsonify({
                'success': False,
                'error': {
                    'type': 'validation_error',
                    'message': 'payment_intent_id is required'
                }
            }), 400

        payment_intent_id = data['payment_intent_id']
        payment_method_id = data.get('payment_method_id')

        # Confirm payment
        result = processor.confirm_payment(
            payment_intent_id=payment_intent_id,
            payment_method_id=payment_method_id
        )

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"Error in confirm_payment: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'type': 'server_error',
                'message': 'An unexpected error occurred'
            }
        }), 500


@app.route('/payment-status/<payment_intent_id>', methods=['GET'])
def get_payment_status(payment_intent_id):
    """
    Get payment status by payment intent ID
    """
    try:
        if not payment_intent_id:
            return jsonify({
                'success': False,
                'error': {
                    'type': 'validation_error',
                    'message': 'payment_intent_id is required'
                }
            }), 400

        # Get payment status
        result = processor.get_payment_status(payment_intent_id)

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404

    except Exception as e:
        logger.error(f"Error in get_payment_status: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'type': 'server_error',
                'message': 'An unexpected error occurred'
            }
        }), 500


@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    """
    Handle Stripe webhooks
    """
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        # Verify webhook signature (if webhook secret is configured)
        if STRIPE_WEBHOOK_SECRET:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        else:
            # For testing without webhook secret
            event = json.loads(payload)

        logger.info(f"Received webhook event: {event['type']}")

        # Handle different event types
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            logger.info(f"Payment succeeded: {payment_intent['id']}")

            # Update our demo database
            if payment_intent['id'] in payment_records:
                payment_records[payment_intent['id']]['status'] = 'succeeded'

        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            logger.info(f"Payment failed: {payment_intent['id']}")

            # Update our demo database
            if payment_intent['id'] in payment_records:
                payment_records[payment_intent['id']]['status'] = 'failed'

        elif event['type'] == 'payment_intent.canceled':
            payment_intent = event['data']['object']
            logger.info(f"Payment canceled: {payment_intent['id']}")

            # Update our demo database
            if payment_intent['id'] in payment_records:
                payment_records[payment_intent['id']]['status'] = 'canceled'

        else:
            logger.info(f"Unhandled event type: {event['type']}")

        return jsonify({'success': True}), 200

    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Invalid payload'
        }), 400
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Invalid signature'
        }), 400
    except Exception as e:
        logger.error(f"Error in webhook: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Webhook processing failed'
        }), 500


@app.route('/payments', methods=['GET'])
def list_payments():
    """
    List all payments (demo endpoint)
    """
    try:
        return jsonify({
            'success': True,
            'payments': list(payment_records.values())
        }), 200
    except Exception as e:
        logger.error(f"Error in list_payments: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'type': 'server_error',
                'message': 'An unexpected error occurred'
            }
        }), 500


if __name__ == '__main__':
    # Print startup information
    print("🚀 Starting Stripe Payment Service...")
    print(f"📍 Health check: http://localhost:5001/health")
    print(f"📖 API Documentation: See README.md")

    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )
