# PWA Testing Guide — Whirlwind KB
**Date Created**: February 7, 2026  
**Status**: Ready for Testing

---

## PWA Configuration Status ✅

### What's Configured

| Component | Status | Details |
|-----------|--------|---------|
| **Icons** | ✅ Added | pwa-192.png (192×192) + pwa-512.png (512×512) |
| **Manifest** | ✅ Generated | `dist/manifest.webmanifest` |
| **Service Worker** | ✅ Generated | `dist/sw.js` (via Workbox) |
| **Vite PWA Plugin** | ✅ Configured | `frontend/vite.config.ts` |
| **RegisterSW.js** | ✅ Generated | `dist/registerSW.js` |

### Manifest Details

**File**: `dist/manifest.webmanifest`

```json
{
  "name": "Whirlwind KB",
  "short_name": "WhirlwindKB",
  "description": "Source-grounded knowledge base for organization building...",
  "theme_color": "#05441d",
  "background_color": "#fdfbf7",
  "display": "standalone",
  "icons": [
    {
      "src": "pwa_192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "pwa_512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

---

## Testing Procedures

### Test 1: Desktop Browser (Chrome/Edge)

**Prerequisites**:
- Backend running (not strictly required, but recommended)
- Frontend running or deployed
- Chrome/Edge browser

**Steps**:

1. **Open app** in Chrome
   - URL: http://127.0.0.1:4173 (local) or https://your-domain.com (deployed)

2. **Open DevTools** (F12)
   - Go to **Application** tab
   - Left sidebar: **Manifest**
   - **Expected**: Manifest displays all fields (name, icons, colors, etc.) ✅

3. **Check Service Worker**
   - DevTools **Application** → **Service Workers**
   - **Expected**: Shows "registerSW.js" with status ✅ (active and running)

4. **Check Cache**
   - DevTools **Application** → **Cache Storage**
   - **Expected**: Shows precached files (JS, CSS, assets) ✅

5. **Install prompt**
   - Address bar (right side) should show **"Install"** or **"Add WhirlwindKB"** button
   - Click it → app installs as standalone window
   - **Expected**: App opens in its own window without browser chrome ✅

6. **Offline functionality** (optional)
   - After installing, toggle DevTools **Network** → **Offline**
   - Try navigating the app
   - **Expected**: Static pages load, API calls fail gracefully ✅

---

### Test 2: iPhone (Safari)

**Prerequisites**:
- iPhone with Safari (iOS 15.1+)
- App deployed at HTTPS (required by Apple)
- Manifest with icons

**Steps**:

1. **Open Safari** → navigate to HTTPS app URL
   - Example: https://app.your-domain.com

2. **Tap Share button** (lower right, arrow/box icon)

3. **Tap "Add to Home Screen"**

4. **Verify**:
   - App name displays ✅
   - Icon shown (should be 192x192 or 512x512) ✅
   - Tap "Add" → app installs to home screen

5. **Open from home screen**
   - Tap the installed app icon
   - **Expected**: Opens full-screen without Safari chrome ✅
   - URL bar hidden ✅
   - App theme colors visible ✅

6. **Offline test** (optional)
   - Open app while offline (airplane mode)
   - **Expected**: Homepage and cached pages load ✅

---

### Test 3: Android (Chrome)

**Prerequisites**:
- Android 5.0+ device with Chrome
- App deployed at HTTPS
- Manifest with icons

**Steps**:

1. **Open Chrome** → navigate to HTTPS app URL

2. **Wait for install prompt**
   - Chrome shows **"Install app"** button in address bar or floating prompt
   - **Expected**: Takes 2-3 seconds to appear after page loads ✅

3. **Tap install**
   - Dialog: "Install 'Whirlwind KB'?"
   - OK → installs

4. **Verify**:
   - App appears on home screen ✅
   - Icon matches 192x192 or 512x512 ✅
   - Tap → opens full-screen ✅

5. **Check web app settings**
   - Chrome Menu → **Settings** → **Apps and notifications** → **App shortcuts**
   - "Whirlwind KB" listed ✅

---

## Expected Behaviors

| Action | Expected | Status |
|--------|----------|--------|
| **Install on desktop** | Install button in address bar | ✅ Chrome/Edge |
| **Install on iPhone** | Share → Add to Home Screen | ✅ Safari iOS 15.1+ |
| **Install on Android** | Install banner or prompt | ✅ Chrome 31+ |
| **App icon** | Uses pwa_192.png or pwa_512.png | ✅ Configured |
| **App name** | "Whirlwind KB" | ✅ In manifest |
| **Splash screen** | Theme colors (dark green, light tan) | ✅ Configured |
| **Standalone mode** | No browser chrome on open | ✅ display: standalone |
| **Theme color** | Dark green (#05441d) address bar | ✅ Configured |
| **Service Worker** | Auto-updates on each app launch | ✅ registerType: autoUpdate |

---

## Troubleshooting

### Issue: Install button not appearing

**Cause**: Service Worker not registered or icon missing  
**Fix**:
1. Check DevTools > Application > Manifest — all fields present?
2. Check icons exist: `frontend/public/pwa_192.png` and `pwa_512.png`
3. Rebuild: `npm run build`
4. Clear cache: DevTools > Application > Clear storage > Clear site data
5. Reload page

### Issue: Wrong icon displaying

**Cause**: Browser cached old manifest  
**Fix**:
1. Ensure new icons in `frontend/public/`
2. Rebuild frontend: `npm run build`
3. Clear browser cache and app data
4. Remove app from home screen and reinstall

### Issue: "Add to Home Screen" not working on iPhone

**Cause**: Not at HTTPS or iOS < 15.1  
**Fix**:
1. Verify URL is HTTPS (not HTTP)
2. Update iOS to 15.1+
3. Ensure Safari is default browser
4. Try another device/iOS version

### Issue: App crashes or goes offline

**Cause**: Missing environment variables or backend connection  
**Fix**:
1. Check `VITE_API_BASE_URL` set correctly at build time
2. Verify backend is running
3. Check browser console for errors (DevTools)
4. Clear app data and reinstall

---

## Testing Checklist

### Desktop (Chrome/Edge)
- [ ] Manifest displays correctly in DevTools
- [ ] Service Worker shows as "active"  
- [ ] Install button appears in address bar
- [ ] Clicking install opens app standalone
- [ ] App shows correct name and icon
- [ ] App theme color visible (dark green)
- [ ] Offline mode gracefully degrades (no crashes)

### iPhone (Safari)
- [ ] App deployed at HTTPS
- [ ] Share → Add to Home Screen works
- [ ] Icon displays (192×192 or 512×512)
- [ ] App opens full-screen without Safari UI
- [ ] App name is "Whirlwind KB"
- [ ] Splash screen shows theme colors

### Android (Chrome)
- [ ] Install prompt appears (within 2-3 sec)
- [ ] Install creates app on home screen
- [ ] Icon correct size and appearance
- [ ] App opens full-screen standalone
- [ ] Theme color (dark green) visible in address bar
- [ ] Offline pages still load (cached)

---

## After Testing

### If all tests pass ✅
- PWA is production-ready
- Users can install on mobile/desktop
- App works offline for cached pages

### If tests fail ⚠️
- Check troubleshooting section above
- Rebuild: `npm run build`
- Redeploy frontend
- Clear user cache and retry

### Recommended User Instructions

**For end users** (put in FAQ or Help section):

**iPhone (Safari)**:
1. Open Whirlwind KB in Safari
2. Tap Share (arrow box icon, lower right)
3. Tap "Add to Home Screen"
4. Tap "Add" in the dialog
5. Open app from home screen

**Android (Chrome)**:
1. Open Whirlwind KB in Chrome
2. Look for "Install app" prompt
3. Tap "Install"
4. Tap "Install" on the confirmation dialog
5. Open app from home screen

**Windows/Mac (Chrome/Edge)**:
1. Visit Whirlwind KB website
2. Click the "instal" button in the address bar
3. Click "Install"
4. Launch from app menu or Start menu

---

## PWA Benefits Now Live

Once deployed and tested:

✅ **Installable**: Users can add to home screen  
✅ **Fast**: Service Worker caches static assets  
✅ **Offline**: Cached pages work without internet  
✅ **Reliable**: Auto-updates when you deploy new version  
✅ **App-like**: Full-screen, no browser chrome  
✅ **Discoverable**: Works like native app on all devices  

---

**Status**: 🟢 **Ready for testing** — PWA fully configured, just need to test on devices.
