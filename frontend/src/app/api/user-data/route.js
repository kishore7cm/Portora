import { db } from '../../../lib/firebaseAdmin';

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('user_id');
    
    if (!userId) {
      return Response.json({ 
        error: 'User ID is required',
        message: 'Please provide a valid user_id parameter'
      }, { status: 400 });
    }
    
    console.log('👤 Fetching user data for user:', userId);
    
    // Get user data from Firebase
    const userDoc = await db.collection('users').doc(userId).get();
    
    if (!userDoc.exists) {
      return Response.json({ 
        success: false,
        message: 'User not found',
        user_id: userId 
      });
    }
    
    const userData = userDoc.data();
    console.log('✅ User data fetched successfully:', userData);
    
    return Response.json({ 
      success: true,
      user_data: userData,
      user_id: userId,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('❌ Firebase user data error:', error);
    return Response.json({ 
      error: 'Failed to fetch user data',
      details: error.message,
      timestamp: new Date().toISOString()
    }, { status: 500 });
  }
}
