"""AutoSite AI Pro — FastAPI backend."""
from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Any, Dict

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import Response
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, ConfigDict, Field
from starlette.middleware.cors import CORSMiddleware

import ai_service
from site_generator import compute_seo_score, make_zip, render_site_html

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

app = FastAPI(title="AutoSite AI Pro")
api = APIRouter(prefix="/api")

logger = logging.getLogger("autosite")
logging.basicConfig(level=logging.INFO)


# ---------- Models ----------
class ProjectCreate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    business_name: str
    sector: str
    city: str
    address: Optional[str] = ""
    phone: Optional[str] = ""
    email: Optional[str] = ""
    whatsapp: Optional[str] = ""
    social: Optional[Dict[str, str]] = Field(default_factory=dict)
    objective: Optional[str] = "contacter"
    style: Optional[str] = "moderne"
    primary_color: Optional[str] = "#FF4500"
    secondary_color: Optional[str] = "#0A0A0A"
    tone: Optional[str] = "pro"
    services: Optional[str] = ""
    description: Optional[str] = ""
    audience: Optional[str] = ""
    main_button: Optional[str] = "Contactez-nous"
    sections: Optional[List[str]] = Field(default_factory=list)
    design_level: Optional[str] = "premium"
    template: Optional[str] = ""


class Project(ProjectCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    content: Optional[Dict[str, Any]] = None
    versions: Optional[List[Dict[str, Any]]] = Field(default_factory=list)


class ProjectUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    business_name: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    content: Optional[Dict[str, Any]] = None


# ---------- Helpers ----------
async def _get_project(project_id: str) -> Dict[str, Any]:
    doc = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Project not found")
    return doc


# ---------- Routes ----------
@api.get("/")
async def root():
    return {"service": "AutoSite AI Pro", "status": "ok"}


@api.get("/sectors")
async def sectors():
    return [
        {"id": "restaurant", "name": "Restaurant / Pizzeria", "icon": "utensils"},
        {"id": "garage", "name": "Garage / Auto", "icon": "wrench"},
        {"id": "coiffeur", "name": "Coiffeur / Barber", "icon": "scissors"},
        {"id": "construction", "name": "Construction", "icon": "hard-hat"},
        {"id": "nettoyage", "name": "Nettoyage", "icon": "sparkles"},
        {"id": "immobilier", "name": "Immobilier", "icon": "home"},
        {"id": "avocat", "name": "Avocat / Consultant", "icon": "scale"},
        {"id": "medecin", "name": "Médecin / Santé", "icon": "stethoscope"},
        {"id": "ecommerce", "name": "E-commerce", "icon": "shopping-bag"},
        {"id": "startup", "name": "Startup / SaaS", "icon": "rocket"},
        {"id": "coach", "name": "Coach", "icon": "target"},
        {"id": "photographe", "name": "Photographe", "icon": "camera"},
        {"id": "gym", "name": "Salle de sport", "icon": "dumbbell"},
        {"id": "esthetique", "name": "Esthétique / Spa", "icon": "flower-2"},
        {"id": "livraison", "name": "Livraison", "icon": "truck"},
    ]


@api.post("/projects", response_model=Project)
async def create_project(payload: ProjectCreate):
    proj = Project(**payload.model_dump())
    doc = proj.model_dump()
    await db.projects.insert_one(doc.copy())
    return proj


@api.get("/projects", response_model=List[Project])
async def list_projects():
    cursor = db.projects.find({}, {"_id": 0}).sort("created_at", -1)
    return await cursor.to_list(500)


@api.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    return await _get_project(project_id)


@api.patch("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, payload: ProjectUpdate):
    existing = await _get_project(project_id)
    updates = {k: v for k, v in payload.model_dump(exclude_none=True).items()}
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.projects.update_one({"id": project_id}, {"$set": updates})
    existing.update(updates)
    return existing


@api.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    res = await db.projects.delete_one({"id": project_id})
    if res.deleted_count == 0:
        raise HTTPException(404, "Project not found")
    return {"deleted": True}


@api.post("/projects/{project_id}/duplicate", response_model=Project)
async def duplicate_project(project_id: str):
    orig = await _get_project(project_id)
    copy = {**orig}
    copy["id"] = str(uuid.uuid4())
    copy["business_name"] = f"{orig.get('business_name','')} (copie)"
    copy["created_at"] = datetime.now(timezone.utc).isoformat()
    copy["updated_at"] = copy["created_at"]
    await db.projects.insert_one(copy.copy())
    return copy


@api.post("/projects/{project_id}/generate", response_model=Project)
async def generate_project_content(project_id: str):
    proj = await _get_project(project_id)
    try:
        content = await ai_service.generate_site_content(proj)
    except Exception as e:
        logger.exception("Gemini generation failed")
        raise HTTPException(500, f"Generation failed: {e}")

    now = datetime.now(timezone.utc).isoformat()
    versions = proj.get("versions") or []
    if proj.get("content"):
        versions.append({"at": proj.get("updated_at", now), "content": proj["content"]})
        versions = versions[-10:]

    await db.projects.update_one(
        {"id": project_id},
        {"$set": {"content": content, "versions": versions, "updated_at": now}},
    )
    proj["content"] = content
    proj["versions"] = versions
    proj["updated_at"] = now
    return proj


@api.get("/projects/{project_id}/seo-score")
async def seo_score(project_id: str):
    proj = await _get_project(project_id)
    if not proj.get("content"):
        raise HTTPException(400, "Project not generated yet")
    return compute_seo_score(proj, proj["content"])


@api.get("/projects/{project_id}/preview", response_class=Response)
async def preview(project_id: str):
    proj = await _get_project(project_id)
    if not proj.get("content"):
        return Response(
            "<!doctype html><html><body style='background:#0a0a0a;color:#fff;font-family:sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0'><div style='text-align:center'><div style='font-size:14px;letter-spacing:4px;text-transform:uppercase;color:#FF4500'>En attente de génération</div><div style='margin-top:12px;color:#aaa'>Cliquez sur « Générer le site » pour lancer l'IA.</div></div></body></html>",
            media_type="text/html",
        )
    html = render_site_html(proj, proj["content"])
    return Response(html, media_type="text/html")


@api.get("/projects/{project_id}/export")
async def export_zip(project_id: str):
    proj = await _get_project(project_id)
    if not proj.get("content"):
        raise HTTPException(400, "Project not generated yet")
    data = make_zip(proj, proj["content"])
    filename = (proj.get("business_name") or "site").replace(" ", "-").lower() + ".zip"
    return Response(
        data,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


app.include_router(api)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
