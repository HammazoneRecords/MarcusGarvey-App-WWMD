# Debug Guide: API Key Transfer

## Step 1: Start the Backend with Debug Output

```bash
cd backend
python api/server.py
```

Watch the console for debug messages.

---

## Step 2: Test the Flow

### Via Browser:
1. Open Profile page
2. Scroll to **AI / API** section
3. Enter your Gemini API key in the **Google Gemini** field
4. **Important**: Refresh the page or navigate away and back to ensure localStorage is saved
5. Go to **Garvey Lens** (WWMD) page
6. Enter a situation (e.g., "How do I build a strong community?")
7. Click "Analyze with Garvey Lens"
8. **Check the browser console** (F12 → Console tab) for the logged apiConfig
9. **Check the backend terminal** for debug messages

### What to Look For:

**In Browser Console:**
```
Current apiConfig: { 
  hasKey: true,          // Should be true if key entered
  keyLength: 39,         // Gemini keys are ~39 chars
  provider: "gemini"     // or "openai" depending on selection
}
```

**In Backend Terminal:**
```
DEBUG: Using user-provided API key: AIza...XXXX
DEBUG: /api/wwmd endpoint received data with apiConfig
```

---

## Step 3: Check Key Entry Path

### If the key is NOT being stored in Profile:
1. Open **Developer Tools** (F12)
2. Go to **Application → Local Storage**
3. Find entry with key `whirlwind-kb-storage`
4. Check if `apiConfig.geminiApiKey` has your key

### If the key is NOT being sent to backend:
1. Open **Developer Tools** (F12)
2. Go to **Network** tab
3. Submit the WWMD form
4. Click on the request to `/api/wwmd`
5. Go to **Request** tab and expand JSON body
6. Look for `"apiConfig": { "geminiApiKey": "..." }`

---

## Step 4: Common Issues

### Issue: "Gemini API key is missing or invalid"
- **Cause**: Key was empty string or not valid format
- **Fix**: Verify your actual Gemini API key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### Issue: Key entered in Profile but doesn't persist
- **Cause**: Browser localStorage not saving
- **Fix**: Open DevTools → Check if Site has permission to store data

### Issue: Backend says "No user API key provided"
- **Cause**: Frontend didn't send apiConfig in request body
- **Fix**: Check Network tab to verify JSON includes apiConfig

### Issue: Backend receives empty key
- **Cause**: Front-end sent `apiConfig: { geminiApiKey: "" }`
- **Fix**: Clear the input field and re-enter the key (no trailing spaces)

---

## Step 5: Manual Testing (via curl)

```bash
# Test WWMD endpoint with user API key
curl -X POST http://localhost:5050/api/wwmd \
  -H "Content-Type: application/json" \
  -d '{
    "situation": "How do I organize a community effectively?",
    "mode": "Personal",
    "apiConfig": {
      "provider": "gemini",
      "geminiApiKey": "YOUR_ACTUAL_API_KEY_HERE"
    }
  }'
```

Check backend console for `DEBUG: Using user-provided API key:` message.

---

## What to Report

Once you see the issue, please share:

1. **The exact error message** you receive
2. **Browser console output** (F12 → Console)
3. **Backend terminal output** (when you submit the form)
4. **Network request body** (F12 → Network → Request tab for /api/wwmd)

This will help identify exactly where the key is being lost.

---

## Quick Restart

If something is cached wrong:

```bash
# Clear browser cache for localStorage
# F12 → Application → Local Storage → right-click → Clear All

# Restart backend
# Ctrl+C in terminal, then run again:
python api/server.py

# Refresh browser page
# Ctrl+Shift+R (hard refresh)
```
