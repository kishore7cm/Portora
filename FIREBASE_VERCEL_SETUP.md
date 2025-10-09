# Firebase + Vercel Integration Setup Guide

## Overview
This guide explains how to connect Firebase to your Vercel-deployed Next.js application.

## Files Added
- `frontend/src/lib/firebaseClient.js` - Client-side Firebase configuration
- `frontend/src/lib/firebaseAdmin.js` - Server-side Firebase Admin configuration
- `backend/api/portfolio/route.js` - API route using Firebase Firestore

## Environment Variables Required

### Client-side Variables (NEXT_PUBLIC_*)
These are exposed to the browser and should be prefixed with `NEXT_PUBLIC_`:

```bash
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyAIQc85PpLp4_t3IjwyVo7eJI4BszG_p74
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=wealtheon-1d939.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=wealtheon-1d939
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=wealtheon-1d939.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=986272646985
NEXT_PUBLIC_FIREBASE_APP_ID=1:986272646985:web:0b2293495f9c2cce017c98
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=G-0W0HT17X7J
```

### Server-side Variables
These are only available on the server:

```bash
FIREBASE_ADMIN_SA_JSON={"type":"service_account","project_id":"wealtheon-1d939","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"firebase-adminsdk-fbsvc@wealtheon-1d939.iam.gserviceaccount.com","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"..."}
```

**Note**: Replace the `...` with your actual values from the JSON file.

## Setup Steps

### 1. Firebase Console Setup
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select existing one
3. Enable Firestore Database
4. Go to Project Settings → General → Your apps
5. Add a web app and copy the config values
6. Go to Project Settings → Service accounts
7. Generate a new private key (downloads JSON file)

### 2. Vercel Dashboard Setup
1. Go to your Vercel project dashboard
2. Navigate to Settings → Environment Variables
3. Add all the environment variables listed above
4. Make sure to set them for Production, Preview, and Development environments

### 3. Local Development Setup
Create a `.env.local` file in your frontend directory with the same variables:

```bash
# Copy the template above and replace with your actual values
```

### 4. Install Dependencies
```bash
cd frontend
npm install firebase firebase-admin
```

## Usage Examples

### Client-side Authentication
```javascript
import { auth } from '@/lib/firebaseClient';
import { signInWithEmailAndPassword } from 'firebase/auth';

// Sign in user
const signIn = async (email, password) => {
  try {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    return userCredential.user;
  } catch (error) {
    console.error('Sign in error:', error);
  }
};
```

### Server-side Firestore Operations
```javascript
import { db } from '@/lib/firebaseAdmin';

// Get user data
const getUserData = async (userId) => {
  const snapshot = await db.collection('users').doc(userId).get();
  return snapshot.data();
};
```

## Security Notes
- Never commit `.env.local` to version control
- Keep your service account JSON secure
- Use environment variables for all sensitive data
- Consider using Firebase Security Rules for Firestore

## Troubleshooting
- Ensure all environment variables are set in Vercel
- Check Firebase project permissions
- Verify service account has proper roles
- Test locally with `.env.local` first

## Next Steps
1. Set up Firebase Authentication
2. Configure Firestore Security Rules
3. Implement user management
4. Add data validation
5. Set up monitoring and logging
