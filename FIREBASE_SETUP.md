# 🔥 Firebase Setup Guide

Follow these steps to connect Firebase Firestore to StockMind AI.
Takes about 5 minutes. It's completely FREE.

---

## Step 1 — Create a Firebase Project

1. Go to https://console.firebase.google.com
2. Click **"Add project"**
3. Name it: `stockmind-ai` (or anything you like)
4. Disable Google Analytics (optional) → **Create project**

---

## Step 2 — Enable Firestore Database

1. In your Firebase project, click **"Firestore Database"** in the left sidebar
2. Click **"Create database"**
3. Choose **"Start in test mode"** (allows all reads/writes — fine for demo)
4. Select any region → **Enable**

---

## Step 3 — Register a Web App

1. Click the **⚙️ gear icon** → **Project Settings**
2. Scroll to **"Your apps"** → click the **`</>`** (Web) icon
3. App nickname: `stockmind-web` → click **Register app**
4. You'll see a `firebaseConfig` object — **copy it**

---

## Step 4 — Paste Config into index.html

Open `frontend/index.html` and find this block near the top (~line 20):

```javascript
const firebaseConfig = {
  apiKey:            "YOUR_API_KEY",
  authDomain:        "YOUR_PROJECT.firebaseapp.com",
  projectId:         "YOUR_PROJECT",
  storageBucket:     "YOUR_PROJECT.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId:             "YOUR_APP_ID"
};
```

Replace it with the config you copied from Firebase. Example:

```javascript
const firebaseConfig = {
  apiKey:            "AIzaSyD...",
  authDomain:        "stockmind-ai.firebaseapp.com",
  projectId:         "stockmind-ai",
  storageBucket:     "stockmind-ai.appspot.com",
  messagingSenderId: "123456789",
  appId:             "1:123456789:web:abc123"
};
```

---

## Step 5 — Done! Reload the app

Refresh `frontend/index.html`. Now:

| Feature | What Firestore does |
|---------|-------------------|
| **Watchlist** | Saves your tickers to `watchlist` collection |
| **Prediction History** | Every analysis auto-saves to `predictions` collection |
| **Persistence** | Data survives browser refresh & is visible in Firebase Console |

---

## What gets stored?

### `watchlist` collection
```json
{
  "ticker": "AAPL",
  "name": "Apple Inc.",
  "price": 189.25,
  "addedAt": <timestamp>
}
```

### `predictions` collection
```json
{
  "ticker": "AAPL",
  "signal": "BUY",
  "confidence": 74,
  "price": 189.25,
  "predicted": 192.10,
  "sentimentScore": 67,
  "savedAt": <timestamp>
}
```

---

## Resume Bullet Points You Can Use 🎯

```
• Integrated Google Firebase Firestore for real-time NoSQL cloud storage
  of user watchlists and ML prediction history across sessions

• Implemented serverless data persistence using Firebase SDK v10
  (compat mode) with structured Firestore collections and server-side timestamps

• Built full CRUD operations (create, read, delete) for a personalized
  stock watchlist synced to Firebase cloud database
```

---

## Viewing Your Data in Firebase

1. Go to https://console.firebase.google.com → Your project
2. Click **Firestore Database**
3. You'll see `watchlist` and `predictions` collections populate in real-time as you use the app!
