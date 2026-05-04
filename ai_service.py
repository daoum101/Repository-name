"""Ultra-premium Gemini generation service for AutoSite AI Pro.

Indépendant d'Emergent. Génère un contenu JSON riche, stable et prêt à rendre
avec site_generator.py.
Required env var: GEMINI_API_KEY
Optional env var: GEMINI_MODEL, default: gemini-1.5-flash
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
import google.generativeai as genai

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
Tu es un directeur artistique senior + copywriter conversion + expert SEO local.
Ton niveau attendu : agence premium type Framer/Webflow/Relume, pas site générique.
Tu dois générer le contenu d'un site commercial haut de gamme, crédible, vendable.

RÈGLES ABSOLUES :
- Réponds UNIQUEMENT en JSON valide. Aucun markdown. Aucun texte avant/après.
- Langue : français naturel, sauf si le brief est clairement dans une autre langue.
- Zéro Lorem ipsum, zéro placeholder, zéro phrase vague du type "solutions adaptées" sans preuve.
- Texte premium mais humain : phrases courtes, concrètes, commerciales.
- Intègre naturellement la ville et le secteur pour le SEO local.
- Les avis clients doivent être réalistes, pas exagérés.
- Le ton doit correspondre au business : restaurant chaleureux, avocat sérieux, garage fiable, beauté élégant, etc.
- Les CTA doivent donner envie de passer à l'action.
"""

SCHEMA_HINT = """
Retourne exactement ce JSON, avec tous les champs remplis :
{
  "meta": {
    "title": "Titre SEO 50-65 caractères avec nom + ville",
    "description": "Meta description 135-165 caractères avec service principal + ville + appel à l'action",
    "keywords": ["8 à 14 mots-clés locaux et sectoriels"],
    "og_title": "Titre partage réseaux sociaux",
    "og_description": "Description partage réseaux sociaux"
  },
  "design": {
    "mood": "3 mots décrivant l'ambiance visuelle",
    "visual_direction": "Direction artistique courte et précise",
    "accent_words": ["mot premium 1", "mot premium 2", "mot premium 3"],
    "microcopy": "Petite phrase de confiance à afficher"
  },
  "hero": {
    "eyebrow": "Label court en majuscules",
    "headline": "Titre puissant 5-9 mots, avec ville si naturel",
    "subheadline": "Promesse claire 18-28 mots, concrète et élégante",
    "cta_primary": "CTA principal",
    "cta_secondary": "CTA secondaire"
  },
  "trust_bar": {
    "items": [
      {"label": "Preuve courte", "value": "Valeur courte"},
      {"label": "Preuve courte", "value": "Valeur courte"},
      {"label": "Preuve courte", "value": "Valeur courte"},
      {"label": "Preuve courte", "value": "Valeur courte"}
    ]
  },
  "about": {
    "title": "Titre À propos premium",
    "paragraph": "2-3 phrases concrètes sur l'activité, la qualité, l'expérience client et la ville.",
    "highlights": [
      {"label": "Label", "value": "Valeur"},
      {"label": "Label", "value": "Valeur"},
      {"label": "Label", "value": "Valeur"}
    ]
  },
  "services": {
    "title": "Titre services",
    "subtitle": "Sous-titre clair et commercial",
    "items": [
      {"name": "Service", "description": "Description 2 phrases, précise et vendable", "icon": "utensils"},
      {"name": "Service", "description": "Description 2 phrases, précise et vendable", "icon": "star"},
      {"name": "Service", "description": "Description 2 phrases, précise et vendable", "icon": "clock"},
      {"name": "Service", "description": "Description 2 phrases, précise et vendable", "icon": "map-pin"},
      {"name": "Service", "description": "Description 2 phrases, précise et vendable", "icon": "sparkles"},
      {"name": "Service", "description": "Description 2 phrases, précise et vendable", "icon": "phone"}
    ]
  },
  "process": {
    "title": "Titre déroulement / expérience",
    "items": [
      {"step": "01", "title": "Étape", "description": "Description courte"},
      {"step": "02", "title": "Étape", "description": "Description courte"},
      {"step": "03", "title": "Étape", "description": "Description courte"}
    ]
  },
  "features": {
    "title": "Pourquoi choisir ce business",
    "items": [
      {"title": "Avantage", "description": "1-2 phrases concrètes"},
      {"title": "Avantage", "description": "1-2 phrases concrètes"},
      {"title": "Avantage", "description": "1-2 phrases concrètes"},
      {"title": "Avantage", "description": "1-2 phrases concrètes"}
    ]
  },
  "testimonials": {
    "title": "Titre avis clients",
    "items": [
      {"name": "Prénom Nom réaliste", "role": "Client, Ville", "quote": "Avis réaliste 2 phrases", "rating": 5},
      {"name": "Prénom Nom réaliste", "role": "Client, Ville", "quote": "Avis réaliste 2 phrases", "rating": 5},
      {"name": "Prénom Nom réaliste", "role": "Client, Ville", "quote": "Avis réaliste 2 phrases", "rating": 5}
    ]
  },
  "faq": {
    "title": "Titre FAQ",
    "items": [
      {"question": "Question client fréquente", "answer": "Réponse claire et utile"},
      {"question": "Question client fréquente", "answer": "Réponse claire et utile"},
      {"question": "Question client fréquente", "answer": "Réponse claire et utile"},
      {"question": "Question client fréquente", "answer": "Réponse claire et utile"},
      {"question": "Question client fréquente", "answer": "Réponse claire et utile"}
    ]
  },
  "cta": {
    "title": "Titre final très vendeur",
    "subtitle": "Phrase courte qui pousse à contacter",
    "button": "Texte bouton"
  },
  "contact": {
    "title": "Titre contact",
    "subtitle": "Phrase rassurante avant formulaire"
  },
  "local_business": {
    "areas_served": ["Ville", "Ville proche 1", "Ville proche 2", "Ville proche 3"],
    "opening_hours": [
      {"days": "Lun-Ven", "hours": "09:00 - 18:00"},
      {"days": "Sam", "hours": "10:00 - 17:00"},
      {"days": "Dim", "hours": "Fermé"}
    ]
  }
}
"""

