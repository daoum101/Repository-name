"""AutoSite AI Pro - Backend API tests."""
import os
import io
import zipfile
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://ai-agency-sites.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"

# Generation can be slow (30-90s)
GEN_TIMEOUT = 180


@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="module")
def created_project(session):
    payload = {
        "business_name": "TEST_AutoSite Pizzeria",
        "sector": "restaurant",
        "city": "Lyon",
        "address": "12 rue de Lyon",
        "phone": "+33611223344",
        "email": "test@example.com",
        "whatsapp": "+33611223344",
        "objective": "contacter",
        "style": "moderne",
        "primary_color": "#FF4500",
        "secondary_color": "#0A0A0A",
        "tone": "pro",
        "services": "Pizzas artisanales, livraison rapide, menus du jour",
        "description": "Restaurant pizzeria familial",
        "audience": "Familles, étudiants, professionnels",
        "main_button": "Réserver une table",
        "design_level": "premium",
    }
    r = session.post(f"{API}/projects", json=payload, timeout=30)
    assert r.status_code == 200, f"create failed: {r.status_code} {r.text}"
    data = r.json()
    assert data["business_name"] == payload["business_name"]
    assert data["sector"] == "restaurant"
    assert "id" in data and isinstance(data["id"], str)
    yield data
    # teardown
    session.delete(f"{API}/projects/{data['id']}", timeout=15)


# ---------- Health ----------
class TestHealth:
    def test_root(self, session):
        r = session.get(f"{API}/", timeout=15)
        assert r.status_code == 200
        d = r.json()
        assert d.get("status") == "ok"
        assert d.get("service")


class TestSectors:
    def test_sectors_15(self, session):
        r = session.get(f"{API}/sectors", timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) == 15
        ids = [s["id"] for s in data]
        for required in ["restaurant", "garage", "coiffeur", "ecommerce", "startup"]:
            assert required in ids
        for s in data:
            assert "name" in s and "icon" in s


# ---------- Project CRUD ----------
class TestProjectCRUD:
    def test_list_projects_no_id_leak(self, session, created_project):
        r = session.get(f"{API}/projects", timeout=15)
        assert r.status_code == 200
        items = r.json()
        assert isinstance(items, list)
        assert any(p["id"] == created_project["id"] for p in items)
        for p in items:
            assert "_id" not in p

    def test_get_single_project(self, session, created_project):
        r = session.get(f"{API}/projects/{created_project['id']}", timeout=15)
        assert r.status_code == 200
        d = r.json()
        assert d["id"] == created_project["id"]
        assert d["business_name"] == created_project["business_name"]
        assert "_id" not in d

    def test_get_unknown_404(self, session):
        r = session.get(f"{API}/projects/does-not-exist", timeout=15)
        assert r.status_code == 404

    def test_patch_project(self, session, created_project):
        pid = created_project["id"]
        r = session.patch(
            f"{API}/projects/{pid}",
            json={"business_name": "TEST_Updated Name", "primary_color": "#00AAFF", "secondary_color": "#111111"},
            timeout=15,
        )
        assert r.status_code == 200
        d = r.json()
        assert d["business_name"] == "TEST_Updated Name"
        assert d["primary_color"] == "#00AAFF"
        assert d["secondary_color"] == "#111111"
        # verify persistence
        g = session.get(f"{API}/projects/{pid}", timeout=15).json()
        assert g["business_name"] == "TEST_Updated Name"
        assert g["primary_color"] == "#00AAFF"

    def test_duplicate(self, session, created_project):
        pid = created_project["id"]
        r = session.post(f"{API}/projects/{pid}/duplicate", timeout=15)
        assert r.status_code == 200
        d = r.json()
        assert d["id"] != pid
        assert "(copie)" in d["business_name"]
        # cleanup duplicate
        session.delete(f"{API}/projects/{d['id']}", timeout=15)

    def test_delete_project_isolated(self, session):
        # standalone create + delete to verify removal
        r = session.post(
            f"{API}/projects",
            json={"business_name": "TEST_ToDelete", "sector": "garage", "city": "Paris"},
            timeout=15,
        )
        pid = r.json()["id"]
        d = session.delete(f"{API}/projects/{pid}", timeout=15)
        assert d.status_code == 200
        g = session.get(f"{API}/projects/{pid}", timeout=15)
        assert g.status_code == 404


# ---------- AI Generation (slow) ----------
class TestGeneration:
    def test_generate_content(self, session, created_project):
        pid = created_project["id"]
        r = session.post(f"{API}/projects/{pid}/generate", timeout=GEN_TIMEOUT)
        assert r.status_code == 200, f"generate failed: {r.status_code} {r.text[:500]}"
        d = r.json()
        assert d.get("content") is not None
        c = d["content"]
        for key in ["meta", "hero", "about", "services", "features", "testimonials", "faq", "cta", "contact", "local_business"]:
            assert key in c, f"missing section: {key}"
        # meta sub-checks
        assert c["meta"].get("title")
        assert c["meta"].get("description")
        assert isinstance(c["meta"].get("keywords"), list) and len(c["meta"]["keywords"]) >= 5
        # hero
        assert c["hero"].get("headline")
        # services
        assert isinstance(c["services"].get("items"), list) and len(c["services"]["items"]) >= 3
        # faq
        assert isinstance(c["faq"].get("items"), list) and len(c["faq"]["items"]) >= 3

    def test_seo_score(self, session, created_project):
        pid = created_project["id"]
        r = session.get(f"{API}/projects/{pid}/seo-score", timeout=30)
        assert r.status_code == 200
        d = r.json()
        assert "score" in d and 0 <= d["score"] <= 100
        assert "checks" in d
        assert len(d["checks"]) == 12
        for c in d["checks"]:
            assert "key" in c and "label" in c and "passed" in c

    def test_preview(self, session, created_project):
        pid = created_project["id"]
        r = session.get(f"{API}/projects/{pid}/preview", timeout=30)
        assert r.status_code == 200
        assert "text/html" in r.headers.get("content-type", "")
        html = r.text
        assert len(html) > 5000, f"preview HTML too small: {len(html)} bytes"
        assert "<html" in html.lower()
        assert "schema.org" in html
        assert "LocalBusiness" in html

    def test_export_zip(self, session, created_project):
        pid = created_project["id"]
        r = session.get(f"{API}/projects/{pid}/export", timeout=30)
        assert r.status_code == 200
        assert "application/zip" in r.headers.get("content-type", "")
        z = zipfile.ZipFile(io.BytesIO(r.content))
        names = z.namelist()
        for required in ["index.html", "robots.txt", "sitemap.xml", "README.md", "content.json"]:
            assert required in names, f"missing in zip: {required}"


# ---------- Edge cases ----------
class TestEdge:
    def test_seo_score_before_generation(self, session):
        r = session.post(
            f"{API}/projects",
            json={"business_name": "TEST_NoGen", "sector": "garage", "city": "Paris"},
            timeout=15,
        )
        pid = r.json()["id"]
        s = session.get(f"{API}/projects/{pid}/seo-score", timeout=15)
        assert s.status_code == 400
        e = session.get(f"{API}/projects/{pid}/export", timeout=15)
        assert e.status_code == 400
        # preview returns waiting page
        p = session.get(f"{API}/projects/{pid}/preview", timeout=15)
        assert p.status_code == 200
        assert "attente" in p.text.lower() or "génération" in p.text.lower()
        session.delete(f"{API}/projects/{pid}", timeout=15)
