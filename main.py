import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, Response
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from database import db, create_document, get_documents
from bson.objectid import ObjectId
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = FastAPI(title="Construction Company API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Utilities
# -----------------------------

def slugify(text: str) -> str:
    return "-".join(
        "".join(c.lower() if c.isalnum() else "-" for c in text).split("-")
    )


def send_email(subject: str, html_body: str) -> bool:
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    sender = os.getenv("SMTP_FROM", user or "no-reply@example.com")
    recipient = os.getenv("SMTP_TO", os.getenv("SALES_EMAIL", "sales@example.com"))

    if not host or not recipient:
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipient
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(host, port) as server:
            server.starttls()
            if user and password:
                server.login(user, password)
            server.sendmail(sender, [recipient], msg.as_string())
        return True
    except Exception:
        return False

# -----------------------------
# Models
# -----------------------------

class LeadIn(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    project_location: Optional[str] = None
    project_type: Optional[str] = None
    budget_estimate: Optional[str] = None
    desired_start_date: Optional[str] = None
    message: Optional[str] = None
    newsletter_optin: bool = False

# -----------------------------
# Seed data helper
# -----------------------------

def ensure_seed():
    # Services
    if db and db["service"].count_documents({}) == 0:
        services = [
            {
                "name": "Design & Planning",
                "slug": "design-planning",
                "icon": "PenTool",
                "blurb": "Perencanaan arsitektur & struktur yang efisien dan aman.",
                "scope": ["Site survey", "Architectural design", "Structural design"],
            },
            {
                "name": "Construction",
                "slug": "construction",
                "icon": "Building",
                "blurb": "Konstruksi turnkey dari pondasi hingga finishing.",
                "scope": ["Earthwork", "Structure", "MEP", "Finishing"],
            },
            {
                "name": "Renovation",
                "slug": "renovation",
                "icon": "Hammer",
                "blurb": "Renovasi dan retrofit bangunan eksisting.",
                "scope": ["Assessment", "Reinforcement", "Upgrade"],
            },
            {
                "name": "Civil Works",
                "slug": "civil-works",
                "icon": "Road",
                "blurb": "Pekerjaan sipil: jalan, drainase, jembatan kecil.",
                "scope": ["Roadwork", "Drainage", "Culvert"],
            },
            {
                "name": "Project Management",
                "slug": "project-management",
                "icon": "ClipboardList",
                "blurb": "Manajemen proyek end-to-end on-time & on-budget.",
                "scope": ["Scheduling", "Cost control", "Quality & safety"],
            },
            {
                "name": "Maintenance",
                "slug": "maintenance",
                "icon": "Wrench",
                "blurb": "Perawatan berkala untuk aset Anda.",
                "scope": ["Inspection", "Preventive", "Corrective"],
            },
        ]
        db["service"].insert_many(services)

    # Projects
    if db and db["project"].count_documents({}) == 0:
        projects = [
            {
                "title": "Gudang Industri A",
                "slug": "gudang-industri-a",
                "category": "Industrial",
                "client": "PT Industri Makmur",
                "location": "Bekasi, Jawa Barat",
                "year": 2023,
                "summary": "Pembangunan gudang 8.000 m2 lengkap dengan MEP.",
                "cover_image": "https://images.unsplash.com/photo-1581091870634-6f9a6b4d9c55?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "title": "Perumahan Green Residence",
                "slug": "perumahan-green-residence",
                "category": "Residential",
                "client": "PT Properti Sejahtera",
                "location": "Tangerang, Banten",
                "year": 2022,
                "summary": "Cluster 50 unit tipe 60/120 dengan infrastruktur kawasan.",
                "cover_image": "https://images.unsplash.com/photo-1502005229762-cf1b2da7c52f?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "title": "Office Fit-out XYZ",
                "slug": "office-fitout-xyz",
                "category": "Commercial",
                "client": "PT Teknologi Nusantara",
                "location": "Jakarta Selatan",
                "year": 2024,
                "summary": "Renovasi kantor 1.200 m2 dengan konsep modern industrial.",
                "cover_image": "https://images.unsplash.com/photo-1507209696998-3c532be9b2b9?q=80&w=1200&auto=format&fit=crop",
            },
        ]
        db["project"].insert_many(projects)

    # Posts
    if db and db["post"].count_documents({}) == 0:
        posts = [
            {
                "title": "Tips Memilih Material Bangunan",
                "slug": "tips-memilih-material",
                "excerpt": "Panduan ringkas memilih material yang tepat untuk proyek Anda.",
                "content": "Konten artikel seputar material, kualitas, dan biaya.",
                "tags": ["material", "tips"],
            },
            {
                "title": "Keselamatan Kerja di Lokasi Proyek",
                "slug": "keselamatan-kerja-proyek",
                "excerpt": "Prinsip K3 yang wajib diterapkan.",
                "content": "Langkah-langkah praktis penerapan K3 di lapangan.",
                "tags": ["safety", "K3"],
            },
        ]
        db["post"].insert_many(posts)

# Ensure initial data
try:
    ensure_seed()
except Exception:
    pass

# -----------------------------
# Basic routes
# -----------------------------

@app.get("/")
def read_root():
    return {"message": "Construction Company API running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# -----------------------------
# Services
# -----------------------------

@app.get("/api/services")
def list_services():
    ensure_seed()
    return list(db["service"].find({}, {"_id": 0}))

@app.get("/api/services/{slug}")
def get_service(slug: str):
    doc = db["service"].find_one({"slug": slug}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Service not found")
    return doc

# -----------------------------
# Projects
# -----------------------------

@app.get("/api/projects")
def list_projects(category: Optional[str] = None):
    ensure_seed()
    q = {"category": category} if category else {}
    return list(db["project"].find(q, {"_id": 0}))

@app.get("/api/projects/{slug}")
def get_project(slug: str):
    doc = db["project"].find_one({"slug": slug}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Project not found")
    return doc

# -----------------------------
# Blog posts
# -----------------------------

@app.get("/api/posts")
def list_posts(tag: Optional[str] = None):
    ensure_seed()
    q = {"tags": tag} if tag else {}
    return list(db["post"].find(q, {"_id": 0}))

@app.get("/api/posts/{slug}")
def get_post(slug: str):
    doc = db["post"].find_one({"slug": slug}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Post not found")
    return doc

# -----------------------------
# Leads
# -----------------------------

@app.post("/api/leads")
def create_lead(lead: LeadIn):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    lead_dict = lead.model_dump()
    lead_id = create_document("lead", lead_dict)

    # Send email notification (best-effort)
    html = f"""
    <h3>New Quote Request</h3>
    <p><strong>Name:</strong> {lead.full_name}</p>
    <p><strong>Email:</strong> {lead.email}</p>
    <p><strong>Phone:</strong> {lead.phone or '-'} </p>
    <p><strong>Company:</strong> {lead.company or '-'} </p>
    <p><strong>Location:</strong> {lead.project_location or '-'} </p>
    <p><strong>Project Type:</strong> {lead.project_type or '-'} </p>
    <p><strong>Budget:</strong> {lead.budget_estimate or '-'} </p>
    <p><strong>Desired Start:</strong> {lead.desired_start_date or '-'} </p>
    <p><strong>Message:</strong><br/>{(lead.message or '').replace('\n', '<br/>')}</p>
    """
    send_email("New Lead - Request a Quote", html)

    return {"status": "ok", "id": lead_id}

# -----------------------------
# SEO: sitemap & robots
# -----------------------------

@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots():
    return """User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n"""

@app.get("/sitemap.xml")
def sitemap():
    base = os.getenv("FRONTEND_URL", "https://example.com")
    urls = [
        "", "about", "services", "projects", "blog", "contact"
    ]
    xml_urls = "".join([f"<url><loc>{base}/{u}</loc></url>" for u in urls])
    xml = f"""
    <?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
      {xml_urls}
    </urlset>
    """
    return Response(content=xml.strip(), media_type="application/xml")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
