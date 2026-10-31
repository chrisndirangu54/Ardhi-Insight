from __future__ import annotations
import os, math
from datetime import datetime
from typing import Optional
import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Ardhi Insight", version="0.2.0")
from backend.geospatial import router as geospatial_router
app.include_router(geospatial_router)
# Demonstration catalog. Do not represent these listings as verified offers.
LISTINGS = [
    {"id":1,"location":"Ruiru","county":"Kiambu","lat":-1.145,"lon":36.96,"acreage":0.125,"asking_price_kes":2800000,"verified":False},
    {"id":2,"location":"Kitengela","county":"Kajiado","lat":-1.47,"lon":36.96,"acreage":0.125,"asking_price_kes":1700000,"verified":False},
    {"id":3,"location":"Thika","county":"Kiambu","lat":-1.04,"lon":37.08,"acreage":0.25,"asking_price_kes":3700000,"verified":False},
]
# Placeholder observation registry; ingest licensed reports with citation and dates.
OBSERVATIONS: list[dict] = []
URBAN_CENTRES = {"Nairobi":(-1.286389,36.817223),"Mombasa":(-4.0435,39.6682),
                 "Kisumu":(-0.0917,34.7680),"Nakuru":(-0.3031,36.0800),
                 "Eldoret":(0.5143,35.2698),"Thika":(-1.0333,37.0693)}

