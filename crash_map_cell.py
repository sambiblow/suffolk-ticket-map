import os
import re
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import folium
from branca.element import Element

# Work inside your ticket_map folder (finds it automatically on any computer)
os.chdir(os.path.join(os.path.expanduser("~"), "ticket_map"))

TOWNS = ["Babylon", "Brookhaven", "Huntington", "Islip", "Smithtown"]
VILLAGES = {
    "Village Of Islandia": "Islip", "Village Of Brightwaters": "Islip",
    "Village Of Patchogue": "Brookhaven", "Village Of Lake Grove": "Brookhaven",
    "Village Of Bellport": "Brookhaven", "Village Of Mastic Beach": "Brookhaven",
    "Village Of Babylon": "Babylon", "Village Of Lindenhurst": "Babylon", "Village Of Amityville": "Babylon",
    "Village Of Huntington Bay": "Huntington", "Village Of Northport": "Huntington",
}

# ---------- 1. Load the tickets ----------
tk = pd.read_csv("ticket_data_clean.zip", usecols=["LOCATION", "MUNICIP", "ACCIDENT"], dtype=str).fillna("")
tk["town"] = tk["MUNICIP"].str.replace("TOWN OF ", "").str.title().replace(VILLAGES)
tk = tk[tk["town"].isin(TOWNS)].copy()
tk["crash"] = tk["ACCIDENT"].str.upper().eq("Y")
print(f"{len(tk):,} tickets, {tk['crash'].sum():,} crash-related")

# ---------- 2. Rules for cleaning road names (same as the road map) ----------
# Spelling swaps so every version of a word matches
ABBREVIATIONS = [
    (r"\bAVENUE\b|\bAV\b", "AVE"), (r"\bROAD\b", "RD"), (r"\bSTREET\b", "ST"),
    (r"\bHIGHWAY\b|\bHGWY\b|\bHWAY\b|\bHW\b", "HWY"), (r"\bTURNPIKE\b|\bTPK\b|\bTNPK\b", "TPKE"),
    (r"\bPARKWAY\b|\bPKY\b|\bPWKY\b|\bPWY\b|\bPKWAY\b", "PKWY"), (r"\bBOULEVARD\b|\bBL\b", "BLVD"),
    (r"\bDRIVE\b", "DR"), (r"\bLANE\b", "LN"), (r"\bPLACE\b", "PL"), (r"\bCOURT\b", "CT"),
    (r"\bEXPRESSWAY\b|\bEXPWY\b|\bE ?WAY\b", "EXPY"), (r"\bCAUSEWAY\b", "CSWY"), (r"\bBYPASS\b", "BYP"),
    (r"\bSTATE PKWY\b", "PKWY"), (r"\bNORTH\b", "N"), (r"\bSOUTH\b", "S"), (r"\bEAST\b", "E"), (r"\bWEST\b", "W"),
    (r"\bMOUNT\b", "MT"), (r"\bCPT\b|\bCAPT\b", "CAPTAIN"), (r"\bVETS HWY\b", "VETERANS HWY"),
    (r"\bNY AVE\b", "NEW YORK AVE"), (r"\bBROAD ?HOLLOW RD\b", "RT 110"), (r"\bDPA\b", "DEER PARK AVE"),
    (r"\bLI AVE\b", "LONG ISLAND AVE"), (r"\bBAYSHORE RD\b", "BAY SHORE RD"), (r"\bSPUR (N|S)\b", r"SPUR DR \1"),
]

# Route numbers that are really a named road
ROUTE_ALIASES = {"RT 27": "SUNRISE HWY", "RT 454": "VETERANS MEMORIAL HWY", "RT 347": "NESCONSET HWY",
                 "RT 46": "WILLIAM FLOYD PKWY", "CR 46": "WILLIAM FLOYD PKWY", "CR 97": "NICOLLS RD",
                 "RT 97": "NICOLLS RD", "RT 83": "CR 83"}

RTE = r"(?:RT|RTE|ROUTE|NY|SR|STATE RTE)"

