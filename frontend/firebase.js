// ============================================================
// firebase.js — Firebase SDK integration for StockMind AI
// Features: Auth (Google), Firestore (watchlist, history, alerts)
// ============================================================

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  signOut,
  onAuthStateChanged
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";
import {
  getFirestore,
  collection,
  doc,
  setDoc,
  getDoc,
  getDocs,
  deleteDoc,
  query,
  where,
  orderBy,
  limit,
  serverTimestamp,
  onSnapshot
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";

// ─── PASTE YOUR FIREBASE CONFIG HERE ───────────────────────
// Go to: https://console.firebase.google.com
// Project Settings → General → Your Apps → Web App → Config
const firebaseConfig = {
  apiKey:            "YOUR_API_KEY",
  authDomain:        "YOUR_PROJECT.firebaseapp.com",
  projectId:         "YOUR_PROJECT_ID",
  storageBucket:     "YOUR_PROJECT.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId:             "YOUR_APP_ID"
};
// ────────────────────────────────────────────────────────────

const app  = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db   = getFirestore(app);
const gProvider = new GoogleAuthProvider();

// ═══════════════════════════════════════════════════════════
// AUTH
// ═══════════════════════════════════════════════════════════

export async function signInWithGoogle() {
  const result = await signInWithPopup(auth, gProvider);
  return result.user;
}

export async function logOut() {
  await signOut(auth);
}

export function onAuthChange(callback) {
  return onAuthStateChanged(auth, callback);
}

export function currentUser() {
  return auth.currentUser;
}

// ═══════════════════════════════════════════════════════════
// WATCHLIST  (Firestore: users/{uid}/watchlist/{ticker})
// ═══════════════════════════════════════════════════════════

export async function addToWatchlist(ticker, stockData) {
  const uid = auth.currentUser?.uid;
  if (!uid) throw new Error("Not signed in");
  await setDoc(doc(db, "users", uid, "watchlist", ticker.toUpperCase()), {
    ticker: ticker.toUpperCase(),
    name:   stockData.name || ticker,
    price:  stockData.current_price,
    change_pct: stockData.change_pct,
    addedAt: serverTimestamp()
  });
}

export async function removeFromWatchlist(ticker) {
  const uid = auth.currentUser?.uid;
  if (!uid) throw new Error("Not signed in");
  await deleteDoc(doc(db, "users", uid, "watchlist", ticker.toUpperCase()));
}

export async function getWatchlist() {
  const uid = auth.currentUser?.uid;
  if (!uid) return [];
  const snap = await getDocs(collection(db, "users", uid, "watchlist"));
  return snap.docs.map(d => d.data());
}

export function watchlistListener(callback) {
  const uid = auth.currentUser?.uid;
  if (!uid) return () => {};
  return onSnapshot(collection(db, "users", uid, "watchlist"), snap => {
    callback(snap.docs.map(d => d.data()));
  });
}

// ═══════════════════════════════════════════════════════════
// PREDICTION HISTORY  (Firestore: users/{uid}/history/{auto-id})
// ═══════════════════════════════════════════════════════════

export async function savePrediction(ticker, stockData, sentimentData, predData) {
  const uid = auth.currentUser?.uid;
  if (!uid) return;   // silently skip if not signed in
  const ref = doc(collection(db, "users", uid, "history"));
  await setDoc(ref, {
    id:             ref.id,
    ticker:         ticker.toUpperCase(),
    price:          stockData.current_price,
    signal:         predData.signal,
    confidence:     predData.confidence,
    sentiment_score: sentimentData.sentiment_score,
    predicted_price: predData.predicted_next_day,
    change_pct:     predData.price_change_pct,
    analyzedAt:     serverTimestamp()
  });
}

export async function getPredictionHistory(limitCount = 20) {
  const uid = auth.currentUser?.uid;
  if (!uid) return [];
  const q = query(
    collection(db, "users", uid, "history"),
    orderBy("analyzedAt", "desc"),
    limit(limitCount)
  );
  const snap = await getDocs(q);
  return snap.docs.map(d => d.data());
}

export function historyListener(callback) {
  const uid = auth.currentUser?.uid;
  if (!uid) return () => {};
  const q = query(
    collection(db, "users", uid, "history"),
    orderBy("analyzedAt", "desc"),
    limit(10)
  );
  return onSnapshot(q, snap => {
    callback(snap.docs.map(d => d.data()));
  });
}

// ═══════════════════════════════════════════════════════════
// ALERTS  (Firestore: users/{uid}/alerts/{ticker})
// ═══════════════════════════════════════════════════════════

export async function setAlert(ticker, alertConfig) {
  // alertConfig: { priceAbove, priceBelow, sentimentShift, enabled }
  const uid = auth.currentUser?.uid;
  if (!uid) throw new Error("Not signed in");
  await setDoc(doc(db, "users", uid, "alerts", ticker.toUpperCase()), {
    ticker: ticker.toUpperCase(),
    ...alertConfig,
    enabled:   true,
    createdAt: serverTimestamp()
  });
}

export async function getAlerts() {
  const uid = auth.currentUser?.uid;
  if (!uid) return [];
  const snap = await getDocs(collection(db, "users", uid, "alerts"));
  return snap.docs.map(d => d.data());
}

export async function deleteAlert(ticker) {
  const uid = auth.currentUser?.uid;
  if (!uid) return;
  await deleteDoc(doc(db, "users", uid, "alerts", ticker.toUpperCase()));
}

export function alertsListener(callback) {
  const uid = auth.currentUser?.uid;
  if (!uid) return () => {};
  return onSnapshot(collection(db, "users", uid, "alerts"), snap => {
    callback(snap.docs.map(d => d.data()));
  });
}

// ═══════════════════════════════════════════════════════════
// ALERT CHECKER  (call after every stock fetch)
// ═══════════════════════════════════════════════════════════

export async function checkAlerts(stockData, sentimentScore) {
  const uid = auth.currentUser?.uid;
  if (!uid) return [];
  const alerts = await getAlerts();
  const triggered = [];

  for (const alert of alerts) {
    if (alert.ticker !== stockData.ticker || !alert.enabled) continue;
    const price = stockData.current_price;

    if (alert.priceAbove && price >= alert.priceAbove) {
      triggered.push({ type: "PRICE_HIGH", ticker: alert.ticker, message: `🚨 ${alert.ticker} crossed above $${alert.priceAbove} — now $${price}` });
    }
    if (alert.priceBelow && price <= alert.priceBelow) {
      triggered.push({ type: "PRICE_LOW", ticker: alert.ticker, message: `📉 ${alert.ticker} dropped below $${alert.priceBelow} — now $${price}` });
    }
    if (alert.sentimentShift) {
      if (sentimentScore > 70) triggered.push({ type: "SENTIMENT_BULLISH", ticker: alert.ticker, message: `📈 ${alert.ticker} sentiment turned very bullish (${sentimentScore}/100)` });
      if (sentimentScore < 30) triggered.push({ type: "SENTIMENT_BEARISH", ticker: alert.ticker, message: `📉 ${alert.ticker} sentiment turned very bearish (${sentimentScore}/100)` });
    }
  }
  return triggered;
}