def haversine(lat1,lon1,lat2,lon2):
    r=6371.0088
    a=math.sin(math.radians(lat2-lat1)/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(math.radians(lon2-lon1)/2)**2
    return 2*r*math.asin(min(1,math.sqrt(a)))

class Location(BaseModel):
    latitude:float=Field(ge=-90,le=90)
    longitude:float=Field(ge=-180,le=180)

class Simulation(BaseModel):
    purchase_kes:float=Field(gt=0)
    annual_growth_pct:float=Field(ge=-100,le=100)
    years:int=Field(ge=1,le=40)
    additional_costs_kes:float=Field(default=0,ge=0)
    selling_cost_pct:float=Field(default=0,ge=0,le=100)

@app.get("/api/health")
def health():
    return {"status":"ok","model_trained":False,"regen_insight_connected":bool(os.environ.get("REGEN_INSIGHT_URL"))}

@app.get("/api/listings")
def listings():
    return {"items":LISTINGS,"notice":"Illustrative listings, not verified properties for sale."}

@app.get("/api/listings/{listing_id}/intelligence")
def listing_intelligence(listing_id:int):
    listing=next((x for x in LISTINGS if x["id"]==listing_id),None)
    if listing is None:raise HTTPException(404,"Listing not found")
    distances=sorted([{"centre":name,"straight_line_km":round(haversine(listing["lat"],listing["lon"],*coords),1)} for name,coords in URBAN_CENTRES.items()], key=lambda x:x["straight_line_km"])
    return {"listing":listing,"urban_centres":distances,
            "ownership":{"status":"unverified","registry_url":"https://ardhisasa.lands.go.ke/","official_search_required":True},
            "regional_market_observations":[o for o in OBSERVATIONS if o.get("location","").lower()==listing["location"].lower()],
            "environment":{"status":"not_assessed","screening_route":"/api/intelligence/environment"},
            "caveat":"Regional observations are not parcel valuations. Geographic distances are straight-line rather than road travel times."}

@app.post("/api/investment/simulate")
def simulate(value:Simulation):
    resale=value.purchase_kes*((1+value.annual_growth_pct/100)**value.years)
    net=resale*(1-value.selling_cost_pct/100)-value.purchase_kes-value.additional_costs_kes
    investment=value.purchase_kes+value.additional_costs_kes
    return {"projected_resale_kes":round(resale,2),"net_profit_kes":round(net,2),"roi_pct":round(100*net/investment,2),
            "disclaimer":"Scenario calculator only; growth rate is a user assumption, not an ML forecast."}

@app.get("/api/market/observations")
def observations():
    return {"items":OBSERVATIONS,"notice":"No verified bulk historical transaction feed is connected. Supply licensed, dated observations."}

@app.post("/api/intelligence/environment")
async def environment(loc:Location):
    endpoint=os.environ.get("REGEN_INSIGHT_URL")
    token=os.environ.get("REGEN_INSIGHT_TOKEN")
    if not endpoint:
        return {"status":"not_configured","hazards":[],"note":"No risk assessment performed; absence of data does not indicate safety."}
    if not endpoint.startswith("https://"):
        raise HTTPException(503,"REGEN_INSIGHT_URL must use HTTPS")
    headers={"Authorization":f"Bearer {token}"} if token else {}
    try:
        async with httpx.AsyncClient(timeout=12,follow_redirects=False) as client:
            resp=await client.post(endpoint, json=loc.model_dump(), headers=headers)
            resp.raise_for_status()
            result=resp.json()
    except (httpx.HTTPError,ValueError):
        raise HTTPException(503,"Regen Insight service is unavailable or returned an invalid response")
    return {"status":"upstream_response","source":"Regen Insight","assessment":result,"notice":"Verify methodology, spatial coverage and observation date before use."}

@app.get("/",response_class=HTMLResponse)
def homepage():
    return """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Ardhi Insight</title><style>body{font-family:system-ui;margin:auto;max-width:1050px;background:#f3f7f4;color:#153f31;padding:24px}article{background:white;padding:22px;border-radius:15px;margin:20px 0}button{background:#126344;color:white;border:0;padding:10px 15px;border-radius:8px;cursor:pointer}input,select{padding:9px;margin:5px;max-width:100%}pre{white-space:pre-wrap;overflow-wrap:anywhere}small{color:#576d62}</style></head><body><h1>Ardhi Insight</h1><p>Kenyan land marketplace and location intelligence research</p><p><small>Listings are illustrations. No ownership verification, environmental clearance or future price forecast has been performed.</small></p><article><h2>Explore land listings</h2><div id="listings">Loading…</div></article><article><h2>Parcel intelligence</h2><label>Listing <select id="parcel"></select></label><button onclick="inspect()">Analyze</button><pre id="analysis"></pre></article><article><h2>Regen Insight environmental research</h2><label>Latitude <input id="lat" type="number" step="any" value="-1.145"></label><label>Longitude <input id="lon" type="number" step="any" value="36.96"></label><button onclick="environment()">Screen location</button><pre id="hazards"></pre></article><article><h2>Investment scenarios</h2><label>Price KES <input id="price" type="number" value="2800000"></label><label>Annual growth % <input id="growth" type="number" value="5"></label><label>Years <input id="years" type="number" value="5"></label><button onclick="simulate()">Simulate (not a prediction)</button><pre id="forecast"></pre></article><article><h2>Official ownership verification</h2><p>For legal verification request an authorized official land search. Listings are not title-verified by the platform.</p><a href="https://ardhisasa.lands.go.ke/" target="_blank" rel="noopener noreferrer">Go to Ardhisasa</a></article><script>
async function json(url,options){const r=await fetch(url,options);if(!r.ok)throw new Error('Request failed ('+r.status+')');return r.json()}
function post(url,payload){return json(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})}
json('/api/listings').then(d=>{document.querySelector('#listings').innerHTML=d.items.map(x=>'<p><b>'+x.location+', '+x.county+'</b> — KES '+x.asking_price_kes.toLocaleString()+' — '+x.acreage+' acres (unverified)</p>').join('');document.querySelector('#parcel').innerHTML=d.items.map(x=>'<option value="'+x.id+'">'+x.location+'</option>').join('')}).catch(e=>document.querySelector('#listings').textContent=e.message);
async function inspect(){try{document.querySelector('#analysis').textContent=JSON.stringify(await json('/api/listings/'+document.querySelector('#parcel').value+'/intelligence'),null,2)}catch(e){document.querySelector('#analysis').textContent=e.message}}
async function environment(){try{document.querySelector('#hazards').textContent=JSON.stringify(await post('/api/intelligence/environment',{latitude:Number(document.querySelector('#lat').value),longitude:Number(document.querySelector('#lon').value)}),null,2)}catch(e){document.querySelector('#hazards').textContent=e.message}}
async function simulate(){try{document.querySelector('#forecast').textContent=JSON.stringify(await post('/api/investment/simulate',{purchase_kes:Number(document.querySelector('#price').value),annual_growth_pct:Number(document.querySelector('#growth').value),years:Number(document.querySelector('#years').value)}),null,2)}catch(e){document.querySelector('#forecast').textContent=e.message}}
</script></body></html>"""
