"""Cliente para consumir la API de HubSpot (Private App).

Scopes soportados:
- crm.objects.contacts.read, crm.objects.companies.read, crm.objects.deals.read
- crm.objects.line_items.read, crm.objects.owners.read, crm.objects.leads.read
- crm.schemas.contacts.read, crm.schemas.companies.read, crm.schemas.deals.read
- crm.pipelines.orders.read
- marketing.campaigns.read, marketing.campaigns.revenue.read
"""

import logging
from typing import Any

import requests

from app.core.config import settings

HUBSPOT_BASE_URL = "https://api.hubapi.com"
DEFAULT_LIMIT = 100
logger = logging.getLogger(__name__)


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.HUBSPOT_API_KEY}",
        "Content-Type": "application/json",
    }


def _get(endpoint: str, params: dict[str, Any] | None = None) -> dict | None:
    """Realiza GET a la API de HubSpot."""
    if not settings.HUBSPOT_API_KEY:
        return None
    url = f"{HUBSPOT_BASE_URL}{endpoint}"
    try:
        resp = requests.get(url, headers=_headers(), params=params or {}, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        return {"error": resp.status_code, "detail": resp.text}
    except requests.RequestException as e:
        return {"error": str(e)}


def _post(endpoint: str, json: dict) -> dict | None:
    """Realiza POST a la API de HubSpot."""
    if not settings.HUBSPOT_API_KEY:
        return None
    url = f"{HUBSPOT_BASE_URL}{endpoint}"
    try:
        resp = requests.post(url, headers=_headers(), json=json, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        return {"error": resp.status_code, "detail": resp.text}
    except requests.RequestException as e:
        return {"error": str(e)}


# --- CRM Objects ---
def get_contacts(limit: int = DEFAULT_LIMIT, after: str | None = None) -> dict | None:
    """Contactos (crm.objects.contacts.read)."""
    params = {"limit": limit}
    if after:
        params["after"] = after
    return _get("/crm/v3/objects/contacts", params=params)


def get_companies(limit: int = DEFAULT_LIMIT, after: str | None = None) -> dict | None:
    """Empresas (crm.objects.companies.read)."""
    params = {"limit": limit}
    if after:
        params["after"] = after
    return _get("/crm/v3/objects/companies", params=params)


def get_deals(limit: int = DEFAULT_LIMIT, after: str | None = None) -> dict | None:
    """Deals (crm.objects.deals.read)."""
    params = {"limit": limit}
    if after:
        params["after"] = after
    return _get("/crm/v3/objects/deals", params=params)


def get_line_items(
    limit: int = DEFAULT_LIMIT, after: str | None = None
) -> dict | None:
    """Line items (crm.objects.line_items.read)."""
    params = {"limit": limit}
    if after:
        params["after"] = after
    return _get("/crm/v3/objects/line_items", params=params)


def get_leads(limit: int = DEFAULT_LIMIT, after: str | None = None) -> dict | None:
    """Leads (crm.objects.leads.read)."""
    params = {"limit": limit}
    if after:
        params["after"] = after
    return _get("/crm/v3/objects/0-136", params=params)  # leads object type


def get_owners() -> dict | None:
    """Owners (crm.objects.owners.read)."""
    return _get("/crm/v3/owners")


# --- CRM Schemas / Properties ---
def get_contact_properties() -> dict | None:
    """Schema de contactos (crm.schemas.contacts.read)."""
    return _get("/crm/v3/properties/contacts")


def get_company_properties() -> dict | None:
    """Schema de empresas (crm.schemas.companies.read)."""
    return _get("/crm/v3/properties/companies")


def get_deal_properties() -> dict | None:
    """Schema de deals (crm.schemas.deals.read)."""
    return _get("/crm/v3/properties/deals")


# --- Pipelines ---
def get_deal_pipelines() -> dict | None:
    """Pipelines de deals (necesario para dealstages)."""
    return _get("/crm/v3/pipelines/deals")


def get_order_pipelines() -> dict | None:
    """Pipelines de órdenes (crm.pipelines.orders.read)."""
    return _get("/crm/v3/pipelines/orders")


# --- Marketing Campaigns ---
def get_campaigns(
    limit: int = 50, after: str | None = None, properties: str | None = None
) -> dict | None:
    """Lista campañas de marketing (marketing.campaigns.read)."""
    params: dict[str, Any] = {"limit": limit}
    if after:
        params["after"] = after
    if properties:
        params["properties"] = properties
    return _get("/marketing/v3/campaigns", params=params)


def get_campaign_metrics(
    campaign_guid: str, start_date: str | None = None, end_date: str | None = None
) -> dict | None:
    """Métricas de una campaña (marketing.campaigns.read)."""
    params: dict[str, Any] = {}
    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date
    return _get(
        f"/marketing/v3/campaigns/{campaign_guid}/reports/metrics", params=params
    )


def get_campaign_revenue(
    campaign_guid: str, start_date: str | None = None, end_date: str | None = None
) -> dict | None:
    """Ingresos atribuidos a una campaña (marketing.campaigns.revenue.read)."""
    params: dict[str, Any] = {}
    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date
    return _get(
        f"/marketing/v3/campaigns/{campaign_guid}/reports/revenue", params=params
    )


def _store_result(data: dict, key: str, result: dict | None) -> None:
    """Guarda resultado en data o error."""
    if result is not None and "error" not in result:
        data[key] = result
    elif result is not None and "error" in result:
        data[key] = {"error": result.get("error"), "detail": str(result.get("detail", ""))[:200]}


def fetch_all_bi_data(limit: int = 100) -> dict:
    """
    Obtiene todos los datos disponibles para construir KPIs/BI.

    Incluye: contacts, companies, deals, line_items, leads, owners,
    schemas (properties), pipelines, campaigns (+ metrics/revenue para las primeras).
    """
    data: dict = {}

    # CRM Objects
    _store_result(data, "contacts", get_contacts(limit=limit))
    _store_result(data, "companies", get_companies(limit=limit))
    _store_result(data, "deals", get_deals(limit=limit))
    _store_result(data, "line_items", get_line_items(limit=limit))
    _store_result(data, "leads", get_leads(limit=limit))
    _store_result(data, "owners", get_owners())

    # Schemas (útil para saber qué campos existen)
    _store_result(data, "contact_properties", get_contact_properties())
    _store_result(data, "company_properties", get_company_properties())
    _store_result(data, "deal_properties", get_deal_properties())

    # Pipelines
    _store_result(data, "deal_pipelines", get_deal_pipelines())
    _store_result(data, "order_pipelines", get_order_pipelines())

    # Marketing campaigns
    campaigns_resp = get_campaigns(limit=min(limit, 50), properties="hs_name,hs_campaign_status,hs_start_date,hs_end_date")
    _store_result(data, "campaigns", campaigns_resp)

    # Métricas y revenue de las primeras campañas (si hay)
    if campaigns_resp and "error" not in campaigns_resp and "results" in campaigns_resp:
        results = campaigns_resp.get("results", [])[:5]
        campaign_metrics: list[dict] = []
        campaign_revenue: list[dict] = []
        for c in results:
            cid = c.get("id")
            if cid:
                m = get_campaign_metrics(cid)
                r = get_campaign_revenue(cid)
                if m and "error" not in m:
                    campaign_metrics.append({"campaign_id": cid, "metrics": m})
                if r and "error" not in r:
                    campaign_revenue.append({"campaign_id": cid, "revenue": r})
        if campaign_metrics:
            data["campaign_metrics_sample"] = campaign_metrics
        if campaign_revenue:
            data["campaign_revenue_sample"] = campaign_revenue

    return data
