# Dismal River '26 — Boys Golf Trip

A single-page site for the August 27–30, 2026 golf trip: Denver → Ogallala → Dismal River Club (Mullen, NE) → Denver.

## What's here

- `index.html` — the trip site. No build step, no dependencies to install.
- `red-course.html` / `white-course.html` — the on-course caddies, one per course, eighteen
  holes each. One hole per screen: swipe or arrow-key to flip, tap the tee view for full
  screen, pinch or double-tap to zoom in on a bunker. Par, stroke index and all three tee
  sets sit under the photo, and the tee-shot carries move with whichever tee you pick.
  Every JPEG is baked in as base64, so each is a single file with **zero** network requests
  — 10.7 MB for Red, 11.5 MB for White. Both are generated — see below.

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

### The caddies

Both caddies are **generated** — edit the template, not the output:

```bash
pip install pillow
python build-caddies.py            # both courses
python build-caddies.py white      # just one
```

`red-course.html` comes from `red-course.template.html`, `white-course.html` from
`white-course.template.html`. The two templates are the same file bar the palette accent, the
tee names and the hole data, so a UX change to one should be made to the other.

The script encodes `Course Images/<Course>/*.png` as base64 JPEGs and drops them
into the template's `/*__PHOTOS__*/` marker, with their pixel dimensions going separately into
`/*__SIZES__*/` near the top of the script. It **upscales with Lanczos and applies an unsharp
mask first** — see `TARGET_WIDTH` / `MAX_UPSCALE` / `SHARPEN_*`. The originals are small and
soft (851 to 1337 px wide), so at native size a phone renders them at roughly 1:1 and every
soft pixel shows, while a desktop downsamples 2x and hides it. That's why they looked fine on
one and muddy on the other. Upscaling here rather than letting the browser's bilinear filter
do it when you pinch is a visible improvement, and it costs only file size (~600 KB per hole
at quality 78, ~11 MB per page).

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
`{ blue, white, red }` on the Red card and `{ back, mid, fwd }` on the White one, because the
two courses name their tees differently. (The Red Course's forward tee really is called "Red";
that's the card's naming, not a typo.)

Per-hole par, stroke index and yardages are transcribed from the Red scorecard PDF and
cross-checked against every printed subtotal: OUT (3,547 / 3,264 / 2,503), IN (3,447 / 2,988 /
2,335), TOT (6,994 / 6,252 / 4,838), the alternate Blue set (3,350 IN / 6,897 TOT), par
36 / 35 / 71, and stroke indexes 1–18 each appearing exactly once. All twelve checks pass, and
the test asserts them against the rendered DOM rather than the source array.

### Distances move with the tee

Every distance in the notes was paced from the middle tee of each course — **White** on the
Red Course, **Middle** on the White Course — so that set is the reference and its cards read
exactly as written. Pick Blue or Red and the tee-shot carries shift by the
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

**When the notes weren't paced from a yardage on the card**, the hole says so. `noteFrom`
overrides the baseline and `caveat` prints the reason under the tee note. Hole 15 is the one
that needs it: the club card has it at 271 off White, GS Pro plays it 318, and the notes were
paced in GS Pro. Its badge reads `−47 yds from 318` rather than naming a tee, and every tee on
that hole shifts from 318 instead of 271. Add the same two fields to any other hole where GS
Pro and the card disagree.

The shift assumes the tee boxes sit back along the same line. That's the usual case but it
isn't a survey: on a dogleg where the back tee is offset, or where the card's yardage follows
a bend the tee shot doesn't, the derived carry will be a yard or three off. Treat White as
gospel and the others as a good working estimate — which is what the dotted underline is
there to say.

Each card has a tee set with **two configurations**. On the Red card it's Blue, 6,994 and
6,897; on the White card it's Back, 7,398 and 7,275, differing on holes **2 (510/455),
7 (475/437) and 16 (430/400)**. Both numbers show, smaller below, and the longer rated set
drives the carry adjustment.

The Red card's Blue tee, 6,994 and 6,897 yards, differing only on
differs on holes **13 (496/480), 17 (454/410) and 18 (447/410)** — 97 yards across the three.

Only the current hole and the one either side of it hold a decoded photo at a time; the rest
have their `src` dropped. At around 2600x1600 each decoded frame is ~17 MB, so this matters —
eighteen at once would be over 300 MB.

## External dependencies (loaded from CDN, needs internet)

`index.html` only:

- [Leaflet 1.9.4](https://leafletjs.com/) + CARTO basemap tiles for the route map
- Google Fonts: Instrument Serif, Inter

If the map can't load, the page falls back to a plain text route summary.

`red-course.html` and `white-course.html` have **no external dependencies at all** — that's
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
