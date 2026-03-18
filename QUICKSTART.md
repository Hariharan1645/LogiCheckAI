# 🚀 LogiCheckAI - Quick Start Guide

## What Was Wrong?

Your LogiCheckAI project had **two critical issues** preventing it from working:

1. **Missing Backend Startup Code** - The `backend/main.py` file was incomplete and couldn't start the server
2. **Port Conflict** - Port 8081 was already in use by another process, preventing the backend from binding

When you tried to analyze a YouTube Shorts video, the frontend had no backend to send requests to, resulting in **"no output"**.

---

## What's Fixed ✅

### Files Modified:
- ✅ `backend/main.py` - Added complete startup code with uvicorn
- ✅ `app.js` - Updated to use correct port 8000
- ✅ `backend/services/claim_detection.py` - Enhanced with more healthcare keywords
- ✅ Created `test.html` - System testing interface
- ✅ Created `ISSUES_AND_FIXES.md` - Complete documentation

---

## Environment Setup (IMPORTANT)

### 1. Create `.env` File
Before running the backend, you must set up API keys:

```bash
cd backend
```

Copy the template file:
```bash
cp .env.example .env
```

### 2. Add Your API Keys
Edit `backend/.env` and add your actual API keys:
```
GROQ_API_KEY=your_actual_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here (optional)
YOUTUBE_API_KEY=your_youtube_api_key_here (optional)
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Note:** The `.env` file is **never** committed to git. It's added to `.gitignore` to protect your secrets.

---

## How to Run

### Step 1: Start the Backend Server
Open a terminal and run:
```bash
cd backend
python main.py
```

OR using uvicorn directly:
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Started server process
Initializing backend... Loading models and corpus.
Loading SentenceTransformer model...
Backend initialization complete.
INFO:     Application startup complete.
```

### Step 2: Open the Frontend
- Simply open `index.html` in your web browser, OR
- Serve it with a local server:
  ```bash
  python -m http.server 8080
  # Then visit: http://localhost:8080
  ```

### Step 3: Test the System (Optional)
Open `test.html` in your browser to:
- Check if backend is running
- Test API endpoints directly
- Debug any issues

---

## Using the Application

### Enter a YouTube URL
Paste any YouTube link into the input field:
- **Regular videos**: `https://www.youtube.com/watch?v=VIDEO_ID`
- **YouTube Shorts**: `https://youtube.com/shorts/VIDEO_ID`
- **Short links**: `https://youtu.be/VIDEO_ID`

### Click "Analyze Video"
The system will:
1. Extract the video ID from the URL
2. Download the video and transcribe audio
3. Detect healthcare claims
4. Verify claims against trusted sources
5. Display results with reasoning

### Interpret Results

**If claims are found:**
- Original claim text
- Rewritten/structured claim
- Verdict (Supported/Unsupported/Weak Support)
- Confidence score
- Supporting evidence from medical sources

**If no claims found:**
- System shows "No healthcare claims detected"
- AI reasoning explains why
- This is **expected behavior** for non-medical content

---

## Understanding the Analysis

### Claim Detection Keywords
The system looks for medical/health-related sentences mentioning:
- **Treatments**: cure, treat, therapy, medication
- **Prevention**: prevent, reduce risk, avoid
- **Benefits**: helps, improve, enhance, boost
- **Conditions**: disease, illness, disorder, fever, pain
- **Health Terms**: health, wellness, nutrition, diet, supplement
- **Body Functions**: immune, digestion, metabolism, heart, brain
- **Evidence**: study, research, proven, clinical trial
- And more...

### Verdict Meanings
- ✅ **Supported** - Claim backed by evidence from WHO/CDC sources
- ⚠️ **Weak Support** - Limited evidence or conflicting sources
- ❌ **Unsupported** - Contradicts established medical knowledge

---

## Troubleshooting

### Issue: "Failed to connect to the analysis server"
**Solution:**
1. Make sure backend is running: `python backend/main.py`
2. Verify it's on port 8000 in the terminal output
3. Check firewall isn't blocking the connection

