import express from "express";
import * as admin from "firebase-admin";

const router = express.Router();

// Initialize Firebase Admin (if not initialized)
if (!admin.apps.length) {
  const serviceAccount = JSON.parse(process.env.FIREBASE_ADMIN_SA_JSON);
  admin.initializeApp({
    credential: admin.credential.cert(serviceAccount),
  });
}
const db = admin.firestore();

router.get("/", async (req, res) => {
  try {
    const { user_id } = req.query;
    const snapshot = await db
      .collection("portfolio_data")
      .where("user_id", "==", Number(user_id))
      .get();

    const data = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    res.status(200).json({ data });
  } catch (err) {
    console.error("❌ Firestore error:", err);
    res.status(500).json({ error: "Internal Server Error" });
  }
});

export default router;