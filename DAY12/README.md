# DAY12 - React UI, Forms and Validation

Day 12 extends the Day 11 Task Management application in an isolated project.

## Frontend
- Tailwind CSS v4
- Shadcn-style reusable UI components
- React Hook Form
- Zod validation
- Multi-step project form
- Dynamic project tags
- React Dropzone image upload and preview
- Accessible labels, errors and keyboard interactions
- Light/dark theme toggle

## Backend additions
- Project image upload endpoint
- 5 MB image validation
- JPG/PNG/WEBP validation
- Static image serving
- Project `image_url` field with Alembic migration

## Run

Frontend:
```bash
cd frontend
npm install
npm run dev
```

Backend:
```bash
cd task-management-api
alembic upgrade head
uvicorn app.main:app --reload
```
