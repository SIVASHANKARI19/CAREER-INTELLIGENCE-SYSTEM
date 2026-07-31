# Architecture

Frontend
- React + Vite
- TailwindCSS
- React Query
- Recharts

Backend
- FastAPI
- SQLAlchemy
- MySQL
- JWT Authentication

AI
- spaCy
- PyMuPDF
- Sentence Transformers
- XGBoost
- SHAP
- Gemini API

Folder Structure

backend/
    api/
    models/
    schemas/
    services/
    ai/
    utils/

Rules

- Architecture is frozen.
- Never rename APIs.
- Never rename models.
- Never redesign database.
- Never create duplicate services.
- Only replace mock implementations.

Backend Skeleton

✔ Routers exist

✔ Models exist

✔ Schemas exist

✔ Database exists

Only AI services are mocked.