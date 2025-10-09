import { db } from '@/lib/firebaseAdmin';

export async function GET() {
  try {
    // Test Firestore connection
    const testCollection = await db.collection('test').limit(1).get();
    
    return Response.json({ 
      success: true, 
      message: 'Firebase Admin connection successful',
      timestamp: new Date().toISOString(),
      projectId: process.env.FIREBASE_ADMIN_SA_JSON ? 'Service account configured' : 'No service account'
    });
  } catch (error) {
    console.error('Firebase Admin test error:', error);
    return Response.json({ 
      success: false, 
      error: error.message,
      timestamp: new Date().toISOString()
    }, { status: 500 });
  }
}
