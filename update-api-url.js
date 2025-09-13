// Script to update API URL in frontend
const fs = require('fs');
const path = require('path');

// Replace this with your actual Render backend URL
const BACKEND_URL = 'https://your-backend-url.onrender.com';

// Update config.ts
const configPath = path.join(__dirname, 'frontend/src/lib/config.ts');
let configContent = fs.readFileSync(configPath, 'utf8');

configContent = configContent.replace(
  /const API_BASE_URL = process\.env\.NEXT_PUBLIC_API_URL \|\| 'http:\/\/localhost:8000';/,
  `const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '${BACKEND_URL}';`
);

fs.writeFileSync(configPath, configContent);
console.log('✅ Updated API URL in config.ts');
console.log(`Backend URL: ${BACKEND_URL}`);
