# R6 runtime and narrative figure interface

This file describes the delivered implementation. It is not an assessment of story quality.

## Content and executable files

`content/game.json` is the authored bilingual source. `node tools/build_runtime.mjs` first verifies the frozen mechanics, then creates `play/data.json`, `play/data.js` and `R6_Offline.html`. The standalone HTML embeds data, styles, the original engine and figures, the new caper figure module and the new app. Its gameplay requires no server, login or runtime network request. The print link points to the separately generated `play/print.html`.

`play/engine.js` and `play/figures.js` are byte-identical copies from the verified R3.1 attachment. Their original CommonJS exports remain available. `engine.initial().version` remains `R3.1` because it identifies that frozen state format; it does not select a previous story. The new product version comes from `game.json`.

## Bilingual story fields

All text values below use `{ "zh": "…", "en": "…" }`. A dialogue entry is `{ "speaker": {"zh":"…","en":"…"}, "text": {"zh":"…","en":"…"} }`.

| Field | Display and behavior |
| --- | --- |
| `openingTitle`, `opening` | Opening heading and prose. |
| `fictionNotice` | Explicit notice immediately before the opening illustration. |
| `openingFigure` | Display-only opening illustration, currently `caper_open`. |
| `openingDialogue` | Opening dialogue array. |
| `originalCaption`, `parkAnnotation` | The original clearing instruction and the park annotation remain explicitly visible in the opening work-page panel. They are not hidden inside the rules disclosure. |
| `rules` | Bilingual rules array in an expandable disclosure. |
| `stages[].before`, `after` | Dialogue before the existing puzzle and after successful submission. |
| `stages[].beforeFigure`, `afterFigure` | Display-only illustration before and after the action. No answer field, stamp or prop is added. |
| `stages[].operation` | Current action and its narrative purpose. |
| `choiceLabels`, `choiceResponses` | Text keyed by the original `challenge` / `share` branch values. |
| `finalTitle`, `finalIntro` | Heading and instructions for the original seven-field final submission. |
| `endingLabels`, `ending` | Text keyed by the original `solo` / `joint` ending values. |
| `finale` | Array of scenes with `title`, `text`, optional `dialogue`, `figure`, optional `byChoice` and optional `byEnding`. All correct final submissions reach the complete array. |

Existing fields (`cards`, `fields`, `answer`, `hints`, `success`, `lead`, source IDs and `finalAnswer`) retain their mechanism roles. Figure names do not participate in answer checking.

## Original code-rendered narrative figures

Browser: `window.R6_CAPER` after loading unchanged `figures.js` and then `caper.js`.

Node/CommonJS:

```js
const C = require('../play/caper.js');
const onlySVG = C.svg('caper_open', 'zh', { static: true });
const finalFrame = C.frame(4, 'en', { static: true });
const withCaption = C.render('parkFull', 'en', { static: true });
```

All outer SVG view boxes are `0 0 800 480`. `C.svg` returns one self-contained SVG. `C.frame(n, lang, options)` returns `C.svg('caper' + n, lang, options)` for `n = 0…5`; its default is static. `C.render` returns a figure with an accessible description and caption. The latter includes playback controls only for non-static performance figures. For printing, use the SVG interface with `{static:true}`.

| Figure names | Visible change |
| --- | --- |
| `caper_open` | The original river and actor disappear behind a pale blank back in a narrow viewing window. The static/reduced-motion version shows before and after frames. Its player caption does not reveal the holder's off-window position. |
| `fragments` → `joined` | The same three horizontal scene strips join; occlusion is not treated as missing artwork. |
| `riverWrong` → `riverBoth` | The original river moves from outside a blank substitute frame into the retained scene, with separate stage and real-source labels. |
| `oldClaim` → `modernReference` | The claimed 1930 authority is removed. The same garden reference stays with the limited conclusion “1995 or later.” |
| `parkCrop` → `parkFull` | A mask excludes the playground foreground; the restored version retains it with the sports centre behind. The viewing arrow starts on the playground side. |
| `oldExit` → `lineageJoined` | The same Chitose-za label gains its contemporary counterpart. The 1928 relocation is a separate location line. No real park-to-theatre camera view is implied. |
| `caper0` | Same scene and sheet; the narrow viewing aperture opens to a wide stage. |
| `caper1` | The same lateral sheet movement finishes in the wide frame; holder and footsteps remain visible beside the pale blank sheet back. |
| `caper2` | The performer tries to hide behind the sheet; body edge and shoes remain visible. |
| `caper3` | The old title, contemporary counterpart and separate relocation line remain on stage; there is no blackout. |
| `caper4` | The same sheet comes down and the original scene is fully visible again. Use this for the souvenir back. |
| `caper5` | A complete bow followed by a visible side exit, leaving the scene with the audience. The static version shows the bow and exit direction. |

The original figure names `scene`, `river`, `memorial`, `park` and `facade` remain supported by the app. The original river SVG is reused directly inside opening/finale and scene-recovery diagrams. It is never deleted to create the opening disappearance.

Animated performance figures start when they enter the viewport, avoiding an opening that has already finished before a reader reaches it. The local “Replay this action” control restarts presentation only. Finale Previous/Next/Replay controls do not change puzzle state. `prefers-reduced-motion: reduce` disables movement, retains a meaningful static pose, and replaces the opening motion with explicit before/after frames. All illustrations identify themselves as original staging, not site footage or a venue performance.

## Saves and inherited mechanism behavior

The new localStorage key is `tokyo-five-sites-r6-progress`. Export format is `{ "format": "tokyo-five-sites-progress", "product": "R6.0-review", "state": … }`. An envelope must match the product version. Raw original engine state is also accepted because the frozen mechanism is the same; unknown card IDs and invalid inputs are discarded. Story prose is not part of progress files.

All chapter navigation and the final chapter are available from the beginning. Correct early final answers do not require chapter completion flags. `challenge` / `share` only affects the first initialization of the park diagram; changing strategy afterward does not reset work already begun. `solo` / `joint` is independent. Hints and assistance preserve the complete ending and souvenir. A successful answer edited later loses its stale success display.

## Verification commands

From `r6/`:

```sh
node tools/build_runtime.mjs
node qa/test_logic.mjs
python3 qa/test_runtime.py
python3 qa/test_caper.py
```

Browser checks require Python Playwright and Chromium. `CHROMIUM_PATH` may point to a local Chromium executable. Fontconfig may provide a CJK-capable font; fonts are not fetched at runtime. Contact-sheet generation uses Pillow when available. These development dependencies are not needed to open the shipped standalone HTML.
