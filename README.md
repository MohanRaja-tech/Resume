# Resume Summary Generator

A professional web application that generates attractive resume summaries based on user input. Built with Flask backend and modern responsive frontend.

## Features

- 📝 Professional resume summary generation
- 🔐 User authentication (signup/login)
- 💳 Premium subscription with Razorpay integration
- � Free trial system (3 generations)
- �🎨 Modern, responsive UI design
- 📱 Mobile-friendly interface
- 🔄 Multiple summary variations
- 📋 One-click copy functionality
- ⚡ Fast and lightweight
- 🌐 MongoDB Atlas integration
- 🔒 Secure payment processing

## Setup Instructions

### 1. Environment Setup

Copy the environment example file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` file and configure your settings:
```
SECRET_KEY=your_super_secret_key_here
CUSTOM_API_KEY=your_custom_api_key_here
RAZORPAY_KEY_ID=your_razorpay_key_id_here
RAZORPAY_KEY_SECRET=your_razorpay_secret_here
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python3 app.py
```

### 4. Open in Browser

Navigate to: `http://localhost:5000`

## Deployment on Vercel

### 1. Install Vercel CLI

```bash
npm i -g vercel
```

### 2. Configure Environment Variables

In your Vercel dashboard or via CLI, set these environment variables:

```bash
vercel env add OPENAI_API_KEY
vercel env add SECRET_KEY
vercel env add FREE_TRIAL_LIMIT
```

### 3. Deploy

```bash
vercel --prod
```

### Environment Variables for Vercel:

- `SECRET_KEY`: A secure random string for Flask sessions
- `CUSTOM_API_KEY`: Your custom API key for the resume summary service
- `FREE_TRIAL_LIMIT`: Number of free generations (default: 3)
- `MONGODB_URI`: MongoDB Atlas connection string for user authentication
- `RAZORPAY_KEY_ID`: Your Razorpay Key ID for payment processing
- `RAZORPAY_KEY_SECRET`: Your Razorpay Key Secret for payment verification

## Razorpay Payment Integration Setup

This application includes premium subscription functionality using Razorpay payment gateway for Indian users (₹1000/month).

### 1. Create Razorpay Account

