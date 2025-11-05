# 🚀 Stripe Payment Service Setup Guide

This guide will help you set up and test the Stripe Payment Service backend API.

## 📋 Prerequisites

1. **Python 3.7+** installed
2. **Stripe Account** (free test account)
3. **Terminal/Command Line** access

## 🔧 Installation Steps

### Step 1: Install Dependencies

```bash
cd stripe-payment-service
pip3 install -r requirements.txt
```

### Step 2: Get Stripe Test Keys

1. **Create Stripe Account:**
   - Go to [stripe.com](https://stripe.com) and sign up
   - Verify your email

2. **Get Test API Keys:**
   - Go to [Stripe Dashboard](https://dashboard.stripe.com/test/apikeys)
   - Make sure you're in "Test mode" (toggle in top left)
   - Copy your "Publishable key" and "Secret key"

### Step 3: Configure Environment

1. **Copy environment template:**
```bash
cp .env.example .env
```

2. **Edit .env file:**
```bash
# Replace with your actual Stripe test keys
STRIPE_SECRET_KEY=sk_test_your_actual_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_actual_publishable_key_here
```

### Step 4: Start the Service

```bash
python3 app.py
```

You should see:
```
🚀 Starting Stripe Payment Service...
📍 Health check: http://localhost:5001/health
📖 API Documentation: See README.md
 * Running on http://127.0.0.1:5001
```

## 🧪 Testing

### Quick Test

Open a new terminal and run:

```bash
# Test health check
curl http://localhost:5001/health

# Test payment creation
curl -X POST http://localhost:5001/create-payment-intent \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 2000,
    "currency": "usd",
    "customer_email": "test@example.com"
  }'
```

### Automated Tests

```bash
python3 test_api.py
```

### Example Client

```bash
python3 example_client.py
```

## 🔍 Troubleshooting

### Common Issues

**1. "Invalid API Key" Error**
- Make sure you copied the correct test keys from Stripe Dashboard
- Ensure you're using test keys (start with `sk_test_` and `pk_test_`)
- Check that .env file is in the correct directory

**2. "Connection Refused" Error**
- Make sure the service is running on port 5001
- Check if another service is using port 5001

**3. "Module Not Found" Error**
- Install dependencies: `pip3 install -r requirements.txt`
- Make sure you're in the correct directory

**4. Stripe SDK Import Error**
- The service uses the local Stripe SDK from `../payment-integrations/stripe-python-sdk`
- If you prefer, uncomment the stripe line in requirements.txt and install via pip

### Verification Steps

1. **Service Health:**
```bash
curl http://localhost:5001/health
# Should return: {"status": "healthy", ...}
```

2. **Stripe Connection:**
```bash
curl -X POST http://localhost:5001/create-payment-intent \
  -H "Content-Type: application/json" \
  -d '{"amount": 1000, "currency": "usd"}'
# Should return payment intent with client_secret
```

## 🎯 Next Steps

### For Development

1. **Frontend Integration:**
   - Use the `client_secret` with Stripe.js
   - Implement payment form on frontend
   - Handle payment confirmation

2. **Webhook Setup:**
   - Add webhook endpoint in Stripe Dashboard
   - Point to: `https://your-domain.com/webhook`
   - Select events: `payment_intent.succeeded`, `payment_intent.payment_failed`

3. **Database Integration:**
   - Replace in-memory storage with real database
   - Add proper data models
   - Implement data persistence

### For Production

1. **Security:**
   - Use HTTPS only
   - Implement authentication
   - Validate webhook signatures
   - Add rate limiting

2. **Monitoring:**
   - Add logging
   - Implement health checks
   - Set up error tracking

3. **Deployment:**
   - Use production WSGI server (gunicorn)
   - Set up environment variables
   - Configure reverse proxy (nginx)

## 📚 API Reference

See `README.md` for complete API documentation with examples.

## 🆘 Getting Help

If you encounter issues:

1. Check the service logs in the terminal
2. Verify your Stripe test keys are correct
3. Test with curl commands first
4. Check Stripe Dashboard for payment attempts

## 🎉 Success!

Once you see successful API responses, you have a working Stripe payment backend that can:

- Create payment intents
- Handle payment confirmations
- Process webhooks
- Track payment status

You can now integrate this with any frontend application!
