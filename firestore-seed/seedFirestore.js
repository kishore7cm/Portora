import { initializeApp } from "firebase/app";
import { getFirestore, collection, addDoc, doc, setDoc } from "firebase/firestore";
import fs from "fs";

// read JSON manually
const rawData = fs.readFileSync("./usMarketMockData.json");
const mockData = JSON.parse(rawData);

// 🔑 Replace these with your Firebase config
const firebaseConfig = {
    apiKey: "AIzaSyAIQc85PpLp4_t3IjwyVo7eJI4BszG_p74",
    authDomain: "wealtheon-1d939.firebaseapp.com",
    projectId: "wealtheon-1d939",
    storageBucket: "wealtheon-1d939.firebasestorage.app",
    messagingSenderId: "986272646985",
    appId: "1:986272646985:web:0b2293495f9c2cce017c98"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

async function seedFirestore() {
    try {
      // Insert USERS (only if present)
      if (mockData.users && Array.isArray(mockData.users)) {
        for (const user of mockData.users) {
          // Use setDoc with user_id as document ID instead of addDoc
          await setDoc(doc(db, "users", user.user_id), user);
        }
        console.log(`✅ Inserted ${mockData.users.length} user documents`);
      } else {
        console.log("⚠️ No users array found — skipping user insert");
      }
  
      // Insert PORTFOLIO DATA (only if present)
      if (mockData.portfolio_data && Array.isArray(mockData.portfolio_data)) {
        for (const portfolio of mockData.portfolio_data) {
          // Use setDoc with user_id as document ID instead of addDoc
          await setDoc(doc(db, "portfolio_data", portfolio.user_id), portfolio);
        }
        console.log(`✅ Inserted ${mockData.portfolio_data.length} portfolio documents`);
      } else {
        console.log("⚠️ No portfolio_data array found — skipping portfolio insert");
      }
  
      console.log("✅ Mock data successfully inserted!");
    } catch (err) {
      console.error("❌ Error inserting mock data:", err);
    }
  }
  
  seedFirestore();