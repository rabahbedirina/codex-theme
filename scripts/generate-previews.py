#!/usr/bin/env python3
"""Render preview images (assets/*.png) for every Codex theme.

These are rendered mockups built from each theme's real colour values
(not screenshots). Requires: pip install playwright && playwright install chromium
"""
import json, re, html, pathlib, base64
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"; OUT.mkdir(exist_ok=True)
THEMES = [
    ("carbon", "Codex Carbon", "Deep carbon gray with a teal accent"),
    ("anthracite", "Codex Anthracite", "Lighter neutral gray with a blue accent"),
    ("slate", "Codex Slate", "Cool blue-gray with a sky-blue accent"),
    ("graphite", "Codex Graphite", "Warm graphite with an amber accent"),
    ("forest", "Codex Forest", "Green-tinted dark with a green accent"),
    ("carbon-high-contrast", "Codex Carbon High Contrast", "Maximum contrast with bright borders"),
]

def b64(path): return base64.b64encode(open(path,"rb").read()).decode()

def load(slug): return json.load(open(ROOT / f"themes/codex-{slug}-color-theme.json"))

def tok(theme, scope, default="#cccccc"):
    for r in theme["tokenColors"]:
        sc = r["scope"] if isinstance(r["scope"], list) else [r["scope"]]
        if scope in sc: return r["settings"].get("foreground", default)
    return default

CODE = [
 "«kw|import» «var|express» «kw|from» «str|\"express\"»;",
 "«kw|import» { «var|loadTheme» } «kw|from» «str|\"./themes\"»;",
 "",
 "«cm|// Codex: clean, sleek, easy on the eyes»",
 "«kw|const» «var|PORT» «op|=» «num|3000»;",
 "",
 "«kw|class» «type|ThemeServer» «kw|extends» «type|EventEmitter» {",
 "  «fn|constructor»(«param|name», «param|opts» «op|=» {}) {",
 "    «fn|super»();",
 "    «this|this».«prop|name» «op|=» «param|name»;",
 "    «this|this».«prop|accent» «op|=» «param|opts».«prop|accent» «op|??» «str|\"@ACCENT@\"»;",
 "  }",
 "",
 "  «kw|async» «fn|start»() {",
 "    «kw|const» «var|app» «op|=» «fn|express»();",
 "    «var|app».«fn|get»(«str|\"/theme/:id\"», «kw|async» (<param|req>, <param|res>) «kw|=>» {",
 "      «kw|const» «var|theme» «op|=» «kw|await» «fn|loadTheme»(«param|req».«prop|params».«prop|id»);",
 "      «kw|if» («op|!»«var|theme») «kw|return» «param|res».«fn|status»(«num|404»).«fn|json»({ «prop|error»: «str|\"Not found\"» });",
 "      «param|res».«fn|json»({ «prop|name»: «var|theme».«prop|name», «prop|colors»: «num|42» });",
 "    });",
 "    «var|app».«fn|listen»(«var|PORT», () «kw|=>» «var|console».«fn|log»(«str|`Listening on ${PORT}`»));",
 "  }",
 "}",
]
CODE = [l.replace("<param|", "«param|").replace(">,", "»,").replace(">)", "»)") for l in CODE]

def render_code(theme, accent):
    c = {
      "kw": tok(theme,"keyword"), "op": tok(theme,"keyword.operator"), "str": tok(theme,"string"),
      "num": tok(theme,"constant.numeric"), "fn": tok(theme,"entity.name.function"),
      "type": tok(theme,"entity.name.type"), "var": tok(theme,"variable"),
      "param": tok(theme,"variable.parameter"), "this": tok(theme,"variable.language"),
      "prop": tok(theme,"variable.other.property"), "cm": tok(theme,"comment"),
    }
    pn = tok(theme, "punctuation")
    rows = []
    for i, line in enumerate(CODE, 1):
        line = line.replace("@ACCENT@", accent)
        out, pos = "", 0
        for m in re.finditer(r"«(\w+)\|([^»]*)»", line):
            out += f'<span style="color:{pn}">{html.escape(line[pos:m.start()])}</span>'
            cls, txt = m.group(1), html.escape(m.group(2))
            style = f"color:{c[cls]}" + (";font-style:italic" if cls in ("cm","param","this") else "")
            extra = ""
            if cls == "fn" and txt == "loadTheme" and i == 17:
                extra = f";background:{theme['colors']['editor.selectionBackground']}"
            out += f'<span style="{style}{extra}">{txt}</span>'
            pos = m.end()
        out += f'<span style="color:{pn}">{html.escape(line[pos:])}</span>'
        cur = " cur" if i == 11 else ""
        rows.append(f'<div class="ln{cur}"><span class="num">{i}</span><span class="code">{out or "&nbsp;"}</span></div>')
    return "\n".join(rows)

