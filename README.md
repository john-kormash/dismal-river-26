# Dismal River '26 — Boys Golf Trip

A single-page site for the August 27–30, 2026 golf trip: Denver → Ogallala → Dismal River Club (Mullen, NE) → Denver.

## What's here

- `index.html` — the trip site. No build step, no dependencies to install.
- `white-course.html` — the on-course yardage book for the White Course. One hole
  per screen, swipe or arrow-key to flip. **Fully self-contained** — no fonts, scripts
  or tiles from any CDN, so it still works once you're north of Ogallala with no bars.
- `red-course.html` — the virtual caddy for the Red Course, all eighteen. Same idea, plus
  the tee view for every hole: tap the photo for full screen, pinch or double-tap to zoom
  in on a bunker. The eighteen JPEGs are baked into the file as base64, so it is one 10.7 MB
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

The script encodes `Course Images/Red/DismalRed_1..18.png` as base64 JPEGs and drops them
into the template's `/*__PHOTOS__*/` marker, with their pixel dimensions going separately into
`/*__SIZES__*/` near the top of the script. It **upscales with Lanczos and applies an unsharp
mask first** — see `TARGET_WIDTH` / `MAX_UPSCALE` / `SHARPEN_*`. The originals are small and
soft (861 to 1337 px wide), so at native size a phone renders them at roughly 1:1 and every
soft pixel shows, while a desktop downsamples 2x and hides it. That's why they looked fine on
one and muddy on the other. Upscaling here rather than letting the browser's bilinear filter
do it when you pinch is a visible improvement, and it costs only file size (~600 KB per hole
at quality 78, ~10.7 MB for the page).

Sources are normalised to `TARGET_WIDTH` rather than multiplied by a fixed factor, because the
back-nine renders are smaller than the front-nine ones and a flat multiplier would leave those
holes visibly softer. `MAX_UPSCALE` caps it at 2.5x, past which Lanczos has nothing left to
work with and the extra pixels are pure weight. The sharpening radius scales with the factor
for the same reason — and because hole 14 carries a hand-drawn red aiming arrow that rings
badly if you over-sharpen it.

The renders are not all the same shape (hole 18 is 2.47:1, hole 13 is 1.49:1), so each card
takes its aspect ratio from its own photo via `SIZES`. With a single hardcoded ratio,
`object-fit: cover` would crop about a third off the wide ones.

If you ever get higher-resolution renders, set `MAX_UPSCALE = 1` and drop `SHARPEN_PERCENT`
toward 0 — sharp input doesn't want any of this.

The notes live
in the `HOLES` array near the top of the template's `<script>`; everything below the
PHOTOS banner is machine-written. Fields match the White book's `HOLES` — `par`, `hcp`,
`y`, `tee`, `app`, `grn`, `keys`, `tags`, `slope` — except that `y` is keyed
`{ blue, white, red }`, since the Red card names its tees Blue / White / Red. (The forward
tee really is called "Red" on the Red Course; that's the card's naming, not a typo.)

Per-hole par, stroke index and yardages are transcribed from the Red scorecard PDF and
cross-checked against every printed subtotal: OUT (3,547 / 3,264 / 2,503), IN (3,447 / 2,988 /
2,335), TOT (6,994 / 6,252 / 4,838), the alternate Blue set (3,350 IN / 6,897 TOT), par
36 / 35 / 71, and stroke indexes 1–18 each appearing exactly once. All twelve checks pass, and
the test asserts them against the rendered DOM rather than the source array.

### Distances move with the tee

Every distance in the notes was paced from the **White** tee, so White is the reference set
and its cards read exactly as written. Pick Blue or Red and the tee-shot carries shift by the
difference in hole length — hole 1 is 535 off Blue and 520 off White, so "220 to clear the
right corner" becomes 235, and the block gets a `+15 yds vs White` badge. Shifted numbers are
marked with a dotted underline so a derived carry never reads as a measured one.

**Only tee-shot carries move.** Approach and green notes are never touched, and inside the
tee note only the numbers wrapped in `{...}` shift. Everything left bare stays put, because
it is anchored to something other than the tee box:

| Left alone | Why |
|---|---|
| "70 yards from the center of the green" (1) | measured from the green |
| "25 yards short of center" (5) | a spot on the ground, true from any tee |
| "8–10 yards separate the visible traps" (8) | gap between two features |
| "~40 yards long of center" (8) | measured from the green |
| "15 yards lower than the tee" (6) | elevation |
| "20 ft hill" (7) | elevation |

So holes 5, 11 and 16 show identical numbers from all three tees, which is correct — they're
par 3s whose notes are written against the green.

The shift assumes the tee boxes sit back along the same line. That's the usual case but it
isn't a survey: on a dogleg where the back tee is offset, or where the card's yardage follows
a bend the tee shot doesn't, the derived carry will be a yard or three off. Treat White as
gospel and the others as a good working estimate — which is what the dotted underline is
there to say.

The Red card's **Blue tee has two configurations**, 6,994 and 6,897 yards, differing only on
holes **13 (496/480), 17 (454/410) and 18 (447/410)** — 97 yards across the three. Those cards
show both numbers, the smaller one below. The longer set is the one the site quotes and the one
the NGA rated, so it is also the one the carry adjustment measures from.

Only the current hole and the one either side of it hold a decoded photo at a time; the rest
have their `src` dropped. At around 2600x1600 each decoded frame is ~17 MB, so this matters —
eighteen at once would be over 300 MB.

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
