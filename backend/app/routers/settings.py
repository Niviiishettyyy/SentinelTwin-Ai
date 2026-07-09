from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, auth

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("/preferences")
def get_preferences(db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)):
    prefs = db.query(models.SettingsPreference).filter(models.SettingsPreference.user_id == current_user.id).all()
    return {p.key: p.value for p in prefs}


@router.put("/preferences/{key}")
def set_preference(key: str, value: str, db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)):
    pref = (
        db.query(models.SettingsPreference)
        .filter(models.SettingsPreference.user_id == current_user.id, models.SettingsPreference.key == key)
        .first()
    )
    if pref:
        pref.value = value
    else:
        pref = models.SettingsPreference(user_id=current_user.id, key=key, value=value)
        db.add(pref)
    db.commit()
    return {"key": key, "value": value}
