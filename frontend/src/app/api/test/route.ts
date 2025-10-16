import { NextRequest } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('user_id');
    
    return Response.json({ 
      message: 'API is working!',
      user_id: userId,
      timestamp: new Date().toISOString(),
      status: 'success'
    });
    
  } catch (error: any) {
    return Response.json({ 
      error: 'Test API failed',
      details: error.message,
      timestamp: new Date().toISOString()
    }, { status: 500 });
  }
}
