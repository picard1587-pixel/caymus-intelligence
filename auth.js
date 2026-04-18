// Firebase Authentication & Authorization Module for Caymus
// Include this script on all pages that require authentication

// ============================================
// FIREBASE CONFIG - Caymus Partners
// ============================================
const firebaseConfig = {
  apiKey: "AIzaSyCpShM5c0ZmYb_cf8snJRGt53f2rGQlCxI",
  authDomain: "caymus-partners.firebaseapp.com",
  projectId: "caymus-partners",
  storageBucket: "caymus-partners.firebasestorage.app",
  messagingSenderId: "407604863980",
  appId: "1:407604863980:web:cf6238fad34280e63f96c9"
};

// ============================================
// AUTHORIZED USERS - ONLY THESE EMAILS CAN ACCESS
// ============================================
const ALLOWED_EMAILS = [
  "taftw86@gmail.com",    // Replace with actual email
  "picard1587@gmail.com",    // Replace with actual email
  "user3@example.com"     // Replace with actual email
];

// Or use UIDs (more secure):
const ALLOWED_UIDS = [
  // "uid1_here",
  // "uid2_here",
  // "uid3_here"
];

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();

// Auth state management
let currentUser = null;

// Access Denied Modal HTML
const accessDeniedHTML = `
  <div id="access-denied-modal" style="
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1001;
  ">
    <div style="
      background: var(--bg-elevated);
      border: 1px solid var(--border-default);
      border-radius: var(--radius-lg);
      padding: 40px;
      width: 100%;
      max-width: 450px;
      text-align: center;
    ">
      <div style="
        width: 64px;
        height: 64px;
        background: var(--red-dim);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 24px;
      ">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--red)" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="15" y1="9" x2="9" y2="15"/>
          <line x1="9" y1="9" x2="15" y2="15"/>
        </svg>
      </div>
      <h2 style="font-size: 22px; font-weight: 700; color: var(--text-primary); margin-bottom: 12px;">
        Access Denied
      </h2>
      <p style="font-size: 14px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 24px;">
        You are not authorized to access this application.<br><br>
        Please contact the administrator if you believe this is an error.
      </p>
      <div style="font-size: 13px; color: var(--text-tertiary); margin-bottom: 20px;" id="denied-email">
      </div>
      <button id="sign-out-denied" style="
        height: 40px;
        padding: 0 24px;
        background: var(--bg-overlay);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-sm);
        font-size: 14px;
        color: var(--text-primary);
        cursor: pointer;
      ">
        Sign Out
      </button>
    </div>
  </div>
`;

// Login Modal HTML
const loginModalHTML = `
  <div id="auth-modal" style="
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(4px);
  ">
    <div style="
      background: var(--bg-elevated);
      border: 1px solid var(--border-default);
      border-radius: var(--radius-lg);
      padding: 32px;
      width: 100%;
      max-width: 400px;
      box-shadow: var(--shadow-md);
    ">
      <div style="text-align: center; margin-bottom: 24px;">
        <div style="
          width: 48px;
          height: 48px;
          background: var(--accent);
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 16px;
          font-size: 20px;
          font-weight: 700;
          color: white;
        ">C</div>
        <h2 style="font-size: 20px; font-weight: 700; color: var(--text-primary); margin-bottom: 8px;">Sign in to Caymus</h2>
        <p style="font-size: 13px; color: var(--text-secondary);">Executive Search Platform</p>
        <p style="font-size: 11px; color: var(--text-tertiary); margin-top: 8px;">Authorized personnel only</p>
      </div>

      <div id="auth-error" style="
        background: var(--red-dim);
        color: var(--red);
        padding: 12px;
        border-radius: var(--radius-sm);
        font-size: 13px;
        margin-bottom: 16px;
        display: none;
      "></div>

      <div style="display: grid; gap: 8px; margin-bottom: 20px;">
        <button
          id="google-login-btn"
          style="
            height: 44px;
            background: var(--bg-overlay);
            border: 1px solid var(--border-default);
            border-radius: var(--radius-sm);
            font-size: 14px;
            color: var(--text-primary);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
          "
        >
          <svg width="18" height="18" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
          Sign in with Google
        </button>

        <button
          id="github-login-btn"
          style="
            height: 44px;
            background: var(--bg-overlay);
            border: 1px solid var(--border-default);
            border-radius: var(--radius-sm);
            font-size: 14px;
            color: var(--text-primary);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
          "
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
          Sign in with GitHub
        </button>
      </div>

      <div style="text-align: center; font-size: 11px; color: var(--text-tertiary);">
        By signing in, you agree to our Terms of Service
      </div>
    </div>
  </div>
`;

// Show login modal
function showLoginModal() {
  if (document.getElementById('auth-modal')) return;
  if (document.getElementById('access-denied-modal')) return;

  const modalContainer = document.createElement('div');
  modalContainer.innerHTML = loginModalHTML;
  document.body.appendChild(modalContainer);

  // Add event listeners - query from the injected container
  const googleBtn = modalContainer.querySelector('#google-login-btn');
  const githubBtn = modalContainer.querySelector('#github-login-btn');

  if (googleBtn) {
    googleBtn.addEventListener('click', handleGoogleLogin);
    console.log('Google login listener attached');
  } else {
    console.error('Google login button not found');
  }

  if (githubBtn) {
    githubBtn.addEventListener('click', handleGitHubLogin);
    console.log('GitHub login listener attached');
  } else {
    console.error('GitHub login button not found');
  }
}