ICON_ALLOWLIST = {
    "utensils", "star", "clock", "map-pin", "sparkles", "phone", "truck", "home",
    "wrench", "scissors", "camera", "dumbbell", "shopping-bag", "heart", "shield",
    "calendar", "message-circle", "chef-hat", "car", "building", "flower-2", "rocket"
}


def _extract_json(text: str) -> Dict[str, Any]:
    """Extract and parse the first JSON object returned by Gemini."""
    if not text:
        raise ValueError("Gemini returned an empty response")
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    first = cleaned.find("{")
    last = cleaned.rfind("}")
    if first == -1 or last == -1 or last <= first:
        logger.error("Gemini did not return JSON. Raw response: %s", cleaned[:1500])
        raise ValueError("Gemini did not return JSON")
    payload = cleaned[first:last + 1]
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        logger.error("Gemini JSON decode error: %s\n--- raw ---\n%s", exc, cleaned[:2000])
        raise


def _coerce_list(value: Any, fallback: List[Any]) -> List[Any]:
    return value if isinstance(value, list) and value else fallback


def _sanitize_content(content: Dict[str, Any], project: Dict[str, Any]) -> Dict[str, Any]:
    """Make model output robust even if Gemini omits small parts."""
    biz = project.get("business_name") or "Votre entreprise"
    city = project.get("city") or "votre ville"
    sector = project.get("sector") or "service local"

    content.setdefault("meta", {})
    content["meta"].setdefault("title", f"{biz} — {sector} à {city}")
    content["meta"].setdefault("description", f"Découvrez {biz}, votre adresse de confiance à {city}. Service soigné, accueil professionnel et prise de contact rapide.")
    content["meta"]["keywords"] = _coerce_list(content["meta"].get("keywords"), [biz, sector, city, f"{sector} {city}", "service local", "contact", "qualité", "professionnel"])
    content["meta"].setdefault("og_title", content["meta"]["title"])
    content["meta"].setdefault("og_description", content["meta"]["description"])

    content.setdefault("design", {})
    content["design"].setdefault("mood", "premium, moderne, chaleureux")
    content["design"].setdefault("visual_direction", "Design sombre haut de gamme, typographie forte, sections respirantes et appels à l'action visibles.")
    content["design"]["accent_words"] = _coerce_list(content["design"].get("accent_words"), ["Qualité", "Confiance", "Savoir-faire"])
    content["design"].setdefault("microcopy", "Réponse rapide — service professionnel — expérience soignée")

    content.setdefault("hero", {})
    content["hero"].setdefault("eyebrow", f"{sector} à {city}".upper())
    content["hero"].setdefault("headline", f"{biz}, l'adresse à retenir à {city}")
    content["hero"].setdefault("subheadline", "Une expérience soignée, des prestations claires et un service pensé pour vous faire gagner du temps.")
    content["hero"].setdefault("cta_primary", project.get("main_button") or "Contactez-nous")
    content["hero"].setdefault("cta_secondary", "Découvrir")

    content.setdefault("trust_bar", {})
    content["trust_bar"]["items"] = _coerce_list(content["trust_bar"].get("items"), [
        {"label": "Service", "value": "Soigné"},
        {"label": "Contact", "value": "Rapide"},
        {"label": "Zone", "value": city},
        {"label": "Qualité", "value": "Premium"},
    ])[:4]

    content.setdefault("about", {})
    content["about"].setdefault("title", f"Une expérience locale, pensée avec exigence")
    content["about"].setdefault("paragraph", f"Basé à {city}, {biz} accompagne ses clients avec un service clair, attentif et professionnel. Chaque détail est pensé pour offrir une expérience agréable et fiable.")
    content["about"]["highlights"] = _coerce_list(content["about"].get("highlights"), [
        {"label": "Approche", "value": "Sur mesure"},
        {"label": "Accueil", "value": "Rapide"},
        {"label": "Ville", "value": city},
    ])[:3]

    content.setdefault("services", {})
    content["services"].setdefault("title", "Des prestations claires et professionnelles")
    content["services"].setdefault("subtitle", "Tout ce qu’il faut pour répondre à vos besoins avec sérieux et efficacité.")
    services = content["services"].get("items") or []
    if not isinstance(services, list) or len(services) < 4:
        raw = project.get("services") or "Service principal, accompagnement, conseil, contact"
        names = [x.strip() for x in re.split(r"[\n,;]+", raw) if x.strip()][:6]
        services = [{"name": n, "description": f"Une prestation pensée pour garantir un résultat propre, clair et adapté à vos besoins à {city}.", "icon": "star"} for n in names]
    for it in services:
        if it.get("icon") not in ICON_ALLOWLIST:
            it["icon"] = "star"
    content["services"]["items"] = services[:6]

    content.setdefault("process", {})
    content["process"].setdefault("title", "Une expérience simple, claire et efficace")
    content["process"]["items"] = _coerce_list(content["process"].get("items"), [
        {"step": "01", "title": "Contact", "description": "Vous nous expliquez votre besoin en quelques minutes."},
        {"step": "02", "title": "Conseil", "description": "Nous vous orientons vers la meilleure solution."},
        {"step": "03", "title": "Service", "description": "Nous réalisons la prestation avec sérieux et attention."},
    ])[:3]

    content.setdefault("features", {})
    content["features"].setdefault("title", f"Pourquoi choisir {biz} ?")
    content["features"]["items"] = _coerce_list(content["features"].get("items"), [
        {"title": "Service fiable", "description": "Une approche claire, sans surprise, avec une vraie attention portée au détail."},
        {"title": "Proximité locale", "description": f"Une présence à {city} et une connaissance des attentes des clients de la région."},
        {"title": "Contact rapide", "description": "Une réponse simple et efficace pour organiser votre demande sans perdre de temps."},
        {"title": "Qualité constante", "description": "Chaque prestation vise un résultat propre, crédible et professionnel."},
    ])[:4]

    content.setdefault("testimonials", {})
    content["testimonials"].setdefault("title", "Ce que nos clients apprécient")
    content["testimonials"]["items"] = _coerce_list(content["testimonials"].get("items"), [
        {"name": "Nadia Lambert", "role": f"Cliente, {city}", "quote": "Service très sérieux et accueil impeccable. On sent une vraie attention portée au client.", "rating": 5},
        {"name": "Julien Martin", "role": f"Client, {city}", "quote": "Expérience fluide, claire et professionnelle. Je recommande sans hésiter.", "rating": 5},
        {"name": "Sophie Bernard", "role": f"Cliente, {city}", "quote": "Très bon contact et résultat à la hauteur. Une adresse fiable dans la région.", "rating": 5},
    ])[:3]

    content.setdefault("faq", {})
    content["faq"].setdefault("title", "Questions fréquentes")
    content["faq"]["items"] = _coerce_list(content["faq"].get("items"), [
        {"question": "Comment prendre contact ?", "answer": "Vous pouvez appeler, envoyer un message ou utiliser le formulaire de contact."},
        {"question": "Intervenez-vous autour de la ville ?", "answer": f"Oui, nous desservons {city} et plusieurs communes proches."},
        {"question": "Quels sont les délais ?", "answer": "Les délais dépendent de la demande, mais nous répondons rapidement pour organiser la suite."},
        {"question": "Puis-je demander un conseil avant de réserver ?", "answer": "Oui, nous pouvons vous orienter vers la solution la plus adaptée."},
        {"question": "Le contact est-il sans engagement ?", "answer": "Oui, une première prise de contact ne vous engage à rien."},
    ])[:5]

    content.setdefault("cta", {})
    content["cta"].setdefault("title", "Envie d’un service clair et professionnel ?")
    content["cta"].setdefault("subtitle", "Contactez-nous aujourd’hui et recevez une réponse rapide.")
    content["cta"].setdefault("button", project.get("main_button") or "Prendre contact")

    content.setdefault("contact", {})
    content["contact"].setdefault("title", f"Contactez {biz}")
    content["contact"].setdefault("subtitle", "Une question, une réservation ou une demande précise ? Nous vous répondons rapidement.")

    content.setdefault("local_business", {})
    content["local_business"]["areas_served"] = _coerce_list(content["local_business"].get("areas_served"), [city])[:4]
    content["local_business"]["opening_hours"] = _coerce_list(content["local_business"].get("opening_hours"), [
        {"days": "Lun-Ven", "hours": "09:00 - 18:00"},
        {"days": "Sam", "hours": "10:00 - 17:00"},
        {"days": "Dim", "hours": "Fermé"},
    ])[:4]
    return content