### Issue: "Transcript not available for this video"
**Solution:**
- The system will automatically fall back to Whisper AI to download and transcribe audio
- This may take longer (needs FFmpeg for audio extraction)
- Make sure you have an internet connection

### Issue: "Invalid YouTube URL"
**Solution:**
1. Use a valid YouTube URL format
2. Can't analyze private or age-restricted videos
3. Verify the video ID is correct

### Issue: Empty claims detected (no healthcare claims)
**Solution:**
- This is **correct behavior** for non-medical content
- The video's transcript doesn't contain medical/health keywords
- System still provides AI reasoning about the content

### Issue: "Port 8000 is already in use"
**Solution:**
1. Find what's using port 8000:
   ```bash
   # On Windows
   netstat -ano | findstr ":8000"
   taskkill /PID <process_id> /F
   
   # On Mac/Linux
   lsof -i :8000
   kill -9 <process_id>
   ```
2. Or change the port in `backend/main.py` and `app.js`

---

## Project Structure

```
LogiCheckAI/
├── index.html              # Main interface
├── app.js                  # Frontend logic
├── style.css               # Styling
├── test.html               # Testing interface
├── ISSUES_AND_FIXES.md     # Full documentation
│
└── backend/
    ├── main.py             # FastAPI server (MAIN ENTRY POINT)
    ├── requirements.txt    # Python dependencies
    ├── corpus/             # Medical knowledge sources
    │   ├── diabetes.txt
    │   ├── ors.txt
    │   └── vaccines.txt
    └── services/
        ├── youtube_service.py       # YouTube video handling
        ├── whisper_service.py       # Audio transcription
        ├── claim_detection.py       # Claim extraction (IMPROVED)
        ├── claim_rewriter.py        # Claim normalization
        ├── semantic_verification.py # Evidence retrieval
        ├── verdict_engine.py        # Fact-checking
        └── reasoning_service.py     # AI analysis
```

---

## Dependencies

Required Python packages (see `backend/requirements.txt`):
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `youtube-transcript-api` - Get video transcripts
- `yt-dlp` - Download videos
- `openai-whisper` - Transcribe audio (if transcript unavailable)
- `sentence-transformers` - Semantic search
- `scikit-learn` - Machine learning
- `beautifulsoup4` - Web scraping

Install all dependencies:
```bash
cd backend
pip install -r requirements.txt
```

---

## How It Works (Technical Overview)

### Pipeline Flow:
```
YouTube URL
    ↓
Extract Video ID (regex matches shorts, regular, short URLs)
    ↓
Try YouTube Transcript API
    ↓ (if not available)
Fallback: Download audio + Whisper AI transcription
    ↓
Clean & normalize text
    ↓
Split into sentences
    ↓
Detect healthcare claims (keyword matching)
    ↓
For each claim:
    • Rewrite claim for clarity
    • Retrieve evidence from corpus
    • Classify verdict (supported/weak/unsupported)
    ↓
Generate AI-powered reasoning
    ↓
Return JSON response with results
```

### Response Structure:
```json
{
  "claims": [
    {
      "original_claim": "...",
      "rewritten_claim": "...",
      "evidence": ["...", "..."],
      "verdict": "Supported"
    }
  ],
  "reasoning": "AI analysis explaining findings..."
}
```

---

## Next Steps & Improvements

### Current Limitations:
- Keyword-based claim detection (basic)
- Small medical corpus
- No real-time updates

### Suggested Improvements:
1. **AI-based Claims** - Use LLM (GPT-4, Claude) for intelligent claim extraction
2. **Larger Corpus** - Add more medical sources (PubMed, journals)
3. **User Feedback** - Store user corrections to improve accuracy
4. **Fact-checking Integration** - Connect to fact-checking APIs
5. **Multi-language Support** - Support non-English videos
6. **Browser Extension** - Quick verification while watching

---

## Support

If you encounter issues:
1. Check `test.html` to debug the backend
2. Look at browser console (F12 → Console) for errors
3. Check `backend/crash_log.txt` for server errors
4. Review `ISSUES_AND_FIXES.md` for detailed solutions

---

**Happy fact-checking! 🧬✨**
