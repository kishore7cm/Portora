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
    
    console.log('🔍 Checking existing data for user:', userId);
    
    // Check if user has data in new structure (single document)
    const newStructureDoc = await db.collection('portfolio_data').doc(userId).get();
    
    // Check if user has data in old structure (multiple documents with user_id field)
    const oldStructureSnapshot = await db
      .collection('portfolio_data')
      .where('user_id', '==', userId)
      .get();
    
    // Check if user has data with user_id = 1 (legacy data)
    const legacySnapshot = await db
      .collection('portfolio_data')
      .where('user_id', '==', '1')
      .get();
    
    const results = {
      user_id: userId,
      new_structure: {
        exists: newStructureDoc.exists,
        holdings_count: newStructureDoc.exists ? (newStructureDoc.data().holdings?.length || 0) : 0
      },
      old_structure: {
        exists: !oldStructureSnapshot.empty,
        documents_count: oldStructureSnapshot.size
      },
      legacy_data: {
        exists: !legacySnapshot.empty,
        documents_count: legacySnapshot.size
      }
    };
    
    console.log('📊 Data check results:', results);
    
    return Response.json({ 
      success: true,
      data: results,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('❌ Error checking existing data:', error);
    return Response.json({ 
      error: 'Failed to check existing data',
      details: error.message,
      timestamp: new Date().toISOString()
    }, { status: 500 });
  }
}
