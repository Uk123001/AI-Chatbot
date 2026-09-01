# Quick Start Guide - AI Booking Assistant

Get started in 5 minutes! ⚡

## Prerequisites
- Python 3.8 or higher
- Git
- An API key from Groq, OpenAI, or Google

## Step 1: Get an API Key (2 minutes)

### Option A: Groq (Recommended - Fastest & Free)
1. Go to [console.groq.com](https://console.groq.com/keys)
2. Sign up or login
3. Click "Create API Key"
4. Copy the key

### Option B: OpenAI
1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign up or login
3. Click "Create new secret key"
4. Copy the key

### Option C: Google Gemini
1. Go to [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API key"
4. Copy the key

## Step 2: Clone and Setup (2 minutes)

```bash
# Clone the repository
git clone <repository-url>
cd ai-booking-assistant

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate
# On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Configure (1 minute)

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API key
# Using your favorite editor (nano, vim, or IDE)
nano .env
```

Add your API key:
```
GROQ_API_KEY=your_key_here
LLM_PROVIDER=groq
```

Save and exit (Ctrl+X, then Y, then Enter for nano)

## Step 4: Run (1 minute)

```bash
streamlit run main.py
```

The app will automatically open in your browser at `http://localhost:8501`

## 🎉 You're Done!

### First Steps in the App

1. **Go to Chat** - Start with a message like:
   - "I want to book a doctor appointment"
   - "Can I reserve a salon slot tomorrow?"

2. **Upload Documents** (Optional)
   - Click "Upload PDF" to add documents for context

3. **Admin Dashboard** (Optional)
   - Click "Admin Dashboard"
   - Login with password: `admin123`
   - View all bookings

## Common Issues & Solutions

### Issue: "GROQ_API_KEY not set"
**Solution:** Make sure you:
1. Created `.env` file (not `.env.example`)
2. Added `GROQ_API_KEY=your_actual_key`
3. Saved the file
4. Restarted Streamlit (Ctrl+C and `streamlit run main.py`)

### Issue: "ModuleNotFoundError: No module named..."
**Solution:** Make sure you:
1. Activated virtual environment
2. Ran `pip install -r requirements.txt`

### Issue: Port 8501 already in use
**Solution:** 
```bash
streamlit run main.py --server.port 8502
```

## Next Steps

- 📖 Read [README.md](README.md) for detailed documentation
- 🚀 Read [DEPLOYMENT.md](DEPLOYMENT.md) to deploy to production
- 💾 Configure email (optional) - see README.md
- 🗄️ Switch to PostgreSQL (optional) - see DEPLOYMENT.md

## Configuration (Optional)

### Enable Email Confirmations

```bash
# In .env, add:
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### Change Admin Password

```bash
# In .env, change:
ADMIN_PASSWORD=your_new_secure_password
```

## File Structure

```
ai-booking-assistant/
├── main.py                 # Run this to start ✨
├── .env                    # Your configuration (keep secret!)
├── requirements.txt        # Python packages
├── README.md              # Full documentation
└── DEPLOYMENT.md          # Production guide
```

## Need Help?

1. **Check logs** - Errors are shown in the console
2. **Read README.md** - Comprehensive documentation
3. **Check environment variables** - Make sure `.env` is correct
4. **Test API key** - Make sure your API key is valid and has credits

## Keyboard Shortcuts

- `Ctrl+C` - Stop Streamlit
- `Ctrl+Z` - Undo (in development mode)
- `R` - Rerun script

## Performance Tips

- Use Groq for fastest responses
- Upload smaller PDFs for faster processing
- Clear chat history if performance slows down
- Restart Streamlit if memory usage gets high

## What's Next?

Once everything is working:

1. Test the booking flow
2. Try uploading a PDF
3. Check the Admin Dashboard
4. Send test emails
5. Deploy to production (see DEPLOYMENT.md)

Happy Booking! 🚀