def basic_clean(text):
    s = str(text or "").upper()
    s = re.sub(r"\bC/R\b", "CR", s)
    s = re.sub(r"\bI/(\d)", r"I \1", s)
    s = re.sub(r"[.,'-]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    for pattern, replacement in ABBREVIATIONS:
        s = re.sub(pattern, replacement, s)
    return s

def major_road(s):
    """Return the standard name if the text is one of the major roads, otherwise None."""
    if re.search(r"\bEXPY\b|\bLIE\b|(^|[^0-9])495([^0-9]|$)", s): return "LONG ISLAND EXPY"
    if re.search(r"SOUTHERN ST|SOUTHERN PKWY|SSPK|\bSSP\b|\bSS PKWY\b", s): return "SOUTHERN STATE PKWY"
    if re.search(r"NORTHERN ST|NORTHERN PKWY|NSPK|\bNSP\b", s): return "NORTHERN STATE PKWY"
    if "SAGTIKOS" in s: return "SAGTIKOS PKWY"
    if "SUNKEN MEADOW" in s: return "SUNKEN MEADOW PKWY"
    if "ROBERT MOSES" in s and "PARK" not in s.replace("PKWY", ""): return "ROBERT MOSES CSWY"
    if re.search(r"SUNRISE(?! (AVE|DR|CT|LN|PL|ST|RD|BLVD|TER|PATH|TRL)\b)", s) or s == "27": return "SUNRISE HWY"
    if re.search(rf"VETERANS (MEM|HWY)|VETS MEM|\b{RTE} ?454\b|(^|\s)454(\s|$)", s): return "VETERANS MEMORIAL HWY"
    if re.search(rf"\b{RTE} ?112\b|(^|\s)112(\s|$)|PORT JEFFERSON AND PATCHOGUE", s): return "RT 112"
    if "WILLIAM FLOYD" in s or "WM FLOYD" in s: return "WILLIAM FLOYD PKWY"
    if "NICOLLS" in s: return "NICOLLS RD"
    if "MOTOR P" in s: return "MOTOR PKWY"
    if re.search(r"MONTAUK( HWY)?$|MONTAUK HWY", s): return "MONTAUK HWY"
    if "MIDDLE COUNTRY" in s: return "MIDDLE COUNTRY RD"
    if re.search(r"JERICHO( TPKE)?$|JERICHO TPKE", s): return "JERICHO TPKE"
    if ("NESCONSET" in s and "HWY" in s) or re.search(rf"\b{RTE} ?347\b", s): return "NESCONSET HWY"
    if re.fullmatch(r"\d{2,3}A?", s): return "RT " + s
    m = re.search(rf"\b{RTE} ?(\d{{2,3}}A?)\b", s)
    if m: return "RT " + m.group(1)
    m = re.search(r"\b(?:CR|CO RD|COUNTY RD) ?(\d{1,3}A?)\b", s)
    if m: return "CR " + m.group(1)
    return None

def use_alias(name):
    return ROUTE_ALIASES.get(name, name) if name else name

# Words at the start of a location that aren't part of the road name
LEADING_JUNK = r"^(?:(?:N|S|E|W)/?B\s+|(?:NB|SB|EB|WB)\s+|C/O\s+|I/F/O\s+|I/O\s+|IFO\s+|P/L(?:OT)?(?:\s+OF)?\s+|IN FRONT OF\s+|CORNER OF\s+)+"
# Words that start a cross street or landmark (everything after them is dropped)
CROSS_STREET = r"\s*(?:@|&| AND | AT | X | / |/| E/O | W/O | N/O | S/O | NEAR | EXIT | OPP | IFO )\s*"

def ticket_road(location):
    s = basic_clean(location)
    s = re.sub(LEADING_JUNK, "", s)
    found = major_road(s)
    if found: return use_alias(found)
    s = re.split(CROSS_STREET, s)[0]          # drop the cross street
    s = re.sub(r"^\d+\s+", "", s)             # drop a house number
    s = re.sub(r"\s+(N|S|E|W)/?B$", "", s).strip()
    found = major_road(s)
    if found: return use_alias(found)
    return s or None

def census_road(name):
    s = basic_clean(name)
    return use_alias(major_road(s)) or s

# ---------- 3. Clean every ticket location ----------
lookup = {loc: ticket_road(loc) for loc in tk["LOCATION"].unique()}
tk["road_key"] = tk["LOCATION"].map(lookup)

# ---------- 4. Load the Census roads and town borders, cut roads at town lines ----------
towns = gpd.read_file("tl_2024_36_cousub.zip")
towns = towns[(towns["COUNTYFP"] == "103") & (towns["NAME"].isin(TOWNS))][["NAME", "geometry"]]
towns = towns.rename(columns={"NAME": "town"}).to_crs(2263)
roads = gpd.read_file("tl_2024_36103_roads.zip").to_crs(2263)
roads["road_key"] = roads["FULLNAME"].fillna("").map(census_road)
road_pieces = gpd.overlay(roads[["FULLNAME", "road_key", "geometry"]], towns, how="intersection", keep_geom_type=True)

# ---------- 5. Match tickets to roads in the same town ----------
names_in_town = {t: set(road_pieces.loc[road_pieces["town"] == t, "road_key"]) for t in TOWNS}
def match(town, key):
    if not isinstance(key, str) or not key:
        return None
    names = names_in_town[town]
    if key in names:
        return key
    starts = [n for n in names if n and len(n) >= 6 and key.startswith(n + " ")]
    if starts:
        return max(starts, key=len)
    longer = [n for n in names if len(key) >= 4 and n.startswith(key + " ")]
    if longer:
        return min(longer, key=len)
    return None

pairs = tk[["town", "road_key"]].drop_duplicates()
pairs["matched"] = [match(t, k) for t, k in zip(pairs["town"], pairs["road_key"])]
tk = tk.merge(pairs, on=["town", "road_key"], how="left")
placed = tk.dropna(subset=["matched"])
print(f"{tk['matched'].notna().mean():.1%} of tickets matched to a road")

# ---------- 6. Count tickets and crash-related tickets per road ----------
per_road = placed.groupby(["town", "matched"]).agg(tickets=("crash", "size"), crashes=("crash", "sum")).reset_index()
per_road = per_road.rename(columns={"matched": "road_key"})
per_road["crash_rate"] = per_road["crashes"] / per_road["tickets"] * 100

roads_c = road_pieces.merge(per_road, on=["town", "road_key"], how="inner")
roads_c = roads_c[roads_c["crashes"] > 0]
roads_c = roads_c.dissolve(by=["town", "road_key"], aggfunc={"tickets": "first", "crashes": "first", "crash_rate": "first"}).reset_index()
roads_c = roads_c.to_crs(4326)
roads_c["geometry"] = roads_c.geometry.simplify(0.0001)
roads_c["road"] = roads_c["road_key"].str.title()
roads_c["crash_rate"] = roads_c["crash_rate"].round(1)
roads_c = roads_c.sort_values("crashes")
print(f"{len(roads_c):,} roads with at least one crash-related ticket")

# ---------- 7. The map ----------
MIN_TICKETS = 200     # roads need at least this many tickets before their crash rate is shown
cmap = plt.get_cmap("YlOrRd")
m = folium.Map(location=[40.82, -73.1], zoom_start=10, tiles=None)
folium.TileLayer("Esri.WorldGrayCanvas", control=False).add_to(m)
folium.GeoJson(towns.to_crs(4326), control=False,
               style_function=lambda f: {"color": "#7a8580", "weight": 1.5, "fillOpacity": 0}).add_to(m)

def add_layer(data, column, label, show, log=True):
    data = data.sort_values(column).copy()
    top = data[column].max()
    scale = mcolors.LogNorm(vmin=1, vmax=top) if log else mcolors.Normalize(vmin=0, vmax=top)
    data["color"] = [mcolors.to_hex(cmap(scale(max(v, 1) if log else v))) for v in data[column]]
    pos = (np.log10(data[column].clip(lower=1)) / np.log10(top)) if log else (data[column] / top)
    data["width"] = (1.5 + 5 * pos ** 1.3).round(2)
    group = folium.FeatureGroup(name=label, overlay=False, show=show)
    folium.GeoJson(
        data[["road", "town", "crashes", "tickets", "crash_rate", "color", "width", "geometry"]],
        style_function=lambda f: {"color": f["properties"]["color"], "weight": f["properties"]["width"], "opacity": 0.9},
        highlight_function=lambda f: {"weight": 10},
        tooltip=folium.GeoJsonTooltip(
            fields=["road", "town", "crashes", "tickets", "crash_rate"],
            aliases=["Road", "Town", "Crash-related tickets", "All tickets", "Crash rate (%)"],
            localize=True),
    ).add_to(group)
    group.add_to(m)

add_layer(roads_c, "crashes", "Crash-related tickets (count)", True, log=True)
add_layer(roads_c[roads_c["tickets"] >= MIN_TICKETS], "crash_rate", f"Crash rate (roads with {MIN_TICKETS}+ tickets)", False, log=False)
folium.LayerControl(position="bottomright", collapsed=False).add_to(m)

# ---------- 8. Side panel with the top roads ----------
def top_list(data, column, fmt):
    rows = ""
    for i, r in enumerate(data.sort_values(column, ascending=False).head(10).itertuples(), start=1):
        x0, y0, x1, y1 = r.geometry.bounds
        rows += (f'<tr class="zoom" onclick="MAP.fitBounds([[{y0},{x0}],[{y1},{x1}]])">'
                 f'<td style="color:#888">{i}</td><td><b>{r.road}</b><br><span class="lbl">{r.town}</span></td>'
                 f'<td class="num">{fmt(r)}</td></tr>')
    return rows

by_count = top_list(roads_c, "crashes", lambda r: f"{r.crashes:,}")
by_rate = top_list(roads_c[roads_c["tickets"] >= MIN_TICKETS], "crash_rate", lambda r: f"{r.crash_rate:.1f}%")
n_crash = int(placed["crash"].sum())
overall_rate = placed["crash"].mean() * 100
ramp = ", ".join(mcolors.to_hex(cmap(x)) for x in np.linspace(0, 1, 7))

panel = f"""
<style>
  #panel {{position:fixed; top:12px; right:12px; z-index:9999; width:330px; max-height:calc(100vh - 200px); overflow:auto;
          background:#fff; border:1px solid #ccc; border-radius:8px; padding:14px; font:13px Arial, sans-serif;
          box-shadow:0 2px 10px rgba(0,0,0,.15)}}
  #panel h1 {{font-size:17px; margin:0 0 4px; padding-right:50px}}
  #panel h2 {{font-size:12px; text-transform:uppercase; letter-spacing:.06em; color:#555; margin:14px 0 6px}}
  #panel .lbl {{color:#666; font-size:12px}}
  #panel table {{width:100%; border-collapse:collapse}}
  #panel td {{padding:4px 2px; vertical-align:top}}
  #panel .num {{text-align:right; font-variant-numeric:tabular-nums}}
  #panel tr.zoom {{cursor:pointer}} #panel tr.zoom:hover {{background:#f3f3f3}}
  #panel .ramp {{height:12px; border-radius:3px; background:linear-gradient(90deg, {ramp})}}
  #hide {{position:absolute; top:10px; right:10px; border:1px solid #ccc; background:#fff; border-radius:4px; cursor:pointer}}
  #show {{position:fixed; top:12px; right:12px; z-index:9999; display:none; padding:8px 12px; border:1px solid #ccc;
         background:#fff; border-radius:6px; cursor:pointer; font:13px Arial, sans-serif}}
</style>
<button id="show" onclick="document.getElementById('panel').style.display='block'; this.style.display='none'">Show stats</button>
<div id="panel">
  <button id="hide" onclick="document.getElementById('panel').style.display='none'; document.getElementById('show').style.display='block'">Hide</button>
  <h1>Where Crash-Related Tickets Happen</h1>
  <div class="lbl">Western Suffolk, Jan 2024 to Oct 2026. Hover a road for details. Switch views at the bottom right.</div>
  <h2>At a glance</h2>
  <div><b style="font-size:19px">{n_crash:,}</b> crash-related tickets placed on a road</div>
  <div style="margin-top:4px"><b style="font-size:19px">{overall_rate:.1f}%</b> of all tickets are written at a crash</div>
  <h2>Color scale</h2>
  <div class="ramp"></div>
  <div class="lbl" style="display:flex; justify-content:space-between"><span>Fewer</span><span>More</span></div>
  <h2>Most crash-related tickets (click to zoom)</h2>
  <table>{by_count}</table>
  <h2>Highest crash rate, roads with {MIN_TICKETS}+ tickets</h2>
  <table>{by_rate}</table>
  <div class="lbl" style="margin-top:10px">Crash-related means a ticket written at a crash scene (ACCIDENT = Y), not every crash. Crash rate is the share of a road's tickets written at a crash.</div>
</div>
"""
m.get_root().html.add_child(Element(panel.replace("MAP", m.get_name())))

m.save("crash_map.html")
if hasattr(os, "startfile"):
    os.startfile("crash_map.html")
print("Saved crash_map.html")

# ---------- 9. The numbers behind it ----------
print("\nMost crash-related tickets:")
print(roads_c.sort_values("crashes", ascending=False).head(10)[["road", "town", "crashes", "tickets", "crash_rate"]].to_string(index=False))
print(f"\nHighest crash rate (roads with {MIN_TICKETS}+ tickets):")
print(roads_c[roads_c["tickets"] >= MIN_TICKETS].sort_values("crash_rate", ascending=False).head(10)[["road", "town", "crashes", "tickets", "crash_rate"]].to_string(index=False))
