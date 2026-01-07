# Smart Cattle Collision Prevention System

An AI-based road safety system that predicts and prevents cattle-related road accidents using computer vision and real-time risk analysis.

---

## Problem
Stray cattle on Indian highways and rural roads cause frequent accidents, especially at night. Existing solutions such as signboards and reflectors are static and ineffective, offering no real-time risk awareness.

---

## Solution
This system uses **computer vision models** to process roadside camera or dashcam video feeds and detect cattle and vehicles in real time. Using visual cues such as object location, size, and movement, the system estimates collision risk based on contextual factors and generates preventive warnings before accidents occur.

Significant risk events are logged and monitored through a live dashboard for authorities.

---

## Key Features
- Real-time cattle and vehicle detection
- Day and night adaptive processing
- Explainable, rule-based risk scoring
- Preventive warning generation
- Smart event logging (no data spam)
- Live monitoring dashboard

---

## Tech Stack
- Computer Vision: Python, OpenCV, YOLO
- Backend: Google Firebase (Firestore)
- Dashboard: HTML, CSS, JavaScript

---

## Status
Hackathon MVP with working detection, risk evaluation, warning logic, and real-time dashboard updates using simulated video feeds.

---

## Team
Developed by a team of four for a hackathon focused on real-world road safety challenges.
