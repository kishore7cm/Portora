import * as admin from "firebase-admin";

let db = null;
let authAdmin = null;

if (!admin.apps.length) {
  const serviceAccountJson = process.env.FIREBASE_ADMIN_SA_JSON;
  
  if (!serviceAccountJson || serviceAccountJson === 'undefined') {
    console.warn('⚠️ FIREBASE_ADMIN_SA_JSON environment variable is not set. Firebase admin features will be disabled.');
    // Don't throw error, just log warning
  } else {
    try {
      const serviceAccount = JSON.parse(serviceAccountJson);
      
      admin.initializeApp({
        credential: admin.credential.cert(serviceAccount),
      });
      
      db = admin.firestore();
      authAdmin = admin.auth();
      console.log('✅ Firebase admin initialized successfully');
    } catch (error) {
      console.error('❌ Failed to parse FIREBASE_ADMIN_SA_JSON:', error.message);
      // Don't throw error, just log error
    }
  }
}

export { db, authAdmin };