import * as admin from "firebase-admin";

let db = null;
let authAdmin = null;

// Only initialize Firebase admin if we're in a server environment and have valid credentials
if (typeof window === 'undefined' && !admin.apps.length) {
  const serviceAccountJson = process.env.FIREBASE_ADMIN_SA_JSON;
  
  if (!serviceAccountJson || serviceAccountJson === 'undefined') {
    console.warn('⚠️ FIREBASE_ADMIN_SA_JSON environment variable is not set. Firebase admin features will be disabled.');
  } else {
    try {
      // Validate JSON format before parsing
      if (serviceAccountJson.length < 100) {
        throw new Error('Service account JSON appears to be truncated');
      }
      
      const serviceAccount = JSON.parse(serviceAccountJson);
      
      // Validate required fields
      if (!serviceAccount.type || !serviceAccount.project_id || !serviceAccount.private_key) {
        throw new Error('Service account JSON is missing required fields');
      }
      
      admin.initializeApp({
        credential: admin.credential.cert(serviceAccount),
      });
      
      db = admin.firestore();
      authAdmin = admin.auth();
      console.log('✅ Firebase admin initialized successfully');
    } catch (error) {
      console.error('❌ Failed to initialize Firebase admin:', error.message);
      console.warn('⚠️ Firebase admin features will be disabled. API will use fallback data.');
    }
  }
}

export { db, authAdmin };