// Show access denied modal
function showAccessDeniedModal(email) {
  if (document.getElementById('auth-modal')) {
    document.getElementById('auth-modal').remove();
  }
  if (document.getElementById('access-denied-modal')) return;

  const modalContainer = document.createElement('div');
  modalContainer.innerHTML = accessDeniedHTML;
  document.body.appendChild(modalContainer);

  // Show the attempted email
  const emailDiv = document.getElementById('denied-email');
  if (emailDiv && email) {
    emailDiv.textContent = `Attempted: ${email}`;
  }

  // Add sign out listener
  document.getElementById('sign-out-denied').addEventListener('click', () => {
    auth.signOut();
  });
}

// Hide all modals
function hideAllModals() {
  const authModal = document.getElementById('auth-modal');
  const deniedModal = document.getElementById('access-denied-modal');
  if (authModal) authModal.remove();
  if (deniedModal) deniedModal.remove();
}

// Check if user is authorized
function isAuthorized(user) {
  if (!user) return false;

  // Check by email
  if (ALLOWED_EMAILS.includes(user.email)) {
    return true;
  }

  // Check by UID (more secure)
  if (ALLOWED_UIDS.length > 0 && ALLOWED_UIDS.includes(user.uid)) {
    return true;
  }

  return false;
}

// Show error
function showAuthError(message) {
  const errorDiv = document.getElementById('auth-error');
  if (errorDiv) {
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
  }
}

// Google login
async function handleGoogleLogin() {
  console.log('Google login button clicked');
  const provider = new firebase.auth.GoogleAuthProvider();
  try {
    console.log('Opening Google popup...');
    const result = await auth.signInWithPopup(provider);
    console.log('Popup result:', result);
    // Authorization check happens in onAuthStateChanged
  } catch (error) {
    console.error('Google login error:', error.code, error.message);
    console.error('Full error:', error);
    if (error.code === 'auth/popup-blocked') {
      showAuthError('Popup was blocked. Please allow popups for this site.');
    } else {
      showAuthError(getErrorMessage(error.code) + ' (' + error.code + ')');
    }
  }
}

// GitHub login
async function handleGitHubLogin() {
  const provider = new firebase.auth.GithubAuthProvider();
  try {
    await auth.signInWithPopup(provider);
    // Authorization check happens in onAuthStateChanged
  } catch (error) {
    if (error.code === 'auth/popup-blocked') {
      showAuthError('Popup was blocked. Please allow popups for this site.');
    } else {
      showAuthError(getErrorMessage(error.code));
    }
  }
}

// Error message mapping
function getErrorMessage(code) {
  const messages = {
    'auth/invalid-email': 'Invalid email address',
    'auth/user-disabled': 'This account has been disabled',
    'auth/user-not-found': 'No account found with this email',
    'auth/wrong-password': 'Incorrect password',
    'auth/invalid-credential': 'Invalid login credentials',
    'auth/too-many-requests': 'Too many attempts. Try again later',
    'auth/popup-closed-by-user': 'Login popup was closed',
    'auth/unauthorized-domain': 'This domain is not authorized',
    'auth/invalid-api-key': 'Firebase configuration error',
    'auth/network-request-failed': 'Network error. Check your connection'
  };
  return messages[code] || 'Login failed. Please try again.';
}

// Update UI for logged-in user
function updateUIForUser(user) {
  currentUser = user;

  // Update sidebar user card
  const userCard = document.querySelector('.user-card');
  if (userCard) {
    const avatar = userCard.querySelector('.avatar');
    const userName = userCard.querySelector('.user-name');
    const userRole = userCard.querySelector('.user-role');

    if (avatar) {
      if (user.photoURL) {
        avatar.innerHTML = `<img src="${user.photoURL}" style="width: 100%; height: 100%; border-radius: 8px; object-fit: cover;">`;
      } else {
        avatar.textContent = (user.displayName || user.email || 'User').charAt(0).toUpperCase();
      }
    }
    if (userName) userName.textContent = user.displayName || user.email.split('@')[0];
    if (userRole) userRole.textContent = 'Authorized User';

    // Add logout button
    if (!document.getElementById('logout-btn')) {
      const logoutBtn = document.createElement('button');
      logoutBtn.id = 'logout-btn';
      logoutBtn.textContent = 'Sign Out';
      logoutBtn.style.cssText = `
        margin-top: 8px;
        font-size: 11px;
        color: var(--text-tertiary);
        background: transparent;
        border: none;
        cursor: pointer;
      `;
      logoutBtn.onclick = () => auth.signOut();
      userCard.appendChild(logoutBtn);
    }
  }
}

// Auth state listener
auth.onAuthStateChanged((user) => {
  if (user) {
    console.log('User signed in:', user.email);

    // Check authorization
    if (isAuthorized(user)) {
      // Authorized - show the app
      console.log('User authorized');
      hideAllModals();
      updateUIForUser(user);

      // Enable interaction
      document.body.style.pointerEvents = 'auto';
    } else {
      // Not authorized - show access denied
      console.log('User NOT authorized:', user.email);
      showAccessDeniedModal(user.email);

      // Block interaction
      document.body.style.pointerEvents = 'none';
      const deniedModal = document.getElementById('access-denied-modal');
      if (deniedModal) {
        deniedModal.style.pointerEvents = 'auto';
      }
    }
  } else {
    // Not signed in
    console.log('No user signed in');
    showLoginModal();

    // Block interaction
    document.body.style.pointerEvents = 'none';
    const modal = document.getElementById('auth-modal');
    if (modal) {
      modal.style.pointerEvents = 'auto';
    }
  }
});

// Initialize auth check on page load
document.addEventListener('DOMContentLoaded', () => {
  console.log('Firebase Auth initialized');
});
