import * as admin from "firebase-admin";

if (!admin.apps.length) {
  const serviceAccountJson = process.env.FIREBASE_ADMIN_SA_JSON;
  
  if (!serviceAccountJson || serviceAccountJson === 'undefined') {
    throw new Error('FIREBASE_ADMIN_SA_JSON environment variable is not set or is undefined');
  }

  try {
    const serviceAccount = JSON.parse(serviceAccountJson);
    
    admin.initializeApp({
      credential: admin.credential.cert(serviceAccount),
    });
  } catch (error) {
    throw new Error(`Failed to parse FIREBASE_ADMIN_SA_JSON: ${error.message}`);
  }
}

export const db = admin.firestore();
export const authAdmin = admin.auth();