ICONS = {
 "files": '<path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4"/>',
 "search": '<circle cx="11" cy="11" r="6"/><path d="M16 16l5 5"/>',
 "git": '<circle cx="7" cy="6" r="2"/><circle cx="7" cy="18" r="2"/><circle cx="17" cy="9" r="2"/><path d="M7 8v8M17 11c0 4-10 2-10 5"/>',
 "run": '<path d="M7 4l12 8-12 8z"/>',
 "ext": '<rect x="4" y="4" width="7" height="7"/><rect x="13" y="4" width="7" height="7"/><rect x="4" y="13" width="7" height="7"/><rect x="13" y="13" width="7" height="7"/>',
}

def window_html(slug, name):
    t = load(slug); C = t["colors"]
    accent = C["button.background"]
    g = lambda k, d="#000": C.get(k, d)
    term = lambda k: g(k)
    icons = "".join(
        f'<div class="ab{" on" if i==0 else ""}"><svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round">{ICONS[n]}</svg></div>'
        for i, n in enumerate(["files","search","git","run","ext"]))
    tree = [("▾","server","dir",0),("","server.js","file",1),("","theme.js","file",1),("▸","themes","dir",0),("","package.json","file",0),("","README.md","file",0),("","LICENSE","file",0)]
    tree_html = ""
    for arrow, nm, kind, depth in tree:
        sel = " sel" if nm == "server.js" else ""
        tree_html += f'<div class="tr{sel}" style="padding-left:{14+depth*16}px"><span class="ar">{arrow or "&nbsp;"}</span>{nm}</div>'
    return f"""
<div class="win" style="--bg:{g('editor.background')};--fg:{g('editor.foreground')};--side:{g('sideBar.background')};--sidefg:{g('sideBar.foreground')};
--act:{g('activityBar.background')};--actfg:{g('activityBar.foreground')};--actin:{g('activityBar.inactiveForeground')};--accent:{g('activityBar.activeBorder')};
--bord:{g('sideBar.border')};--tabsbg:{g('editorGroupHeader.tabsBackground')};--tabact:{g('tab.activeBackground')};--tabin:{g('tab.inactiveBackground')};
--tabinfg:{g('tab.inactiveForeground')};--tabactfg:{g('tab.activeForeground')};--tabtop:{g('tab.activeBorderTop')};--status:{g('statusBar.background')};
--statusfg:{g('statusBar.foreground')};--title:{g('titleBar.activeBackground')};--titlefg:{g('titleBar.activeForeground')};--panel:{g('terminal.background')};
--ln:{g('editorLineNumber.foreground')};--lnact:{g('editorLineNumber.activeForeground')};--hl:{g('editor.lineHighlightBackground','#ffffff08')};
--sel:{g('list.activeSelectionBackground')};--hover:{g('list.hoverBackground')};--badge:{g('activityBarBadge.background')};--badgefg:{g('activityBarBadge.foreground')};
--cursor:{g('editorCursor.foreground')};--hcb:{g('contrastBorder','transparent')};">
  <div class="title"><span class="dots"><i></i><i></i><i></i></span><span class="tt">server.js — codex-theme</span></div>
  <div class="main">
    <div class="actbar">{icons}<div class="badge">3</div></div>
    <div class="side"><div class="sh">EXPLORER</div><div class="sh2">▾ CODEX-THEME</div>{tree_html}</div>
    <div class="editor">
      <div class="tabs"><div class="tab on">server.js</div><div class="tab">theme.js</div><div class="tab">package.json</div></div>
      <div class="codearea">{render_code(t, accent)}</div>
      <div class="panel"><div class="ph"><span class="on">TERMINAL</span><span>PROBLEMS</span><span>OUTPUT</span></div>
        <div class="tl"><span style="color:{term('terminal.ansiGreen')}">➜</span> <span style="color:{term('terminal.ansiCyan')}">codex-theme</span> <span style="color:{term('terminal.ansiYellow')}">git:(main)</span> npm run dev</div>
        <div class="tl"><span style="color:{term('terminal.ansiGreen')}">✔</span> Server ready on <span style="color:{term('terminal.ansiBlue')};text-decoration:underline">http://localhost:3000</span></div>
        <div class="tl"><span style="color:{term('terminal.ansiYellow')}">⚠</span> Theme cache is stale <span style="color:{term('terminal.ansiMagenta')}">(rebuilding)</span></div>
        <div class="tl"><span style="color:{term('terminal.ansiRed')}">✖</span> GET /theme/unknown <span style="color:{term('terminal.ansiRed')}">404</span></div>
      </div>
    </div>
  </div>
  <div class="status"><span>⎇ main</span><span>⊗ 0 &nbsp;⚠ 0</span><span class="sp"></span><span>Ln 11, Col 14</span><span>Spaces: 2</span><span>UTF-8</span><span>JavaScript</span><span>{name}</span></div>
</div>"""

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0b0c0d;font-family:'DejaVu Sans',Segoe UI,Arial,sans-serif}
.win{width:1280px;height:780px;display:flex;flex-direction:column;background:var(--bg);color:var(--fg);border:1px solid var(--hcb);overflow:hidden}
.title{height:32px;background:var(--title);color:var(--titlefg);display:flex;align-items:center;border-bottom:1px solid var(--bord);font-size:12px;position:relative}
.dots{display:flex;gap:8px;margin-left:14px}.dots i{width:12px;height:12px;border-radius:50%;background:var(--actin);opacity:.55}
.tt{position:absolute;left:0;right:0;text-align:center}
.main{flex:1;display:flex;min-height:0}
.actbar{width:52px;background:var(--act);border-right:1px solid var(--bord);display:flex;flex-direction:column;align-items:center;padding-top:6px;position:relative}
.ab{width:52px;height:50px;display:flex;align-items:center;justify-content:center;color:var(--actin)}
.ab.on{color:var(--actfg);box-shadow:inset 2px 0 0 var(--accent)}
.badge{position:absolute;left:30px;top:6px;background:var(--badge);color:var(--badgefg);font-size:10px;font-weight:700;border-radius:9px;min-width:16px;height:16px;display:flex;align-items:center;justify-content:center}
.side{width:230px;background:var(--side);color:var(--sidefg);border-right:1px solid var(--bord);font-size:13px;padding-top:8px}
.sh{font-size:11px;letter-spacing:.5px;padding:6px 14px 10px}
.sh2{font-size:11px;font-weight:700;padding:5px 12px;color:var(--fg);border-top:1px solid var(--bord)}
.tr{height:24px;display:flex;align-items:center}.tr .ar{width:14px;font-size:10px;margin-right:4px}
.tr.sel{background:var(--sel);color:#fff}
.editor{flex:1;display:flex;flex-direction:column;min-width:0}
.tabs{height:36px;background:var(--tabsbg);display:flex;border-bottom:1px solid var(--bord)}
.tab{padding:0 18px;display:flex;align-items:center;font-size:13px;background:var(--tabin);color:var(--tabinfg);border-right:1px solid var(--bord)}
.tab.on{background:var(--tabact);color:var(--tabactfg);box-shadow:inset 0 2px 0 var(--tabtop)}
.codearea{flex:1;padding-top:8px;font-family:'DejaVu Sans Mono',Consolas,monospace;font-size:13.5px;overflow:hidden}
.ln{height:22px;display:flex;align-items:center;white-space:pre}
.ln.cur{background:var(--hl)}
.num{width:56px;text-align:right;padding-right:22px;color:var(--ln)}.ln.cur .num{color:var(--lnact)}
.panel{height:132px;background:var(--panel);border-top:1px solid var(--bord);font-family:'DejaVu Sans Mono',monospace;font-size:12.5px;padding:0 0 6px}
.ph{display:flex;gap:22px;font-family:'DejaVu Sans',Arial,sans-serif;font-size:11px;padding:8px 16px 6px;color:var(--tabinfg)}
.ph .on{color:var(--tabactfg);box-shadow:0 2px 0 var(--tabtop);padding-bottom:3px}
.tl{padding:2px 16px;line-height:18px}
.status{height:24px;background:var(--status);color:var(--statusfg);border-top:1px solid var(--bord);display:flex;align-items:center;gap:18px;padding:0 14px;font-size:12px}
.status .sp{flex:1}
"""

def page(body, w=1280, h=780, extra=""):
    return f"<html><head><meta charset='utf-8'><style>{CSS}{extra}</style></head><body style='width:{w}px;height:{h}px'>{body}</body></html>"

def palette_row(slug, name, desc):
    t = load(slug); C = t["colors"]
    sw = [("Editor", C["editor.background"]), ("Sidebar", C["sideBar.background"]), ("Activity", C["activityBar.background"]),
          ("Accent", C["button.background"]), ("Keyword", tok(t,"keyword")), ("String", tok(t,"string")),
          ("Function", tok(t,"entity.name.function")), ("Type", tok(t,"entity.name.type")), ("Number", tok(t,"constant.numeric"))]
    dots = "".join(f'<div class="sw"><i style="background:{c}"></i><b>{n}</b><u>{c.upper()}</u></div>' for n, c in sw)
    return f'<div class="prow"><div class="pn"><h3>{name}</h3><p>{desc}</p></div><div class="sws">{dots}</div></div>'

def main():
    with sync_playwright() as p:
        b = p.chromium.launch(); 
        # 1) per-theme previews
        pg = b.new_page(viewport={"width":1280,"height":780}, device_scale_factor=1.5)
        for slug, name, _ in THEMES:
            pg.set_content(page(window_html(slug, name))); pg.wait_for_timeout(150)
            pg.screenshot(path=str(OUT / f"preview-{slug}.png")); print("preview", slug)
        # 2) cover
        cards = "".join(f'<div class="card"><img src="data:image/png;base64,{b64(OUT / f'preview-{s}.png')}"><div class="cap"><i style="background:{load(s)["colors"]["button.background"]}"></i>{n}</div></div>' for s, n, _ in THEMES)
        cover_css = """body{background:radial-gradient(1200px 500px at 50% -10%,#23272b,#0b0c0d)}
        .wrap{width:1800px;padding:56px 60px;text-align:center;color:#e4e6ea}
        h1{font-family:'DejaVu Sans',Arial,sans-serif;font-weight:700;font-size:92px;letter-spacing:-2px}h1 span{color:#5ec4d4}
        .sub{font-family:'DejaVu Sans',Arial,sans-serif;font-size:26px;color:#9aa0a8;margin:6px 0 40px}
        .grid{display:grid;grid-template-columns:repeat(3,1fr);gap:34px}
        .card img{width:100%;border-radius:12px;border:1px solid #2a2c2f;box-shadow:0 18px 40px #000a;display:block}
        .cap{font-family:'DejaVu Sans',Arial,sans-serif;margin-top:14px;font-size:22px;color:#c5c8cd;display:flex;align-items:center;justify-content:center;gap:10px}
        .cap i{width:14px;height:14px;border-radius:50%;display:inline-block}"""
        pg2 = b.new_page(viewport={"width":1800,"height":1100}, device_scale_factor=1)
        pg2.set_content(f"<html><head><meta charset='utf-8'><style>{cover_css}</style></head><body><div class='wrap'><h1>Codex<span>.</span></h1><div class='sub'>Six carbon-gray dark themes for Visual Studio Code</div><div class='grid'>{cards}</div></div></body></html>")
        pg2.wait_for_timeout(500)
        pg2.screenshot(path=str(OUT/"cover.png"), full_page=True); print("cover")
        # 3) palettes
        pcss = """body{background:#0f1011;color:#e4e6ea;font-family:'DejaVu Sans',Arial,sans-serif}.w{width:1700px;padding:44px 50px}
        h2{font-size:38px;margin-bottom:26px}.prow{display:flex;gap:30px;align-items:center;padding:18px 0;border-top:1px solid #26282b}
        .pn{width:330px}.pn h3{font-size:24px}.pn p{color:#8a8f98;font-size:15px;margin-top:4px}
        .sws{display:flex;gap:18px}.sw{width:112px;text-align:center}.sw i{display:block;width:64px;height:64px;border-radius:50%;margin:0 auto 8px;border:2px solid #ffffff22}
        .sw b{display:block;font-size:13px;font-weight:600;color:#c5c8cd}.sw u{text-decoration:none;font-size:12px;color:#7f858d;font-family:'DejaVu Sans Mono',monospace}"""
        rows = "".join(palette_row(*t) for t in THEMES)
        pg3 = b.new_page(viewport={"width":1800,"height":900}, device_scale_factor=1)
        pg3.set_content(f"<html><head><meta charset='utf-8'><style>{pcss}</style></head><body><div class='w'><h2>Codex colour palettes</h2>{rows}</div></body></html>")
        pg3.screenshot(path=str(OUT/"palettes.png"), full_page=True); print("palettes")
        b.close()

if __name__ == "__main__":
    main()
