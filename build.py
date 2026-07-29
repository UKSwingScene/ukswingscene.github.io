import json, base64, re as _re
from datetime import datetime, date

# Today's date string for filtering past events
TODAY = date.today().strftime('%Y-%m-%d')

# Hardcoded city corrections — applied at build time regardless of source data
CITY_OVERRIDE = {
    "atlantisEVOLUTION":        "Stoke-on-Trent",
    "Chameleons":                "Darlaston",
    "Chunky Muffins":            "Boston, Lincolnshire",
    "Chunkymuffins":             "Boston, Lincolnshire",
    "Club Alchemy":              "Northwich",
    "Club F":                    "Stanley, Co. Durham",
    "Club Ignite":               "West Drayton",
    "Club Play":                 "Blackpool",
    "Cupids":                    "Swinton, Manchester",
    "Decadance":                 "Rochdale",
    "GG's Lounge":              "Runcorn",
    "House of Earthly Delights": "Llandovery",
    "HU9":                       "Hull",
    "Infusion":                  "Blackpool",
    "Jaydee's":                 "St Neots, East Midlands",
    "Jay-Dees":                  "St Neots, East Midlands",
    "Klub Kink":                 "Dudley",
    "Le Boudoir":                "City of London",
    "Liberty Elite":             "West Midlands",
    "Naughty Pineapple":         "Leicester",
    "The Pineapple Club":        "Leicester",
    "New Gatehouse":             "Bolton",
    "No.3 Club":                 "Chorley, Lancashire",
    "Pandoras":                  "Armley, Leeds",
    "Partners":                  "Bury, Manchester",
    "Penthouse Playrooms":       "Dunstable",
    "Penthouse Club":            "Dunstable",
    "Purple Mamba":              "Nottingham",
    "Quest":                     "Leeds",
    "Shhh":                      "Newcastle",
    "Steel Cliffe":              "Sheffield",
    "Swindon SC":                "Swindon",
    "The Attic":                 "Derby",
    "The Playgrounds":           "Staffordshire",
    "Townhouse":                 "Birkenhead",
    "The Townhouse":             "Birkenhead",
    "V2V":                       "Nuneaton, Warwickshire",
    "Within Temptation":         "Torquay",
    "Xtasia":                    "West Bromwich",
}

# Load manually researched events (always present as fallback)
with open('events.json') as f:
    manual = json.load(f)

# Load freshly scraped events
try:
    with open('events_scraped.json') as f:
        scraped = json.load(f)
    print(f"Scraped: {len(scraped)} events")
except:
    scraped = []
    print("No scraped events, using manual only")

def _is_bad(name):
    if not name or len(name) < 6: return True
    n = name.lower()
    bad = ['more info','google calendar','ics','view event','powered by','events list','event list',
           'sat, ','sun, ','mon, ','tue, ','wed, ','thu, ','fri, ',
           'pm sun','am sun','pm sat','am sat','subscribe','follow',
           'sign up','cookie','found','event name','copyright']
    if any(x in n for x in bad): return True
    if _re.match(r'^[\d\s:apm,\-\/\.]+$', n, _re.I): return True
    return False

merged = {}
for e in manual:
    merged[(e['d'], e['club'])] = e
for e in scraped:
    key = (e['d'], e['club'])
    ev = e.get('event', '')
    if key not in merged and not _is_bad(ev):
        merged[key] = e

# Apply hardcoded city corrections
for e in merged.values():
    correct = CITY_OVERRIDE.get(e.get('club', ''))
    if correct:
        e['city'] = correct

# Filter out events where date has already passed
events = sorted(
    [e for e in merged.values() if e.get('d', '') >= TODAY],
    key=lambda x: x['d']
)
print(f"Total merged events (future only): {len(events)}")

with open('gemini_logo.mp4', 'rb') as f:
    vid_b64 = base64.b64encode(f.read()).decode()

video_tag = f'<video src="data:video/mp4;base64,{vid_b64}" autoplay loop muted playsinline style="width:100%;height:100%;object-fit:contain;display:block;"></video>'
updated = datetime.now().strftime("%-d %B %Y")
events_js = json.dumps(events, ensure_ascii=False)

with open('template.html') as f:
    html = f.read()

num_events = len(events)
num_clubs  = len({e['club'] for e in events})
stats_line = f'{num_events} events across {num_clubs} clubs'

html = html.replace('STATS_PLACEHOLDER', stats_line)
html = html.replace('VIDEO_TAG_PLACEHOLDER', video_tag)
html = html.replace('UPDATED_PLACEHOLDER', updated)
html = html.replace('EVENTS_JS_PLACEHOLDER', events_js)

with open('index.html', 'w') as f:
    f.write(html)
print(f"Built index.html — {len(html)//1024}KB")
