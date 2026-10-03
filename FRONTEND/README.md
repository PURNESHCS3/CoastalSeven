# Day 13 – E-Commerce Frontend

React + Vite + Tailwind CSS + shadcn/ui-style components + Axios + React Router.

## 1. Start the FastAPI backend

From the `DAY10` folder:

```powershell
.\.venv\Scripts\activate
uvicorn app.main:app --reload
```

Backend: `http://127.0.0.1:8000`

## 2. Start the frontend

Open another terminal:

```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```

Frontend: `http://localhost:5173`

If PowerShell does not accept `copy`, use:

```powershell
Copy-Item .env.example .env
```

## Implemented Day 13 features

- Vite React project
- Tailwind CSS
- Reusable shadcn/ui-style Button, Input and Card components
- Product listing from `GET /api/products/`
- Search
- Stock filtering
- Price/name sorting
- Product details from `GET /api/products/{id}`
- Register from `POST /api/auth/register`
- Login from `POST /api/auth/login`
- JWT access-token interceptor
- Refresh-token interceptor using `POST /api/auth/refresh`
- Protected `/account` route
- Current user from `GET /api/auth/me`
- FastAPI CORS configuration
- Product image URL support through FastAPI static files

## Routes

| Frontend route | Purpose |
|---|---|
| `/` | Product listing |
| `/products/:id` | Product details |
| `/login` | Login |
| `/register` | Register |
| `/account` | Protected account page |

## Important

The backend must be running before opening the frontend. If the browser shows a CORS error, verify that `app/main.py` contains the CORS middleware added for `http://localhost:5173`.
