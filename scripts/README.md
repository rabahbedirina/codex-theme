# Codex scripts

Helper scripts for building and maintaining the Codex theme extension. They are for development only and are **not** included in the published `.vsix` (see `.vscodeignore`).

| Script | Purpose |
|---|---|
| [`generate-variants.py`](generate-variants.py) | Builds the five variant themes from the base Carbon theme and updates `package.json` |
| [`generate-previews.py`](generate-previews.py) | Renders the preview images used in the main README (`assets/`) |
| [`recolor-icon.py`](recolor-icon.py) | Recolors a PNG icon while keeping its shading and transparency |

## Setup

You need **Python 3.8+**. Run everything from the **project root** (the folder that contains `package.json`), because the scripts use relative paths.

```bash
# optional but recommended: a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r scripts/requirements.txt
playwright install chromium        # only needed for generate-previews.py
```

`generate-variants.py` uses only the standard library, so it needs none of the packages above.

## Typical workflow

```bash
# 1. edit the base theme (themes/codex-carbon-color-theme.json) or the variant settings
python3 scripts/generate-variants.py     # 2. regenerate the variant themes
python3 scripts/generate-previews.py     # 3. re-render the README images
vsce package                             # 4. build the .vsix
```

Always run `generate-variants.py` before `generate-previews.py`, so the images match the current colors.

---

## generate-variants.py

Creates five themes from `themes/codex-carbon-color-theme.json`:

| File | Theme |
|---|---|
| `codex-anthracite-color-theme.json` | Codex Anthracite |
| `codex-slate-color-theme.json` | Codex Slate |
| `codex-graphite-color-theme.json` | Codex Graphite |
| `codex-forest-color-theme.json` | Codex Forest |
| `codex-carbon-high-contrast-color-theme.json` | Codex Carbon High Contrast |

It also rewrites `contributes.themes` in `package.json` so all six themes are registered.

**Run:**
```bash
python3 scripts/generate-variants.py
```

**How it works:** it takes the base theme's surface colors (editor, sidebar, borders...) and shifts them by a brightness `lift` and an RGB `tint`, then swaps the teal accent for the variant's own accent. The syntax colors are shared by all variants. The High Contrast theme uses a hand-written color map and adds `contrastBorder` / `contrastActiveBorder`.

**Customize a variant:** edit the `VARIANTS` dictionary near the top of the script:

```python
"slate": dict(label="Codex Slate", lift=2, tint=(-2, 2, 9), accent="#58a6e8"),
```

- `lift`: brightens (+) or darkens (-) every surface by that amount.
- `tint`: extra (R, G, B) shift added to surfaces, for example more blue for a cooler look.
- `accent`: the accent color. Lighter shades for hover and links are derived from it automatically.

**Add a new variant:** add an entry to `VARIANTS`, run the script, and it appears in `themes/` and in `package.json`.

> ⚠️ The script sets `"version": "1.1.0"` in `package.json` every time it runs. If you've bumped the version, update that line near the bottom of the script (`pkg["version"] = "1.1.0"`) or fix `package.json` after running.

> ⚠️ The generated variant files are overwritten on every run. Make color changes in the base theme or in this script, not by hand in the variant files.

---

## generate-previews.py

Renders mockup images of VS Code in each theme using the theme's real colors, and saves them to `assets/`:

| Output | Content |
|---|---|
| `assets/preview-<theme>.png` | Full-window mockup for each of the six themes |
| `assets/cover.png` | Cover image with all six previews in a grid |
| `assets/palettes.png` | Color swatches with hex codes for every theme |

**Run:**
```bash
python3 scripts/generate-previews.py
```

These are rendered mockups, **not real screenshots**. Replace them with real screenshots when you have them, using the same file names.

**Customize:**
- `THEMES` (top of the file): the list of themes, with names and descriptions.
- `CODE`: the sample JavaScript shown in the editor. Tokens are written as `«type|text»`, where type is one of `kw`, `op`, `str`, `num`, `fn`, `type`, `var`, `param`, `this`, `prop`, `cm`.
- `CSS` and `window_html()`: layout and sizes of the mockup window.

---

## recolor-icon.py

Changes the color of a PNG icon while keeping its shadows, gradients and transparency. It replaces the hue and scales the saturation, and leaves brightness alone.

**Run:**
```bash
python3 scripts/recolor-icon.py icon.png --color "#39FF14" --out icon-green.png --size 256
```

| Option | Meaning | Default |
|---|---|---|
| `input` | Source PNG | required |
| `--color` | Target color, such as `#39FF14` | `#39FF14` |
| `--out` | Output file | `icon-recolored.png` |
| `--size` | Resize to a square of this size (for example `256`) | keep original size |

**Using it for the extension icon:** save the result as `icon.png` in the project root and add `"icon": "icon.png"` to `package.json`. Use at least 128×128 px; 256×256 looks sharper.

Works best on icons made of one main color with shading. Icons with several different colors will all be changed to the same hue.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Run `pip install -r scripts/requirements.txt` |
| `playwright` can't find a browser | Run `playwright install chromium` |
| `FileNotFoundError: themes/...` | Run the script from the project root, not from inside `scripts/` |
| Preview images use odd fonts | The mockups use DejaVu fonts. Install them, or change the font names in `CSS` |
| Variant themes look unchanged | You edited a variant file by hand and then re-ran the script, or you didn't re-run it after changing the base theme |
