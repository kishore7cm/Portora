export async function GET() {
  return Response.json({ 
    message: 'Portfolio API test endpoint working',
    timestamp: new Date().toISOString()
  });
}
