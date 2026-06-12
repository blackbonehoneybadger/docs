"""Daily report endpoints: text, PDF, image."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from sqlalchemy.orm import Session

from app.api.deps import get_or_create_default_user
from app.database import get_db
from app.reports.daily_report import build_daily_bundle

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/morning", response_class=PlainTextResponse)
def morning_report(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    return build_daily_bundle(db, user, greeting="Доброе утро").text


@router.get("/evening", response_class=PlainTextResponse)
def evening_report(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    return build_daily_bundle(db, user, greeting="Добрый вечер").text


@router.get("/daily/pdf")
def daily_pdf(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    bundle = build_daily_bundle(db, user)
    if not bundle.pdf_path.exists():
        raise HTTPException(status_code=500, detail="PDF generation failed")
    return FileResponse(bundle.pdf_path, media_type="application/pdf",
                        filename=bundle.pdf_path.name)


@router.get("/daily/image")
def daily_image(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    bundle = build_daily_bundle(db, user)
    if not bundle.image_path.exists():
        raise HTTPException(status_code=500, detail="Image generation failed")
    return FileResponse(bundle.image_path, media_type="image/png",
                        filename=bundle.image_path.name)
