#!/usr/bin/env python3
"""Generate Codex colour variants from the base Codex Carbon theme."""
import json, re, colorsys

BASE = "themes/codex-carbon-color-theme.json"
base = json.load(open(BASE))

# Surfaces & borders in the base theme (remapped per variant)
SURFACES = ["#101112","#131415","#141516","#151617","#171819","#1b1c1e","#1f2022",
            "#2a2c2f","#2f3236","#34373b"]
BASE_ACCENT = "#4fb8c9"

def hex2rgb(h): return tuple(int(h[i:i+2],16) for i in (1,3,5))
def rgb2hex(c): return "#%02x%02x%02x" % tuple(max(0,min(255,round(v))) for v in c)
def lighten(h, amt):
    r,g,b = hex2rgb(h)
    return rgb2hex((r+(255-r)*amt, g+(255-g)*amt, b+(255-b)*amt))

VARIANTS = {
  "anthracite": dict(label="Codex Anthracite", lift=9,  tint=(0,0,0),   accent="#6c9bf0"),
  "slate":      dict(label="Codex Slate",      lift=2,  tint=(-2,2,9),  accent="#58a6e8"),
  "graphite":   dict(label="Codex Graphite",   lift=1,  tint=(6,2,-4),  accent="#e0a458"),
  "forest":     dict(label="Codex Forest",     lift=0,  tint=(-3,6,-1), accent="#7fcf8a"),
}

def remap(theme, mapping, accent_only_in_colors):
    text = json.dumps(theme)
    def sub(m):
        token = m.group(0); core = token[:7].lower(); rest = token[7:]
        return mapping.get(core, core) + rest
    colors = re.sub(r"#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?", sub, json.dumps(theme["colors"]))
    out = dict(theme); out["colors"] = json.loads(colors)
    return out

def build(slug, p):
    m = {}
    for s in SURFACES:
        r,g,b = hex2rgb(s)
        m[s] = rgb2hex((r+p["lift"]+p["tint"][0], g+p["lift"]+p["tint"][1], b+p["lift"]+p["tint"][2]))
    a = p["accent"]
    m[BASE_ACCENT] = a
    m["#69c7d6"] = lighten(a, .15)
    m["#5ec4d4"] = lighten(a, .08)   # link / highlight colours (colors only)
    m["#8fdbe6"] = lighten(a, .40)
    t = remap(base, m, True)
    t["name"] = p["label"]
    return t

def build_hc():
    m = {
      "#101112":"#000000","#131415":"#050506","#141516":"#08090a","#151617":"#0a0b0c",
      "#171819":"#0c0d0e","#1b1c1e":"#0f1011","#1f2022":"#141516",
      "#2a2c2f":"#6b7078","#2f3236":"#80868e","#34373b":"#80868e",
      "#c5c8cd":"#f0f2f5","#e4e6ea":"#ffffff","#a7acb4":"#d6d9de","#9aa0a8":"#d0d3d8",
      "#8a8f98":"#b5bac1","#7f858d":"#b5bac1","#6b7078":"#a0a6ad","#666b73":"#a0a6ad",
      "#5ec4d4":"#7fe0ee","#4fb8c9":"#5ed2e4",
    }
    t = remap(base, m, True)
    # comments & dim punctuation stay legible in high contrast
    for rule in t["tokenColors"]:
        s = rule["settings"]
        if s.get("foreground") == "#6b7078": s["foreground"] = "#a0a6ad"
        if s.get("foreground") == "#8a8f98": s["foreground"] = "#b5bac1"
    t["name"] = "Codex Carbon High Contrast"
    t["colors"].update({
      "contrastBorder": "#80868e",
      "contrastActiveBorder": "#5ed2e4",
      "editor.lineHighlightBorder": "#5ed2e455",
      "editor.selectionBackground": "#5ed2e455",
    })
    return t

out = {}
for slug,p in VARIANTS.items():
    out[f"codex-{slug}-color-theme.json"] = (build(slug,p), "vs-dark", p["label"])
out["codex-carbon-high-contrast-color-theme.json"] = (build_hc(), "hc-black", "Codex Carbon High Contrast")

for fn,(theme,ui,label) in out.items():
    json.dump(theme, open(f"themes/{fn}","w"), indent=2); open(f"themes/{fn}","a").write("\n")
    print(fn, ui, label)

# Update package.json
pkg = json.load(open("package.json"))
pkg["version"] = "1.1.0"
pkg["contributes"]["themes"] = [dict(label="Codex Carbon", uiTheme="vs-dark",
                                     path="./themes/codex-carbon-color-theme.json")]
for fn,(theme,ui,label) in out.items():
    pkg["contributes"]["themes"].append(dict(label=label, uiTheme=ui, path=f"./themes/{fn}"))
json.dump(pkg, open("package.json","w"), indent=2); open("package.json","a").write("\n")
