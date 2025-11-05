# 💳 Stripe Payment Service

A Flask-based REST API service for handling Stripe payments. This is a proof-of-concept implementation designed for testing and development purposes.

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Stripe account (test mode)
- Flask and dependencies

### Installation

1. **Install dependencies:**
```bash
cd stripe-payment-service
pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your Stripe test keys
```

3. **Run the service:**
```bash
python app.py
```

The service will start on `http://localhost:5001`

## 📋 API Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "stripe-payment-service",
  "version": "1.0.0"
}
```

### Create Payment Intent
```http
POST /create-payment-intent
Content-Type: application/json

{
  "amount": 2000,
  "currency": "usd",
  "customer_email": "customer@example.com",
  "metadata": {
    "order_id": "12345",
    "product": "Test Product"
  }
}
```

**Response:**
```json
{
  "success": true,
  "payment_intent": {
    "id": "pi_1234567890",
    "client_secret": "pi_1234567890_secret_xyz",
    "amount": 2000,
    "currency": "usd",
    "status": "requires_payment_method"
  }
}
```

### Confirm Payment
```http
POST /confirm-payment
Content-Type: application/json

{
  "payment_intent_id": "pi_1234567890",
  "payment_method_id": "pm_1234567890"
}
```

**Response:**
```json
{
  "success": true,
  "payment_intent": {
    "id": "pi_1234567890",
    "status": "succeeded",
    "amount": 2000,
    "currency": "usd"
  }
}
```

### Get Payment Status
```http
GET /payment-status/{payment_intent_id}
```

**Response:**
```json
{
  "success": true,
  "payment": {
    "id": "pi_1234567890",
    "status": "succeeded",
    "amount": 2000,
    "currency": "usd",
    "created": 1634567890
  }
}
```

### List Payments (Demo)
```http
GET /payments
```

**Response:**
```json
{
  "success": true,
  "payments": [
    {
      "id": "pi_1234567890",
      "amount": 2000,
      "currency": "usd",
      "status": "succeeded",
      "customer_email": "customer@example.com",
      "metadata": {},
      "created_at": 1634567890
    }
  ]
}
```

### Webhook Handler
```http
POST /webhook
Content-Type: application/json
Stripe-Signature: t=1634567890,v1=signature_here

{
  "type": "payment_intent.succeeded",
  "data": {
    "object": {
      "id": "pi_1234567890",
      "status": "succeeded"
    }
  }
}
```

## 🧪 Testing

### Using cURL

**Create a payment intent:**
```bash
curl -X POST http://localhost:5001/create-payment-intent \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 2000,
    "currency": "usd",
    "customer_email": "test@example.com",
    "metadata": {
      "order_id": "test-123"
    }
  }'
```

**Check payment status:**
```bash
curl http://localhost:5001/payment-status/pi_1234567890
```

**List all payments:**
```bash
curl http://localhost:5001/payments
```

### Using Python requests

```python
import requests

# Create payment intent
response = requests.post('http://localhost:5001/create-payment-intent', json={
    'amount': 2000,
    'currency': 'usd',
    'customer_email': 'test@example.com'
})

payment_data = response.json()
print(f"Payment Intent ID: {payment_data['payment_intent']['id']}")
```

## 🔧 Configuration

### Environment Variables

- `STRIPE_SECRET_KEY`: Your Stripe secret key (test mode)
- `STRIPE_PUBLISHABLE_KEY`: Your Stripe publishable key (test mode)
- `STRIPE_WEBHOOK_SECRET`: Webhook endpoint secret (optional)

### Stripe Dashboard Setup

1. **Get API Keys:**
   - Go to [Stripe Dashboard](https://dashboard.stripe.com/test/apikeys)
   - Copy your test mode keys

2. **Set up Webhooks (Optional):**
   - Go to [Webhooks](https://dashboard.stripe.com/test/webhooks)
   - Add endpoint: `http://your-domain.com/webhook`
   - Select events: `payment_intent.succeeded`, `payment_intent.payment_failed`

## 🔒 Security Notes

⚠️ **This is a proof-of-concept implementation. For production use:**

- Use HTTPS only
- Implement proper authentication
- Validate webhook signatures
- Use environment variables for secrets
- Add rate limiting
- Implement proper error handling
- Use a real database instead of in-memory storage
- Add logging and monitoring

## 📊 Payment Flow

1. **Create Payment Intent** - Initialize payment with amount and currency
2. **Client-side Payment** - Use Stripe.js to collect payment method
3. **Confirm Payment** - Confirm payment with payment method
4. **Handle Webhooks** - Process payment status updates
5. **Check Status** - Verify payment completion

## 🛠️ Development

### Project Structure
```
stripe-payment-service/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
├── README.md          # This file
└── tests/             # Test files (optional)
```

### Adding New Features

1. Add new endpoints to `app.py`
2. Update this README with API documentation
3. Add tests for new functionality
4. Update requirements if needed

## 📝 License

This is a proof-of-concept implementation for testing purposes.
