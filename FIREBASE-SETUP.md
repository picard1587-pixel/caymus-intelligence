# Firebase Authentication Setup for Caymus

## Step 1: Create Firebase Project

1. Go to https://console.firebase.google.com/
2. Click "Create a project"
3. Name: `caymus-executive-search`
4. Disable Google Analytics (optional)
5. Click "Create"

## Step 2: Register Web App

1. In Firebase console, click "</>" (Add web app)
2. App nickname: `caymus-web`
3. **IMPORTANT**: Check "Also set up Firebase Hosting" 
4. Click "Register app"
5. You'll see Firebase configuration - copy it:

```javascript
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT.firebaseapp.com",
  projectId: "YOUR_PROJECT",
  storageBucket: "YOUR_PROJECT.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
};
```

## Step 3: Enable Authentication Methods

1. In left sidebar, click "Build" → "Authentication"
2. Click "Get started"
3. Click "Email/Password" → Enable → Save
4. (Optional) Enable Google: Click "Google" → Enable → Select support email → Save
5. (Optional) Enable GitHub: Click "GitHub" → Enable → You'll need to create OAuth app (see below)

## Step 4: Create GitHub OAuth App (for GitHub login)

1. Go to https://github.com/settings/developers
2. Click "New OAuth App"
3. Application name: `Caymus Executive Search`
4. Homepage URL: `https://yourusername.github.io/caymus/`
5. Authorization callback URL: `https://your-project.firebaseapp.com/__/auth/handler`
   (Replace `your-project` with your actual Firebase project ID)
6. Click "Register application"
7. Copy the Client ID and Client Secret
8. Paste them in Firebase GitHub auth settings

## Step 5: Configure Authorized Domains

1. In Firebase Auth, click "Settings" (gear icon) → "Authorized domains"
2. Click "Add domain"
3. Add: `yourusername.github.io` (replace with your GitHub username)
4. Also add: `localhost` (for testing)

## Step 6: Update HTML Files

Replace `YOUR_FIREBASE_CONFIG_HERE` in the HTML files with your actual Firebase config from Step 2.

## Step 7: Create First User

1. In Firebase Auth, click "Users" tab
2. Click "Add user"
3. Enter email and password
4. This is your admin account

## Testing Locally

Before pushing to GitHub:

1. Start local server: `python -m http.server 8000`
2. Open: `http://localhost:8000/news.html`
3. You should see login modal
4. Sign in with the user you created

## Troubleshooting

**"auth/invalid-api-key" error:**
- You didn't paste the Firebase config correctly
- Check Step 2 and ensure config is valid JSON

**"auth/unauthorized-domain" error:**
- Your domain isn't authorized
- Go to Firebase Auth → Settings → Authorized domains
- Add `localhost` for testing
- Add `yourusername.github.io` for production

**"auth/popup-closed-by-user" error:**
- Popup was blocked by browser
- Try allowing popups for your site

**Login button doesn't work:**
- Check browser console (F12) for errors
- Verify Firebase SDK loaded correctly
- Ensure config values are correct