1. **Sign up at Razorpay:**
   - Go to [https://razorpay.com](https://razorpay.com)
   - Click "Sign Up" and create your business account
   - Complete the business verification process (required for live payments)

2. **Business Verification Requirements:**
   - Business PAN card
   - Bank account details
   - Business registration documents (if applicable)
   - Director/Owner ID proof

### 2. Get Razorpay API Keys

#### For Testing (Test Mode):
1. Login to [Razorpay Dashboard](https://dashboard.razorpay.com/)
2. Navigate to **Settings** → **API Keys**
3. In the **Test Mode** section, click **Generate Test Key**
4. Copy both keys:
   - **Key ID**: `rzp_test_xxxxxxxxxx` 
   - **Key Secret**: `xxxxxxxxxxxxxxxxxx`

#### For Production (Live Mode):
1. Ensure your account is activated (business verification complete)
2. Navigate to **Settings** → **API Keys**
3. Switch to **Live Mode** (top-right toggle)
4. Click **Generate Live Key**
5. Copy both keys:
   - **Key ID**: `rzp_live_xxxxxxxxxx`
   - **Key Secret**: `xxxxxxxxxxxxxxxxxx`

### 3. Configure Environment Variables

Add these keys to your `.env` file:

```bash
# Razorpay Configuration
RAZORPAY_KEY_ID=rzp_test_your_key_id_here    # Use rzp_live_ for production
RAZORPAY_KEY_SECRET=your_razorpay_secret_here
```

### 4. Razorpay Dashboard Setup

#### Enable Required Payment Methods:
1. Go to **Settings** → **Payment Methods**
2. Enable these popular Indian payment methods:
   - **UPI** (Google Pay, PhonePe, Paytm, etc.)
   - **Credit/Debit Cards**
   - **Net Banking**
   - **Wallets** (Paytm, Mobikwik, etc.)

#### Set Up Webhooks (Optional but Recommended):
1. Go to **Settings** → **Webhooks**
2. Add webhook URL: `https://yourdomain.com/api/razorpay-webhook`
3. Select events: `payment.captured`, `payment.failed`

### 5. Test the Integration

#### Test Mode Testing:
1. Use test credentials in your `.env` file
2. Use these test card details:
   - **Card Number**: `4111 1111 1111 1111`
   - **Expiry**: Any future date
   - **CVV**: Any 3 digits
   - **For UPI**: Use any VPA like `success@razorpay`

#### Test Payment Flow:
1. Start your application: `python3 app.py`
2. Login/signup for an account
3. Click "Upgrade to Premium Now"
4. Complete test payment using test credentials
5. Verify user gets upgraded to premium status

### 6. Go Live Checklist

Before switching to live mode:

- ✅ Complete Razorpay business verification
- ✅ Test all payment methods thoroughly
- ✅ Update environment variables with live keys
- ✅ Enable live payment methods in dashboard
- ✅ Set up webhook endpoints (recommended)
- ✅ Test with small real payment amounts

### 7. Important Security Notes

🔒 **Security Best Practices:**

- **Never expose** your `RAZORPAY_KEY_SECRET` in frontend code
- **Always verify** payment signatures on backend
- **Use HTTPS** in production for secure data transmission
- **Log payment attempts** for audit and debugging
- **Implement rate limiting** to prevent payment abuse

### 8. Razorpay Integration Features

✨ **What's Included:**

- **Order Creation**: Backend creates secure payment orders
- **Signature Verification**: HMAC-SHA256 signature validation
- **Multiple Payment Methods**: UPI, Cards, Net Banking, Wallets
- **Error Handling**: Comprehensive error management
- **User Upgrade**: Automatic premium activation after successful payment
- **Mobile Responsive**: Works seamlessly on mobile devices

### 9. Pricing Configuration

Current pricing: **₹1000/month**

To change pricing, update the amount in `dashboard.html`:
```javascript
body: JSON.stringify({
    amount: 100000, // Amount in paise (₹1000 = 100000 paise)
    currency: 'INR'
})
```

### 10. Support and Documentation

- **Razorpay Docs**: [https://razorpay.com/docs/](https://razorpay.com/docs/)
- **Payment Gateway**: [https://razorpay.com/docs/payments/](https://razorpay.com/docs/payments/)
- **Test Credentials**: [https://razorpay.com/docs/payments/payments/test-card-details/](https://razorpay.com/docs/payments/payments/test-card-details/)
- **Support**: [https://razorpay.com/support/](https://razorpay.com/support/)

## Custom Resume Summary API

This application uses a custom AWS API for generating professional resume summaries instead of OpenAI.

### API Details:
- **Endpoint**: `https://ufc6ri782h.execute-api.ap-south-1.amazonaws.com/StageOneResumeSummaryText/ProdEasyJobsResumeSummary`
- **Method**: POST
- **Content-Type**: application/json
- **Authentication**: Bearer token (via `CUSTOM_API_KEY` environment variable)

### API Authentication:
The API key is sent in the Authorization header as:
```
Authorization: Bearer your_custom_api_key_here
```

### API Request Format:
```json
{
  "current_job_title": "Data Scientist",
  "job_description": "I analyse data and take meaningful insights to help business grow",
  "years_experience": "0.5",
  "achievements": "Increased sales of the company",
  "technical_skills": "Python, Power BI, Excel, Jupyter Notebook, Pandas",
  "education": "Bachelor of AI and ML"
}
```

### Fallback System:
If the custom API is unavailable, the application automatically falls back to template-based summary generation to ensure uninterrupted service.

## API Documentation

### Generate Summary Endpoint

**URL:** `/api/generate-summary`  
**Method:** `POST`  
**Content-Type:** `application/json`

#### Request Body:
```json
{
  "current_job_title": "Data Scientist",
  "job_description": "I analyse data and take meaningful insights to help business grow and get organic clients",
  "years_experience": "0.5",
  "achievements": "Increased sales of the company",
  "technical_skills": "Python, Power BI, Excel, Jupyter Notebook, Pandas",
  "education": "Bachelor of AI and ML"
}
```

#### Response:
```json
{
    "success": true,
    "data": {
        "v1": "Detail-oriented Data Scientist with 0.5 years of experience...",
        "v2": "Accomplished Data Scientist possessing 0.5 years of expertise...",
        "v3": "Results-driven Data Scientist with 0.5 years of experience..."
    }
}
```

### Razorpay Payment Endpoints

#### Create Payment Order

**URL:** `/api/create-razorpay-order`  
**Method:** `POST`  
**Authentication:** Required (login)  
**Content-Type:** `application/json`

**Request Body:**
```json
{
  "amount": 100000,
  "currency": "INR"
}
```

**Response:**
```json
{
    "success": true,
    "order_id": "order_xxxxxxxxxxxxx",
    "amount": 100000,
    "currency": "INR",
    "razorpay_key": "rzp_test_xxxxxxxxxxxxx"
}
```

#### Verify Payment

**URL:** `/api/verify-razorpay-payment`  
**Method:** `POST`  
**Authentication:** Required (login)  
**Content-Type:** `application/json`

**Request Body:**
```json
{
  "razorpay_order_id": "order_xxxxxxxxxxxxx",
  "razorpay_payment_id": "pay_xxxxxxxxxxxxx",
  "razorpay_signature": "signature_string_here"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Payment verified and premium activated successfully!",
    "is_premium": true,
    "payment_id": "pay_xxxxxxxxxxxxx"
}
```

## Project Structure

```
Biofilterations/
├── app.py                    # Flask backend application
├── database.py               # MongoDB database operations
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not in git)
├── vercel.json              # Vercel deployment configuration
├── templates/
│   ├── auth.html            # Login/Signup page
│   └── dashboard.html       # Main application interface
└── README.md                # This documentation file
```

## Technology Stack

- **Backend:** Flask (Python)
- **AI Summary Generation:** Custom AWS API (https://ufc6ri782h.execute-api.ap-south-1.amazonaws.com/StageOneResumeSummaryText/ProdEasyJobsResumeSummary)
- **Database:** MongoDB Atlas (user authentication & data persistence)
- **Payment Gateway:** Razorpay (Indian payment processing)
- **Authentication:** bcrypt password hashing
- **Frontend:** HTML5, CSS3, JavaScript
- **Styling:** Custom CSS with gradients and animations
- **Icons:** Font Awesome
- **Responsive:** Mobile-first design
- **Deployment:** Vercel (serverless)

## Features Explained

### Professional UI Design
- Modern gradient backgrounds
- Smooth animations and transitions
- Card-based layout with shadows
- Responsive design for all devices

### Form Validation
- Real-time character counting
- Required field validation
- Input sanitization

### Summary Generation
- Three different writing styles
- Professional language optimization
- Industry-specific customization

### User Experience
- Loading indicators
- Error handling
- Copy-to-clipboard functionality
- Visual feedback for user actions

## Customization

You can customize the summary generation logic in the `generate_resume_summaries()` function in `app.py`. The current implementation creates three variations:

1. **Detail-oriented approach** - Focuses on analytical skills
2. **Accomplished approach** - Emphasizes achievements  
3. **Results-driven approach** - Highlights impact and outcomes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.
