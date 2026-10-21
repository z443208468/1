# R7 content and build interface

This document describes software behavior, not a judgement of story quality.

## Editable source

`content/game.json` owns all authored player prose. Every translated value uses
`{"zh":"…","en":"…"}`. Dialogue entries have `speaker` and `text` in that form.
The five stages retain their original `id`, `type`, card IDs, option IDs, answers,
evidence identifiers and three-hint count. `qa/mechanics_contract.json` verifies
these against the recovered R3.1 attachment. The engine and original puzzle
figures remain byte-identical.

Top-level narrative fields: `title`, `subtitle`, `openingTitle`, `opening`,
`openingDialogue`, `fictionNotice`, `rules`, `safety`, `finalTitle`, `finalIntro`,
`paperEnding`. `originalCaption` and `parkAnnotation` are optional authored
opening evidence; no old text is substituted.

Stage narrative fields: `title`, `shortTitle`, `intro`, `prompt`, `before`,
`operation`, `success`, `after`, `lead`, optional `beforeFigure` and `afterFigure`.
`choiceLabels` and `choiceResponses` use `challenge`/`share`; `endingLabels` and
`ending` use `solo`/`joint`. These remain independent variables.

`finale` is a nonempty array with no fixed scene count. Every entry has `title`
and `text`, optional `dialogue`, `figure`, `byChoice`, `byEnding`, `paperAction`.
Paper actions appear only on their own final-scene page. All correct final
accounts, including early solutions and assisted completion, receive every scene.

Optional `paper` fields: `preparation`, `openingInstruction`, `stageActions`
(five translated entries), `finalInstruction`, `souvenirTitle`, `souvenirText`.
These describe the existing materials; they must not introduce a sixth site,
new required component, code, stamp or hidden gate.

## Narrative diagrams

`figures` maps a figure ID to an original diagram specification. Generic forms:

```json
{
  "figure_id": {
    "kind": "board",
    "title": {"zh": "证据的变化", "en": "A change in evidence"},
    "caption": {"zh": "原创示意", "en": "Original diagram"},
    "scene": "river",
    "labels": [{"zh": "一项发现", "en": "A finding"}]
  }
}
```

`scene` selects an unchanged base diagram: `scene`, `river`, `park`, `memorial`,
`facade`. `board` allows up to three translated side labels. `comparison` uses
`left` and `right`, each with `scene`, translated `title` and `text`. `timeline`
uses up to five `items` with `year` (or `label`) and translated `text`.

Browser API: `R7_NARRATIVE.configure(data)`, `svg(id, lang)`, `render(id, lang)`.
Node/CommonJS: `require('./play/narrative.js')`, then `configure(data)`.
Diagrams contain no new answer fields or state changes; they use only local SVG.

## Spoiler boundaries

Digital receipt content is present only after successful final submission and
starts inside a closed disclosure. The user actively opens it. Changing a final
scene rerenders it closed, so reading an earlier scene does not automatically
expose the final receipt. Existing free hints remain explicitly requested.

The paper preparation index does not reproduce the ending or direct preparation
to it. The souvenir is cut and used after the complete ending, not before play.
Three hints occupy their own foldable page; complete answer and consequence are
on another leaf. Midgame choice responses are separate from ending responses.
Printed clues and answer sheets are accessible by page reference, not a hidden
software lock. Players may solve early.

## Building

From `r7/` in a configured Python/Node environment:

```sh
node tools/build_runtime.mjs
python3 tools/build_print.py
python3 qa/audit_content.py
node qa/test_logic.mjs
python3 qa/test_runtime.py
python3 qa/test_narrative.py
python3 tools/build_guide.py
python3 tools/render_pdfs.py --skip-build
```

Or `python3 tools/build_release.py --pdf --browser-test`.

PDF rendering needs local Chromium, Python Playwright, Markdown-It, Pillow,
PyMuPDF and suitable CJK fonts. `CHROMIUM_PATH` and `FONTCONFIG_FILE` may select
local installations. None is downloaded when playing the delivered HTML.
Do not include raw font files in a public repository or release payload.

Generated documents live in `output/pdf/`. Full-page proof renders live under
`output/qa/pdf_pages/`, and each records the SHA-256 of its source PDF and PNG.
After actually reviewing every page, retain the reviewed contact sheets in
`qa/pdf_contacts/`. `qa/PDF_VISUAL_REVIEW.json` must contain `final_documents`
with `path` and `sha256` for all three PDFs, plus `contact_sheets` entries with
`path` and `sha256` for every retained sheet. A stale proof rejects packaging.
No generator automatically declares visual review or story quality complete.

`tools/package_release.py` validates actual extraction of the completed ZIP,
requires current runtime/content/PDF records, and refuses changed input files.
It does not perform a physical print test, tourist blind test or on-site test.
