# 🌤️ Is It Safe to Go Outside?

A simple and intuitive web app that combines **weather** and **air quality** data to answer a single question:  
**"Is it safe to go outside?"**

---

## 🚨 The Problem

- Weather and air quality are usually displayed separately  
- Difficult to evaluate real health risks—especially for people with respiratory conditions  
- Scattered sources mean slower decisions  

---

## ✅ The Solution

An all-in-one interface that provides:

- A **Respiratory Risk Index** (green / yellow / red)
- A **map with markers** showing locations and tooltip details
- Instant feedback based on combined **weather and air quality** data

---

## 🛠️ How It Works

1. User searches for a location  
2. App fetches weather & air quality data  
3. Computes a **risk score**  
4. Displays result as a colored marker on a map

---

## ⚠️ Limitations

- **Mapbox Search Box API** works best in the US, Canada, and Europe  
- **OpenWeather APIs** are updated approximately every 2 hours  

---

## 💻 Tech Stack

**Frontend:**  
- Streamlit – UI with search bar, map, and interactive markers

**Backend:**  
- FastAPI – Fetches APIs, computes risk scores, and caches results

**Storage:**  
- PostgreSQL – Stores raw and computed data

**DevOps:**  
- Docker & Kubernetes – Containerization and deployment with health checks
