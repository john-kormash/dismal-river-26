# Dismal River '26 — Boys Golf Trip

A single-page site for the August 27–30, 2026 golf trip: Denver → Ogallala → Dismal River Club (Mullen, NE) → Denver.

## What's here

- `index.html` — the trip site. No build step, no dependencies to install.
- `white-course.html` — the on-course yardage book for the White Course. One hole
  per screen, swipe or arrow-key to flip. **Fully self-contained** — no fonts, scripts
  or tiles from any CDN, so it still works once you're north of Ogallala with no bars.
- `red-course.html` — the virtual caddy for the Red Course, front nine. Same idea, plus
  the tee view for every hole: tap the photo for full screen, pinch or double-tap to zoom
  in on a bunker. The nine JPEGs are baked into the file as base64, so it is one 5.7 MB
  file with **zero** network requests. Generated — see below.

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

### The Red Course caddy

`red-course.html` is **generated** — edit `red-course.template.html` and rebuild:

```bash
pip install pillow
python build-red-course.py
```

The script encodes `Course Images/Red/DismalRed_1..9.png` as base64 JPEGs and drops them
into the template's `/*__PHOTOS__*/` marker. It **upscales them 2x with Lanczos and applies
an unsharp mask first** — see `UPSCALE` / `SHARPEN_*` in the script. The originals are only
1337x827 and soft, so at native size a phone renders them at roughly 1:1 and every soft pixel
shows, while a desktop downsamples 2x and hides it. That's why they looked fine on one and
muddy on the other. Upscaling here rather than letting the browser's bilinear filter do it
when you pinch is a visible improvement, and it costs only file size (~640 KB per hole at
quality 78, ~5.7 MB for the page). If you ever get higher-resolution renders, set `UPSCALE = 1`
and drop `SHARPEN_PERCENT` toward 0 — sharp input doesn't want any of this.

The notes live
in the `HOLES` array near the top of the template's `<script>`; everything below the
PHOTOS banner is machine-written. Fields match the White book's `HOLES` — `par`, `hcp`,
`y`, `tee`, `app`, `grn`, `keys`, `tags`, `slope` — except that `y` is keyed
`{ blue, white, red }`, since the Red card names its tees Blue / White / Red. (The forward
tee really is called "Red" on the Red Course; that's the card's naming, not a typo.)

Per-hole par, stroke index and yardages are transcribed from the Red scorecard PDF and
cross-checked against every printed subtotal: OUT for all three tee sets (3,547 / 3,264 /
2,503), par 36, and stroke indexes 2–18 even each appearing once. All five checks pass, and
the test asserts them against the rendered DOM rather than the source array.

Worth knowing if you ever extend this to the back nine: the Red card's **Blue tee has two
configurations**, 6,994 and 6,897 yards, differing only on holes **13 (496/480), 17 (454/410)
and 18 (447/410)** — 97 yards across the three. The front nine is identical in both, so the
caddy is unaffected. The site quotes 6,994, which is the longer one.

Only the current hole and the one either side of it hold a decoded photo at a time; the rest
have their `src` dropped. At 2674x1654 each decoded frame is ~18 MB, so this matters — nine
at once would be ~160 MB.

### The White Course book

The yardage book is driven by one array — `HOLES` in the `<script>` of `white-course.html`.
Each entry is a hole:

| Field | What it does |
|---|---|
| `par` / `hcp` | Par and stroke index, from the scorecard. On a par 3 the empty Approach block explains itself instead of saying "no notes". |
| `y` | Yardages per tee — `{ back, mid, fwd }`. An array (holes 2, 7, 16) renders both back tee boxes. |
| `tee` / `app` / `grn` | The three note blocks. An empty string renders a quiet "No notes" panel. |
| `keys` | Yardage chips at the top of the card — `{ v: "260", l: "widest fairway" }` |
| `tags` | Pills under the green notes (Punchbowl, Backstop, False front…) |
| `slope` | Draws the green diagram. `deg` is the fall line: `0` left→right, `90` front→back, `180` right→left, `270` back→front. `strong: true` thickens the arrow. `null` hides the diagram. |

## External dependencies (loaded from CDN, needs internet)

`index.html` only:

- [Leaflet 1.9.4](https://leafletjs.com/) + CARTO basemap tiles for the route map
- Google Fonts: Instrument Serif, Inter

If the map can't load, the page falls back to a plain text route summary.

`white-course.html` and `red-course.html` have **no external dependencies at all** — that's
deliberate, since they're the pages you actually open in the middle of the Sandhills. They use
the same visual system as the trip site but resolve the typefaces from the system stack instead
of Google Fonts. Open them once on the drive up and they stay cached; add them to your home
screen and they open full-screen. Each remembers the last hole you looked at and its light/dark
choice, and `#h7` in the URL jumps to a hole.

## Tee rating / slope sources

Yardages and tee names for Dismal River come from the club's own scorecards
([Red](https://dismalriver.com/wp-content/uploads/2026/03/Dismal-River-Club-Red-Scorecard.pdf),
[White](https://dismalriver.com/wp-content/uploads/2026/03/Dismal-River-Club-White-Scorecard.pdf)).
Note the two courses name their tees differently: the **Red Course** uses Blue / White / Red,
while the **White Course** uses Back / Middle / Forward.

The scorecards don't print course rating or slope, so those come from the
[Nebraska Golf Association course directory](https://www.nebgolf.org/course-directory/dismal-river-club/).
Crandall Creek's Blue and White figures come from its published scorecard data.

The White Course's back tee has two configurations — 7,398 and 7,275 yards, differing on holes
**2 (510/455), 7 (475/437) and 16 (430/400)** — 123 yards across the three. The site shows the
longer one, which is what the NGA rated; the yardage book shows both.

Per-hole par, handicap and yardages in `white-course.html` are transcribed from the White
scorecard PDF and cross-checked against every printed subtotal (OUT/IN/TOT for all four tee
configurations, plus par 36/36/72 and stroke indexes 1–18 each appearing once). All 15 checks pass.

## Trip reference

- [Dismal River Club](https://dismalriver.com/) — 83040 Dismal River Trail, Mullen, NE 69152
- [Hampton Inn Ogallala](https://www.hilton.com/en/hotels/ogapehx-hampton-ogallala/) — 502 Oregon Trail Dr, Ogallala, NE 69153 · (308) 284-7140
- [Crandall Creek Golf Club](https://www.crandallcreekgolfclub.com/) — 359 Road East 85, Ogallala, NE 69153
