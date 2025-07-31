# 📦 Storage Module

This document explains how to set up and test the **Storage** component (PostgreSQL) of the SafeAir backend.

---

## 1. Environment Setup

1. **Copy** the example file:
  
   cp .env.example .env
Edit .env so it contains:
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secret
POSTGRES_DB=safeair_db
DATABASE_URL=postgresql+psycopg2://postgres:secret@127.0.0.1:5432/safeair_db
