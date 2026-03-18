from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime

app = FastAPI(
    title="Global Education Index API",
    description="Global education data including literacy rates, school enrollment, government spending on education, and rankings for 190+ countries. Powered by World Bank Open Data.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

WB_BASE = "https://api.worldbank.org/v2"

INDICATORS = {
    "literacy":          {"id": "SE.ADT.LITR.ZS",   "name": "Adult Literacy Rate",              "unit": "% of Adults 15+"},
    "primary_enroll":    {"id": "SE.PRM.ENRR",       "name": "School Enrollment: Primary",       "unit": "% Gross"},
    "secondary_enroll":  {"id": "SE.SEC.ENRR",       "name": "School Enrollment: Secondary",     "unit": "% Gross"},
    "tertiary_enroll":   {"id": "SE.TER.ENRR",       "name": "School Enrollment: Tertiary",      "unit": "% Gross"},
    "edu_spending":      {"id": "SE.XPD.TOTL.GD.ZS", "name": "Government Education Spending",    "unit": "% of GDP"},
    "pupil_teacher":     {"id": "SE.PRM.PTRT.ZS",    "name": "Pupil-Teacher Ratio: Primary",     "unit": "Pupils per Teacher"},
    "completion_primary":{"id": "SE.PRM.CMPT.ZS",    "name": "Primary School Completion Rate",   "unit": "%"},
    "female_edu":        {"id": "SE.SEC.ENRR.FE",    "name": "Female Secondary Enrollment",      "unit": "% Gross"},
}

COUNTRIES = {
    "WLD": "World",
    "USA": "United States",
    "CHN": "China",
    "IND": "India",
    "DEU": "Germany",
    "JPN": "Japan",
    "GBR": "United Kingdom",
    "FRA": "France",
    "KOR": "South Korea",
    "FIN": "Finland",
    "NOR": "Norway",
    "SWE": "Sweden",
    "DNK": "Denmark",
    "CHE": "Switzerland",
    "AUS": "Australia",
    "CAN": "Canada",
    "NZL": "New Zealand",
    "SGP": "Singapore",
    "BRA": "Brazil",
    "ZAF": "South Africa",
    "NGA": "Nigeria",
    "ETH": "Ethiopia",
    "BGD": "Bangladesh",
    "PAK": "Pakistan",
    "IDN": "Indonesia",
    "MEX": "Mexico",
    "TUR": "Turkey",
    "RUS": "Russia",
    "POL": "Poland",
    "ITA": "Italy",
}


async def fetch_wb_country(country_code: str, indicator_id: str, limit: int = 10):
    url = f"{WB_BASE}/country/{country_code}/indicator/{indicator_id}"
    params = {"format": "json", "mrv": limit, "per_page": limit}
    async with httpx.AsyncClient(timeout=15) as client:
        res = await client.get(url, params=params)
        data = res.json()
    if not data or len(data) < 2:
        return []
    records = data[1] or []
    return [
        {"year": str(r["date"]), "value": r["value"]}
        for r in records
        if r.get("value") is not None
    ]


async def fetch_wb_all_countries(indicator_id: str):
    url = f"{WB_BASE}/country/all/indicator/{indicator_id}"
    params = {"format": "json", "mrv": 1, "per_page": 300}
    async with httpx.AsyncClient(timeout=20) as client:
        res = await client.get(url, params=params)
        data = res.json()
    if not data or len(data) < 2:
        return []
    records = data[1] or []
    return [
        {"country_code": r["countryiso3code"], "country": r["country"]["value"], "year": str(r["date"]), "value": r["value"]}
        for r in records
        if r.get("value") is not None and r.get("countryiso3code")
    ]


@app.get("/")
def root():
    return {
        "api": "Global Education Index API",
        "version": "1.0.0",
        "provider": "GlobalData Store",
        "source": "World Bank Open Data",
        "endpoints": [
            "/summary", "/literacy", "/enrollment", "/spending",
            "/pupil-teacher", "/completion", "/tertiary",
            "/literacy-ranking", "/spending-ranking"
        ],
        "countries": list(COUNTRIES.keys()),
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/summary")
async def summary(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=5, ge=1, le=30)
):
    """All education indicators for a country"""
    country = country.upper()
    results = {}
    for key, meta in INDICATORS.items():
        results[key] = await fetch_wb_country(country, meta["id"], limit)
    formatted = {
        key: {"name": INDICATORS[key]["name"], "unit": INDICATORS[key]["unit"], "data": results[key]}
        for key in INDICATORS
    }
    return {"country_code": country, "country": COUNTRIES.get(country, country), "source": "World Bank Open Data", "updated_at": datetime.utcnow().isoformat() + "Z", "indicators": formatted}


@app.get("/literacy")
async def literacy(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Adult literacy rate (% of people 15 and above)"""
    country = country.upper()
    data = await fetch_wb_country(country, "SE.ADT.LITR.ZS", limit)
    return {"indicator": "Adult Literacy Rate", "series_id": "SE.ADT.LITR.ZS", "unit": "% of Adults 15+", "frequency": "Annual", "country_code": country, "country": COUNTRIES.get(country, country), "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}


@app.get("/enrollment")
async def enrollment(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """School enrollment at primary, secondary, and tertiary levels"""
    country = country.upper()
    primary = await fetch_wb_country(country, "SE.PRM.ENRR", limit)
    secondary = await fetch_wb_country(country, "SE.SEC.ENRR", limit)
    tertiary = await fetch_wb_country(country, "SE.TER.ENRR", limit)
    return {
        "country_code": country, "country": COUNTRIES.get(country, country),
        "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z",
        "primary": {"series_id": "SE.PRM.ENRR", "unit": "% Gross", "data": primary},
        "secondary": {"series_id": "SE.SEC.ENRR", "unit": "% Gross", "data": secondary},
        "tertiary": {"series_id": "SE.TER.ENRR", "unit": "% Gross", "data": tertiary},
    }


@app.get("/spending")
async def spending(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Government expenditure on education (% of GDP)"""
    country = country.upper()
    data = await fetch_wb_country(country, "SE.XPD.TOTL.GD.ZS", limit)
    return {"indicator": "Government Education Spending", "series_id": "SE.XPD.TOTL.GD.ZS", "unit": "% of GDP", "frequency": "Annual", "country_code": country, "country": COUNTRIES.get(country, country), "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}


@app.get("/pupil-teacher")
async def pupil_teacher(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Pupil-teacher ratio in primary education"""
    country = country.upper()
    data = await fetch_wb_country(country, "SE.PRM.PTRT.ZS", limit)
    return {"indicator": "Pupil-Teacher Ratio: Primary", "series_id": "SE.PRM.PTRT.ZS", "unit": "Pupils per Teacher", "frequency": "Annual", "country_code": country, "country": COUNTRIES.get(country, country), "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}


@app.get("/completion")
async def completion(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Primary school completion rate (% of relevant age group)"""
    country = country.upper()
    data = await fetch_wb_country(country, "SE.PRM.CMPT.ZS", limit)
    return {"indicator": "Primary School Completion Rate", "series_id": "SE.PRM.CMPT.ZS", "unit": "%", "frequency": "Annual", "country_code": country, "country": COUNTRIES.get(country, country), "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}


@app.get("/tertiary")
async def tertiary(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Tertiary education enrollment (university/college, % gross)"""
    country = country.upper()
    data = await fetch_wb_country(country, "SE.TER.ENRR", limit)
    return {"indicator": "School Enrollment: Tertiary", "series_id": "SE.TER.ENRR", "unit": "% Gross", "frequency": "Annual", "country_code": country, "country": COUNTRIES.get(country, country), "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}


@app.get("/literacy-ranking")
async def literacy_ranking(limit: int = Query(default=20, ge=1, le=50)):
    """Countries ranked by adult literacy rate"""
    data = await fetch_wb_all_countries("SE.ADT.LITR.ZS")
    sorted_data = sorted(
        [d for d in data if len(d["country_code"]) == 3],
        key=lambda x: x["value"] if x["value"] is not None else 0,
        reverse=True
    )
    ranked = [{"rank": i + 1, **entry} for i, entry in enumerate(sorted_data[:limit])]
    return {"indicator": "Adult Literacy Rate", "unit": "% of Adults 15+", "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "literacy_ranking": ranked}


@app.get("/spending-ranking")
async def spending_ranking(limit: int = Query(default=20, ge=1, le=50)):
    """Countries ranked by education spending as % of GDP"""
    data = await fetch_wb_all_countries("SE.XPD.TOTL.GD.ZS")
    sorted_data = sorted(
        [d for d in data if len(d["country_code"]) == 3],
        key=lambda x: x["value"] if x["value"] is not None else 0,
        reverse=True
    )
    ranked = [{"rank": i + 1, **entry} for i, entry in enumerate(sorted_data[:limit])]
    return {"indicator": "Government Education Spending", "unit": "% of GDP", "source": "World Bank", "updated_at": datetime.utcnow().isoformat() + "Z", "spending_ranking": ranked}

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path == "/":
        return await call_next(request)
    key = request.headers.get("X-RapidAPI-Key", "")
    if not key:
        return JSONResponse(status_code=401, content={"detail": "Missing X-RapidAPI-Key header"})
    return await call_next(request)