def _build_brief(project: Dict[str, Any]) -> str:
    services = project.get("services") or ""
    return f"""
{SYSTEM_PROMPT}

BRIEF BUSINESS :
- Nom : {project.get('business_name')}
- Secteur : {project.get('sector')}
- Ville : {project.get('city')}
- Adresse : {project.get('address') or 'Non précisée'}
- Téléphone : {project.get('phone') or 'Non précisé'}
- Email : {project.get('email') or 'Non précisé'}
- WhatsApp : {project.get('whatsapp') or 'Non précisé'}
- Objectif du site : {project.get('objective') or 'obtenir des contacts'}
- Style demandé : {project.get('style') or 'premium moderne'}
- Niveau design : {project.get('design_level') or 'premium'}
- Ton demandé : {project.get('tone') or 'professionnel'}
- Audience cible : {project.get('audience') or 'clients locaux'}
- CTA principal souhaité : {project.get('main_button') or 'Contactez-nous'}
- Services/produits : {services}
- Description complète : {project.get('description') or ''}

MISSION :
Crée un contenu qui donne l'impression d'un site d'agence vendu cher : clair, élégant, rassurant, commercial.
Le rendu doit être meilleur qu'un site IA générique : plus précis, plus humain, plus local, plus premium.
Si le business est une pizzeria/restaurant, parle de goût, générosité, feu de bois, fraîcheur, livraison, convivialité.
Si le business est beauté/coiffeur, parle d'élégance, conseil, soin, résultat.
Si le business est garage/auto, parle de diagnostic, confiance, transparence, rapidité.
Si le business est immobilier, parle de valorisation, accompagnement, estimation, expertise locale.

{SCHEMA_HINT}
"""


async def generate_site_content(project: Dict[str, Any]) -> Dict[str, Any]:
    """Generate structured premium website content with Gemini."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY missing")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name=os.environ.get("GEMINI_MODEL", "gemini-1.5-flash"),
        generation_config={
            "temperature": 0.82,
            "top_p": 0.96,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",
        },
    )

    brief = _build_brief(project)

    def _call_model() -> str:
        response = model.generate_content(brief)
        return getattr(response, "text", "") or ""

    text = await asyncio.to_thread(_call_model)
    content = _extract_json(text)
    return _sanitize_content(content, project)
