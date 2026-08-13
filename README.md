# Dismal River '26 — Boys Golf Trip

A single-page site for the August 27–30, 2026 golf trip: Denver → Ogallala → Dismal River Club (Mullen, NE) → Denver.

## What's here

- `index.html` — the entire site. No build step, no dependencies to install.

## Run it locally

Double-click `index.html`, or serve it:

```bash
python -m http.server 8000
# then open http://localhost:8000
```

## Deploy to GitHub Pages

```bash
git init
git add .
git commit -m "Dismal River '26 trip site"
git branch -M main
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
```

Then in the repo: **Settings → Pages → Source: Deploy from a branch → `main` / `root`**.
The site goes live at `https://<you>.github.io/<repo>/`.

## Editing the content

Everything is in `index.html`:

| What | Where |
|---|---|
| Countdown target | `DEPART` / `END` constants in the `<script>` |
| Itinerary days | `<section id="itinerary">` — one `<article class="day">` per day |
| Tee times | `.tee-slot` blocks inside each day |
| Map stops & route | `STOPS` and `ROUTE` arrays in the `<script>` |
| Courses + tee ratings | `<section id="courses">` — each `<table class="tees">` |
| Lodging | `<section id="stay">` |
| Roster | `<section id="roster">` |
| Trip notes | `<section id="info">` |

## External dependencies (loaded from CDN, needs internet)

- [Leaflet 1.9.4](https://leafletjs.com/) + CARTO basemap tiles for the route map
- Google Fonts: Instrument Serif, Inter

If the map can't load, the page falls back to a plain text route summary.

## Tee rating / slope sources

Yardages and tee names for Dismal River come from the club's own scorecards
([Red](https://dismalriver.com/wp-content/uploads/2026/03/Dismal-River-Club-Red-Scorecard.pdf),
[White](https://dismalriver.com/wp-content/uploads/2026/03/Dismal-River-Club-White-Scorecard.pdf)).
Note the two courses name their tees differently: the **Red Course** uses Blue / White / Red,
while the **White Course** uses Back / Middle / Forward.

The scorecards don't print course rating or slope, so those come from the
[Nebraska Golf Association course directory](https://www.nebgolf.org/course-directory/dismal-river-club/).
Crandall Creek's Blue and White figures come from its published scorecard data.

The White Course's back tee has two configurations — 7,398 and 7,275 yards, differing on holes 2 and 7.
The site shows the longer one, which is what the NGA rated.

## Trip reference

- [Dismal River Club](https://dismalriver.com/) — 83040 Dismal River Trail, Mullen, NE 69152
- [Hampton Inn Ogallala](https://www.hilton.com/en/hotels/ogapehx-hampton-ogallala/) — 502 Oregon Trail Dr, Ogallala, NE 69153 · (308) 284-7140
- [Crandall Creek Golf Club](https://www.crandallcreekgolfclub.com/) — 359 Road East 85, Ogallala, NE 69153
