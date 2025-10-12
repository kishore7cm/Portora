import { db } from '../../src/lib/firebaseAdmin';

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const userId = req.query.user_id || '1';
    console.log('👤 Fetching user data for userId:', userId);

    // Get user data from users collection
    const usersSnapshot = await db.collection('users').where('uid', '==', userId).get();
    
    if (usersSnapshot.empty) {
      // Try with user_id field if uid doesn't work
      const usersSnapshot2 = await db.collection('users').where('user_id', '==', userId).get();
      
      if (usersSnapshot2.empty) {
        // Return default values if no user found
        return res.status(200).json({
          success: true,
          user_data: {
            last_year_value: 300000, // Default fallback
            uid: userId
          },
          message: 'Using default user data'
        });
      }
      
      const userData = usersSnapshot2.docs[0].data();
      return res.status(200).json({
        success: true,
        user_data: {
          last_year_value: userData.last_year_value || 300000,
          uid: userData.uid || userId,
          name: userData.name || 'User',
          email: userData.email || 'user@example.com'
        }
      });
    }

    const userData = usersSnapshot.docs[0].data();
    console.log('✅ User data found:', userData);

    res.status(200).json({
      success: true,
      user_data: {
        last_year_value: userData.last_year_value || 300000,
        uid: userData.uid || userId,
        name: userData.name || 'User',
        email: userData.email || 'user@example.com'
      }
    });

  } catch (error) {
    console.error('❌ Firebase user data error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch user data',
      details: error.message,
      user_data: {
        last_year_value: 300000, // Fallback
        uid: req.query.user_id || '1'
      }
    });
  }
}
