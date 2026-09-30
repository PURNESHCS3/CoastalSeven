from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_user
from app.database import get_db
from app.models import Project, User

router = APIRouter(prefix="/api/uploads", tags=["Uploads"])

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
MAX_FILE_SIZE = 5 * 1024 * 1024


@router.post("/projects/{project_id}/image")
async def upload_project_image(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to update this project")

    extension = ALLOWED_TYPES.get(file.content_type)
    if not extension:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only JPG, PNG and WEBP images are allowed")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Image must be 5 MB or smaller")

    filename = f"project-{project_id}-{uuid4().hex}{extension}"
    destination = UPLOAD_DIR / filename
    destination.write_bytes(content)

    project.image_url = f"/uploads/{filename}"
    db.commit()
    db.refresh(project)

    return {
        "message": "Project image uploaded successfully",
        "image_url": project.image_url,
    }
