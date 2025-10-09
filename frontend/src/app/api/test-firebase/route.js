export async function GET() {
  try {
    // Check if Firebase Admin environment variable is set
    const serviceAccountJson = process.env.FIREBASE_ADMIN_SA_JSON;
    
    if (!serviceAccountJson || serviceAccountJson === 'undefined') {
      return Response.json({ 
        success: false, 
        message: 'Firebase Admin service account not configured',
        timestamp: new Date().toISOString(),
        error: 'FIREBASE_ADMIN_SA_JSON environment variable is missing or undefined'
      }, { status: 500 });
    }

    // Dynamically import Firebase Admin to avoid build-time errors
    const { db } = await import('@/lib/firebaseAdmin');
    
    // Test Firestore connection
    const testCollection = await db.collection('test').limit(1).get();
    
    return Response.json({ 
      success: true, 
      message: 'Firebase Admin connection successful',
      timestamp: new Date().toISOString(),
      projectId: 'Service account configured'
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
