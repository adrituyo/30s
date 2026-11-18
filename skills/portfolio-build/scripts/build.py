#!/usr/bin/env python3
"""Builds a portfolio from one content file. Standard library only.

Usage:  python3 build.py path/to/portfolio.json [--compare]

Writes index.html (plus one page per project in the "case" layout), assets/styles.css, assets/main.js,
sitemap.xml and robots.txt next to the content file, then lists what the 30-second rules would still flag.
Image paths in the content file are relative to its folder. See references/content.md for every field.

--compare also writes the same content in all three layouts to compare/, with a page that links them, so the
person can choose a grid by looking. That folder is for choosing: delete it before publishing."""
import html, json, os, re, shutil, struct, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(os.path.dirname(HERE), "assets", "template")
LAYOUTS = ("index", "columns", "case")
EMPTY = ["passionate", "multi-disciplinary", "multidisciplinary", "pixel-perfect", "crafting", "creative thinker",
         "storyteller", "problem solver", "user-centric", "delightful", "seamless", "innovative", "detail-oriented"]
VIDEO = (".mp4", ".webm", ".mov")
# The few words the template itself writes. Chosen by site.lang; any of them can be replaced with "labels" in the content file.
LABELS = {
    "en": {"skip": "Skip to work", "about": "About", "index": "Index", "facts": "Facts", "authorship": "About this work", "decision": "Decision",
           "the_decision": "The decision", "result": "What changed", "before": "Before", "after": "After", "personal": "Personal concept",
           "freelance": "Freelance", "read": "Read the case →", "all": "← All work", "next": "Next", "portrait": "Portrait of",
           "role": "Role", "team": "Team", "year": "Year", "for": "For", "close": "Close", "previous": "Previous", "contact": "Contact"},
    "es": {"skip": "Ir al trabajo", "about": "Sobre mí", "index": "Índice", "facts": "Datos", "authorship": "Sobre este trabajo", "decision": "Decisión",
           "the_decision": "La decisión", "result": "Qué cambió", "before": "Antes", "after": "Después", "personal": "Proyecto personal",
           "freelance": "Freelance", "read": "Ver el caso →", "all": "← Todo el trabajo", "next": "Siguiente", "portrait": "Retrato de",
           "role": "Rol", "team": "Equipo", "year": "Año", "for": "Para", "close": "Cerrar", "previous": "Anterior", "contact": "Contacto"},
}
SLOT = re.compile(r"\[[^\[\]]{2,80}\]")
e = lambda s: html.escape(str(s), quote=True)
WARN = []
warn = lambda rule, msg: WARN.append((rule, msg))


def rich(s):
    """Escapes text and turns **words** into emphasis."""
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", e(s))
    return re.sub(r"(?<![\w*])\*([^*\n]+?)\*(?![\w*])", r"<i>\1</i>", s)       # *single* for the title of a work

plain = lambda s: re.sub(r"\*{1,2}([^*]+?)\*{1,2}", r"\1", str(s))


def size_of(path):
    """(width, height) of an image file, read from its first bytes. None if unknown."""
    try:
        with open(path, "rb") as f: b = f.read(400_000)
        if b[:8] == b"\x89PNG\r\n\x1a\n": return struct.unpack(">II", b[16:24])
        if b[:3] == b"GIF": return struct.unpack("<HH", b[6:10])
        if b[:4] == b"RIFF" and b[8:15] == b"WEBPVP8":
            if b[15:16] == b"X": return (int.from_bytes(b[24:27], "little") + 1, int.from_bytes(b[27:30], "little") + 1)
            if b[15:16] == b" ": return tuple(x & 0x3FFF for x in struct.unpack("<HH", b[26:30]))
            if b[15:16] == b"L": n = int.from_bytes(b[21:25], "little"); return ((n & 0x3FFF) + 1, ((n >> 14) & 0x3FFF) + 1)
        if b[4:8] == b"ftyp":                                  # AVIF / HEIF: the size sits in the "ispe" box
            i = b.find(b"ispe")
            if i > 0: return struct.unpack(">II", b[i + 8:i + 16])
        if b[:2] == b"\xff\xd8":
            i = 2
            while i < len(b) - 9:
                if b[i] != 0xFF: i += 1; continue
                m = b[i + 1]
                if m in (0xC0, 0xC1, 0xC2): h, w = struct.unpack(">HH", b[i + 5:i + 9]); return (w, h)
                i += 2 + struct.unpack(">H", b[i + 2:i + 4])[0]
        if b"<svg" in b[:2000]:
            head = b[:2000].decode("utf-8", "replace")
            m = re.search(r'viewBox="[\d.\-]+[ ,]+[\d.\-]+[ ,]+([\d.]+)[ ,]+([\d.]+)"', head)
            if m: return (round(float(m.group(1))), round(float(m.group(2))))
    except Exception: pass
    return None


class Site:
    def __init__(self, path):
        self.root = os.path.dirname(os.path.abspath(path))
        self.d = json.load(open(path, encoding="utf-8"))
        self.layout = self.d.get("layout", "index")
        if self.layout not in LAYOUTS: sys.exit(f'"layout" must be one of: {", ".join(LAYOUTS)}')
        self.person, self.site, self.theme = self.d.get("person", {}), self.d.get("site", {}), self.d.get("theme", {})
        self.projects = self.d.get("projects", [])
        self.L = dict(LABELS["en"]); self.L.update(LABELS.get(str(self.site.get("lang", "en"))[:2].lower(), {})); self.L.update(self.d.get("labels", {}))
        for i, p in enumerate(self.projects):
            p.setdefault("id", re.sub(r"[^a-z0-9]+", "-", p.get("title", f"project-{i + 1}").lower()).strip("-"))
        self.P = ""            # path back to the site root (pictures, assets) from the page being written
        self.H = ""            # path back to the home page of the layout being written
        self.out = self.up = ""  # --compare writes each layout under compare/<layout>/: where, and the way back up
        self.first = True      # the first picture of a page loads eagerly, the rest lazily
        self.count = 0
        self.images = []       # every picture used, for the sitemap

    # ── pictures ──────────────────────────────────────────────────────────
    def item(self, x):
        return {"src": x} if isinstance(x, str) else dict(x)

    def ratio(self, it):
        if it.get("ratio"): return float(it["ratio"])
        s = size_of(os.path.join(self.root, it["src"]))
        return s[0] / s[1] if s and s[1] else 1.5

    def media(self, it, alt, sizes):
        src = it["src"]; full = os.path.join(self.root, src)
        if not os.path.exists(full): warn("—", f"file not found: {src}"); return f'<span class="vh">{e(alt)}</span>'
        if src.lower().endswith(VIDEO):
            return f'<video src="{self.P}{e(src)}" muted loop playsinline preload="metadata" aria-label="{e(alt)}"></video>'
        if not it.get("alt"): self.noalt = getattr(self, "noalt", 0) + 1
        s = size_of(full) or (1600, 1067)
        # A smaller copy named like the big one ("shot-lg.jpg" + "shot-sm.jpg") is offered to small screens
        stem, ext = os.path.splitext(src); srcset = ""; source = ""
        if stem.endswith("-lg") and os.path.exists(os.path.join(self.root, stem[:-3] + "-sm" + ext)):
            sm = stem[:-3] + "-sm" + ext; sw = (size_of(os.path.join(self.root, sm)) or (1100, 0))[0]
            srcset = f' srcset="{self.P}{e(sm)} {sw}w, {self.P}{e(src)} {s[0]}w" sizes="{sizes}"'
            if all(os.path.exists(os.path.join(self.root, os.path.splitext(f)[0] + ".avif")) for f in (sm, src)):
                a = lambda f: self.P + e(os.path.splitext(f)[0] + ".avif")
                source = f'<source type="image/avif" srcset="{a(sm)} {sw}w, {a(src)} {s[0]}w" sizes="{sizes}">'
        served = os.path.splitext(full)[0] + ".avif" if source else full          # what a current browser downloads
        kb = os.path.getsize(served) / 1024
        if kb > 700: warn(13, f"{src} weighs {kb:.0f} KB. Export it under 500 KB (AVIF or WebP, 2000 px wide at most)")
        # The first picture is fetched first, the second is not delayed either (it usually shares the first screen)
        load = ' fetchpriority="high"' if self.first is True else "" if self.first == 1 else ' loading="lazy" decoding="async"'
        self.first = 1 if self.first is True else False; self.images.append((src, alt))
        img = f'<img src="{self.P}{e(src)}"{srcset} width="{s[0]}" height="{s[1]}" alt="{e(alt)}"{load}>'
        return f"<picture>{source}{img}</picture>" if source else img

    def tile(self, p, it, sizes, ar=None, link=True):
        it = self.item(it); self.count += 1
        alt = it.get("alt") or f'{p["title"]} · {self.count:02d}'
        ar = ar or self.ratio(it)
        inner = self.media(it, alt, sizes)
        if not link: return f'<div class="t" style="--ar:{ar:.4f}">{inner}</div>'
        return f'<a class="t" style="--ar:{ar:.4f}" href="{self.P}{e(it["src"])}" data-cap="{e(it.get("alt") or p["title"])}">{inner}</a>'

    def rows(self, p, width):
        """The body of a project: rows of one to three pictures, decision notes, before/after pairs."""
        out = []
        for row in p.get("rows", []):
            if isinstance(row, dict) and "note" in row:
                out.append(f'<p class="note"><span class="label">{e(row.get("label", self.L["decision"]))}</span><span>{rich(row["note"])}</span></p>')
            elif isinstance(row, dict) and "before" in row:
                b, a = self.item(row["before"]), self.item(row["after"]); cap = row.get("caption", p["title"]); self.count += 1
                b.setdefault("alt", f'{cap} ({self.L["before"].lower()})'); a.setdefault("alt", f'{cap} ({self.L["after"].lower()})')
                out.append(f'<figure class="ba" style="--ar:{self.ratio(a):.4f}">{self.media(a, a["alt"], width)}'
                           f'<div class="ba-b">{self.media(b, b["alt"], width)}</div><span class="ba-line" aria-hidden="true"></span>'
                           f'<span class="ba-tag ba-l" aria-hidden="true">{self.L["before"]}</span><span class="ba-tag ba-r" aria-hidden="true">{self.L["after"]}</span>'
                           f'<input type="range" min="0" max="100" value="50" step="any" aria-label="{e(cap)}: {e(self.L["before"])} / {e(self.L["after"])}"></figure>')
            else:
                items = row if isinstance(row, list) else [row]
                keep = " keep" if len(items) > 1 and all(self.ratio(self.item(i)) < 1 for i in items) else ""   # tall pairs stay side by side on a phone
                sizes = f"(max-width: 900px) 100vw, calc({width} / {len(items)})"
                out.append(f'<div class="row{keep}">' + "".join(self.tile(p, i, sizes) for i in items) + "</div>")
        return "\n".join(out)

    def flat(self, p):
        return [self.item(i) for row in p.get("rows", []) if not (isinstance(row, dict) and ("note" in row or "before" in row))
                for i in (row if isinstance(row, list) else [row])]

    # ── shared blocks ─────────────────────────────────────────────────────
    def rel(self, p):
        """Who the project was for: a named client, or what the "relationship" says."""
        return p.get("client") or {"personal": self.L["personal"], "freelance": self.L["freelance"],
                                   "employer": (self.person.get("employer") or {}).get("name", "")}.get(p.get("relationship", ""), "")

    def cover(self, p):
        """The picture for a project's home card: "cover", else its first picture, else the "after" of a before/after."""
        if p.get("cover"): return self.item(p["cover"])
        f = self.flat(p)
        if f: return f[0]
        ba = [r for r in p.get("rows", []) if isinstance(r, dict) and "after" in r]
        return self.item(ba[0]["after"]) if ba else {"src": ""}

    def meta_line(self, p):
        rel = self.rel(p)
        return " · ".join(str(x) for x in (p.get("role"), p.get("team"), p.get("year"), rel) if x)

    def role(self):
        r, emp = self.person.get("role", ""), self.person.get("employer") or {}
        if not emp.get("name"): return e(r)
        name = f'<a class="u" href="{e(emp["url"])}" target="_blank" rel="noopener">{e(emp["name"])}</a>' if emp.get("url") else e(emp["name"])
        return f"{e(r)} @ {name}"

    def avatar(self):
        ph = self.person.get("photo")
        return f'<img class="avatar" src="{self.P}{e(ph)}" width="64" height="64" alt="{e(self.L["portrait"])} {e(self.person.get("name", ""))}">' if ph else ""

    def contact(self):
        links = "".join(f'<a class="pill" href="{e(l["url"])}" target="_blank" rel="noopener me">{e(l["label"])}</a>' for l in self.person.get("links", []))
        mail = self.person.get("email")
        return f'<div class="contact">{links}' + (f'<a class="pill mail" href="mailto:{e(mail)}" data-copy="{e(mail)}">{e(mail)}</a>' if mail else "") + "</div>"

    def dock(self):
        """Rule 17: the name, the role and the address stay within reach. main.js shows this bar once the
        contact block has scrolled away and hides it at the end of the page, where the address already is."""
        P = self.person; mail = P.get("email")
        if not mail: return ""
        emp = (P.get("employer") or {}).get("name"); role = " @ ".join(x for x in (P.get("role"), emp) if x)
        pic = f'<img src="{self.P}{e(P["photo"])}" width="28" height="28" alt="">' if P.get("photo") else ""
        return (f'<aside class="dock" aria-label="{e(self.L["contact"])}"><a class="dock-id" href="{self.H or "#"}">{pic}<b>{e(P.get("name", ""))}</b>'
                + (f"<span>{e(role)}</span>" if role else "")
                + f'</a><a class="pill mail" href="mailto:{e(mail)}" data-copy="{e(mail)}">{e(mail)}</a></aside>\n')

    def say(self):
        return "".join(f"<p>{rich(self.person[k])}</p>" for k in ("headline", "proof") if self.person.get(k))

    def footer(self):
        facts = "".join(f"<li><span>{e(k)}</span><span>{e(v)}</span></li>" for k, v in self.d.get("facts", []))
        left = f'<div><p class="label">{e(self.L["facts"])}</p><ul class="list">{facts}</ul></div>' if facts else ""
        right = f'<div><p class="label">{e(self.L["authorship"])}</p><p>{rich(self.d["authorship"])}</p></div>' if self.d.get("authorship") else ""
        mail = self.person.get("email", "")
        links = " · ".join(f'<a href="{e(l["url"])}" target="_blank" rel="noopener me">{e(l["label"])}</a>' for l in self.person.get("links", []))
        return (f'<footer class="info" id="info">' + (f'<div class="cols">{left}{right}</div>' if left or right else "")
                + (f'<p class="ask">{rich(self.d["ask"])}</p>' if self.d.get("ask") else "")
                + (f'<a class="big" href="mailto:{e(mail)}" data-copy="{e(mail)}">{e(mail)}</a>' if mail else "")
                + f'<p class="fine"><span>© {datetime.date.today().year} {e(self.person.get("name", ""))}</span><span>{links}</span></p></footer>')

    def header(self, n, p):
        m = self.meta_line(p)
        return (f'<header class="wh"><span class="num">{n:02d}</span><h2 id="h-{e(p["id"])}">{e(p["title"])}</h2>'
                + (f'<p class="tags">{e(p["tags"])}</p>' if p.get("tags") else "")
                + (f'<p class="meta">{e(m)}</p>' if m else "")
                + (f'<p class="desc">{rich(p["summary"])}</p>' if p.get("summary") else "") + "</header>")

    def page(self, body, title, desc, path="", cls=None):
        url = self.site.get("url", "").rstrip("/"); canon = f"{url}/{path}" if url and not self.out else ""
        t = self.theme; style = ""
        for k, v in (("--acc", t.get("accent")), ("--sans", t.get("font")), ("--mono", t.get("mono")),
                     ("--rt", f'{t["radius"]}px' if "radius" in t else None), ("--gap", f'{t["gap"]}px' if "gap" in t else None)):
            if v: style += f"{k}:{v};"
        og = self.site.get("share_image")
        ld = {"@context": "https://schema.org", "@type": "ProfilePage", "mainEntity": {k: v for k, v in {
            "@type": "Person", "name": self.person.get("name"), "jobTitle": self.person.get("role"),
            "worksFor": {"@type": "Organization", "name": self.person["employer"]["name"]} if (self.person.get("employer") or {}).get("name") else None,
            "address": {"@type": "PostalAddress", "addressLocality": self.person["city"]} if self.person.get("city") else None,
            "email": self.person.get("email"), "url": url or None, "description": desc,
            "sameAs": [l["url"] for l in self.person.get("links", [])] or None}.items() if v}}
        head = [f'<meta charset="utf-8">', '<meta name="viewport" content="width=device-width, initial-scale=1">',
                f"<title>{e(title)}</title>", f'<meta name="description" content="{e(desc)}">',
                f'<meta property="og:title" content="{e(title)}">', f'<meta property="og:description" content="{e(desc)}">',
                '<meta property="og:type" content="profile">', '<meta name="twitter:card" content="summary_large_image">']
        if canon: head += [f'<link rel="canonical" href="{e(canon)}">', f'<meta property="og:url" content="{e(canon)}">']
        if og: head.append(f'<meta property="og:image" content="{e(og if og.startswith("http") else f"{url}/{og}")}">')
        if t.get("font_url"): head += ['<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>', f'<link rel="stylesheet" href="{e(t["font_url"])}">']
        head += [f'<link rel="stylesheet" href="{self.P}assets/styles.css">',
                 f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>']
        return (f'<!doctype html>\n<html lang="{e(self.site.get("lang", "en"))}" data-mode="{e(t.get("mode", "dark"))}"'
                + (f' style="{e(style)}"' if style else "") + ">\n<head>\n" + "\n".join(head) + "\n</head>\n"
                f'<body class="l-{cls or self.layout}" data-close="{e(self.L["close"])}" data-prev="{e(self.L["previous"])}" data-next="{e(self.L["next"])}">\n<a class="skip" href="#work">{e(self.L["skip"])}</a>\n{body}\n{self.dock()}'
                f'<script src="{self.P}assets/main.js" defer></script>\n</body>\n</html>\n')

    # ── the three layouts ─────────────────────────────────────────────────
    def index(self):
        nav = "".join(f'<li><a href="#{e(p["id"])}"><span class="num">{n:02d}</span><span>{e(p["title"])}</span><span class="ct">{len(self.flat(p))}</span></a></li>'
                      for n, p in enumerate(self.projects, 1))
        aside = (f'<aside class="intro" aria-label="{e(self.L["about"])}"><div class="card who">{self.avatar()}<header><h1>{e(self.person.get("name", ""))}</h1>'
                 f'<p class="role">{self.role()}</p></header><div class="say">{self.say()}</div>{self.contact()}</div>'
                 f'<div class="card nav"><nav class="index" aria-label="{e(self.L["index"])}"><p class="label">{e(self.L["index"])}</p><ol>{nav}</ol></nav></div></aside>')
        work = "\n".join(f'<section class="work" id="{e(p["id"])}" aria-labelledby="h-{e(p["id"])}">{self.header(n, p)}\n{self.rows(p, "100vw - 400px")}</section>'
                         for n, p in enumerate(self.projects, 1))
        return f'{aside}\n<main id="work">\n{work}\n{self.footer()}\n</main>'

    def columns(self):
        top = (f'<header class="top who"><div class="who-id">{self.avatar()}<div><h1>{e(self.person.get("name", ""))}</h1><p class="role">{self.role()}</p></div></div>'
               f'<div class="say">{self.say()}</div>{self.contact()}</header>')
        secs = []
        for n, p in enumerate(self.projects, 1):
            ar = p.get("ratio") or self.theme.get("ratio") or 4 / 3
            if isinstance(ar, str): a, b = ar.replace(":", "/").split("/"); ar = float(a) / float(b)
            notes = "".join(f'<p class="note"><span class="label">{e(r.get("label", self.L["decision"]))}</span><span>{rich(r["note"])}</span></p>'
                            for r in p.get("rows", []) if isinstance(r, dict) and "note" in r)
            tiles = "".join(self.tile(p, it, "(max-width: 900px) 100vw, 50vw", ar) for it in self.flat(p))
            secs.append(f'<section class="work" id="{e(p["id"])}" aria-labelledby="h-{e(p["id"])}">{self.header(n, p)}{notes}<div class="grid">{tiles}</div></section>')
        return f'{top}\n<main id="work">\n' + "\n".join(secs) + f"\n{self.footer()}\n</main>"

    def case_top(self, home):
        name = e(self.person.get("name", ""))
        ident = f"<h1>{name}</h1>" if home else f'<a href="{self.H}"><b>{name}</b></a>'
        return f'<header class="top who"><div class="who-id">{self.avatar()}<div>{ident}<p class="role">{self.role()}</p></div></div>{self.contact()}</header>'

    def case_home(self):
        hero = (f'<section class="hero who"><p class="say">{rich(self.person.get("headline", ""))}</p>'
                + (f'<p class="proof">{rich(self.person["proof"])}</p>' if self.person.get("proof") else "") + "</section>")
        cards = []
        for p in self.projects:
            cover = self.cover(p); m = self.meta_line(p)
            cards.append(f'<a class="pc" href="{e(p["id"])}/" aria-labelledby="h-{e(p["id"])}">'
                         + self.tile(p, cover, "(max-width: 1152px) 100vw, 1120px", p.get("cover_ratio") or min(max(self.ratio(cover), 1.6), 2.2), link=False)
                         + f'<div class="pc-txt"><div><h2 id="h-{e(p["id"])}">{e(p["title"])}</h2>' + (f'<p class="meta">{e(m)}</p>' if m else "") + "</div><div>"
                         + (f'<p class="desc">{rich(p["summary"])}</p>' if p.get("summary") else "")
                         + (f'<p class="res">{rich(p["result"])}</p>' if p.get("result") else "")
                         + f'<span class="go u">{e(self.L["read"])}</span></div></div></a>')
        return f'{self.case_top(True)}\n<main id="work">\n{hero}\n' + "\n".join(cards) + f"\n</main>\n{self.footer()}"

    def case_page(self, n, p):
        L = self.L
        facts = "".join(f"<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in ((L["role"], p.get("role")), (L["team"], p.get("team")), (L["year"], p.get("year")), (L["for"], self.rel(p))) if v)
        nxt = self.projects[(n + 1) % len(self.projects)]
        block = lambda label, key: f'<section class="say2"><h2>{label}</h2><p>{rich(p[key])}</p></section>' if p.get(key) else ""
        return (f'{self.case_top(False)}\n<main id="work" class="sheet"><a class="back" href="{self.H}">{e(L["all"])}</a>'
                f'<header class="head"><h1>{e(p["title"])}</h1>' + (f'<p class="lead">{rich(p["summary"])}</p>' if p.get("summary") else "") + "</header>"
                + (f'<dl class="facts">{facts}</dl>' if facts else "") + block(e(L["the_decision"]), "decision")
                + self.rows(p, "min(100vw, 1120px)") + block(e(L["result"]), "result")
                + (f'<a class="next" href="{self.H}{e(nxt["id"])}/"><span>{e(L["next"])}</span><b>{e(nxt["title"])} →</b></a>' if len(self.projects) > 1 else "")
                + f"</main>\n{self.footer()}")

    # ── checks: what the 30-second audit would still flag ─────────────────
    def check(self):
        P, per = self.person, self.projects
        h = plain(P.get("headline", ""))
        if not h: warn(1, 'no "headline": the first sentence must say what you do')
        elif len(h.split()) > 32: warn(1, f"the headline has {len(h.split())} words; aim for under 25")
        found = [w for w in EMPTY if w in (h + " " + plain(P.get("proof", ""))).lower()]
        if found: warn(1, f'empty words in the headline: {", ".join(found)}. Say what you make and for whom instead')
        if not P.get("proof"): warn(3, 'no "proof" line: years, named clients or employers, numbers')
        if not per: warn(2, "no projects")
        if len(per) > 8: warn(5, f"{len(per)} projects; four to eight is plenty. Cut, or move side work to its own site")
        for p in per:
            t = p.get("title", p["id"])
            if not p.get("summary"): warn(6, f'"{t}" has no summary line')
            if not p.get("role") and not self.d.get("authorship"): warn(7, f'"{t}" does not say your role, and there is no site-wide "authorship" line')
            if not p.get("client") and not p.get("relationship"): warn(7, f'"{t}" does not say whether it was a client, an employer or a personal concept')
            if not self.flat(p) and not any(isinstance(r, dict) and "before" in r for r in p.get("rows", [])): warn(2, f'"{t}" has no pictures')
            if self.layout == "case":
                if not p.get("decision") and not any(isinstance(r, dict) and "note" in r for r in p.get("rows", [])): warn(8, f'"{t}" shows no decision')
                if not p.get("result"): warn(9, f'"{t}" does not say what changed or what shipped')
        if not P.get("email"): warn(10, "no email"); warn(17, "no email, so the dock that keeps your contact on screen was left out")
        if not self.d.get("ask"): warn(10, 'no "ask": one sentence on what to write to you for')
        if not self.site.get("share_image"): warn(14, 'no "share_image" (1200×630) for link previews')
        elif not self.site["share_image"].startswith("http") and not os.path.exists(os.path.join(self.root, self.site["share_image"])):
            warn(14, f'share_image not found: {self.site["share_image"]}')
        if not self.site.get("url"): warn(15, 'no site "url": sitemap.xml and canonical links were left out')
        if not self.d.get("facts"): warn(15, 'no "facts": plain facts (based in, years, clients) help search and AI assistants')
        def walk(x, where):
            if isinstance(x, str):
                for m in SLOT.findall(x): self.slots.append((where, m))
            elif isinstance(x, dict):
                for k, v in x.items():
                    if k not in ("theme", "labels"): walk(v, f'{x["title"]} · {k}' if "title" in x and k != "title" else where if k == "rows" else (where + " · " if where and "title" not in x else "") + k if "title" not in x else k)
            elif isinstance(x, list):
                for v in x: walk(v, where)
        self.slots = []; walk({k: v for k, v in self.d.items() if k != "projects"}, "")
        for p in self.projects: walk(p, p.get("title", ""))
        if getattr(self, "noalt", 0): warn(15, f"{self.noalt} pictures have no alt text of their own; the project title was used")

    # ── write ─────────────────────────────────────────────────────────────
    def write(self, rel, text):
        full = os.path.join(self.root, rel); os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
        open(full, "w", encoding="utf-8").write(text); return rel

    def render(self, title, desc):
        """Writes every page of the current layout under self.out. Returns the files written and the page paths."""
        P = self.person; wrote, pages = [], [""]
        self.P, self.H, self.first, self.count = self.up, "", True, 0
        body = {"index": self.index, "columns": self.columns, "case": self.case_home}[self.layout]()
        wrote.append(self.write(self.out + "index.html", self.page(body, title, desc)))
        if self.layout == "case":
            for n, p in enumerate(self.projects):
                self.P, self.H, self.first, self.count = "../" + self.up, "../", True, 0
                d = plain(p.get("summary") or desc)[:260]
                wrote.append(self.write(f'{self.out}{p["id"]}/index.html', self.page(self.case_page(n, p), f'{p["title"]} — {P.get("name", "")}', d, f'{p["id"]}/')))
                pages.append(f'{p["id"]}/')
        self.P, self.H = self.up, ""
        return wrote, pages

    def compare(self, title, desc):
        """The same content in all three layouts, under compare/, plus a page that links them."""
        chosen = self.layout; said = {"index": "Who you are stays fixed on the left; work runs large on the right.",
                                      "columns": "A short header, then every piece the same size, two across.",
                                      "case": "A big statement, one card per project, one page to read per project."}
        for lay in LAYOUTS:
            self.layout, self.out, self.up = lay, f"compare/{lay}/", "../../"
            self.render(title, desc)
        self.layout, self.out, self.up, self.P = chosen, "", "", ""
        self.noalt, self.images = 0, []          # counted again by the real build
        items = "".join(f'<li><a href="{lay}/"><b>{lay}</b>' + (" <i>current</i>" if lay == chosen else "") + f"<span>{said[lay]}</span></a></li>" for lay in LAYOUTS)
        return self.write("compare/index.html", '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<meta name="robots" content="noindex">\n<title>Choose a grid</title>\n<style>\n'
            'body { margin: 0; padding: 48px 20px; background: #0c0c0c; color: #f2f1ee; font: 16px/1.5 ui-sans-serif, system-ui, sans-serif; }\n'
            'main { max-width: 560px; margin: 0 auto; } h1 { font-size: 24px; letter-spacing: -.02em; margin: 0 0 6px; } p { color: #a3a29d; margin: 0 0 28px; }\n'
            'ul { list-style: none; margin: 0; padding: 0; } a { display: block; padding: 18px 20px; margin-bottom: 8px; border-radius: 16px; background: #171717; border: 1px solid rgba(255,255,255,.07); color: inherit; text-decoration: none; }\n'
            'a:hover { background: #1f1f1f; } b { font: 600 15px ui-monospace, Menlo, monospace; } i { font: 11px ui-monospace, Menlo, monospace; text-transform: uppercase; color: #77766f; margin-left: 8px; }\n'
            'span { display: block; color: #a3a29d; margin-top: 4px; }\n</style>\n</head>\n<body>\n<main>\n<h1>Choose a grid</h1>\n'
            f'<p>The same content in each of the three. To keep one, set <code>"layout"</code> in portfolio.json and build again. Delete this folder before publishing.</p>\n<ul>{items}</ul>\n</main>\n</body>\n</html>\n')

    def build(self, compare=False):
        P = self.person; emp = (P.get("employer") or {}).get("name")
        title = self.site.get("title") or f'{P.get("name", "")} — {P.get("role", "")}' + (f", {emp}" if emp else "") + (f' ({P["city"]})' if P.get("city") else "")
        desc = self.site.get("description") or " ".join(plain(P[k]) for k in ("headline", "proof") if P.get(k))[:260]
        os.makedirs(os.path.join(self.root, "assets"), exist_ok=True)
        for f in ("styles.css", "main.js"): shutil.copy(os.path.join(TEMPLATE, f), os.path.join(self.root, "assets", f))
        wrote = ["assets/styles.css", "assets/main.js"]
        picker = self.compare(title, desc) if compare else None
        w, pages = self.render(title, desc); wrote += w
        url = self.site.get("url", "").rstrip("/")
        if url:
            today = datetime.date.today().isoformat()
            sm = "".join(f"<url><loc>{e(url)}/{e(pg)}</loc><lastmod>{today}</lastmod></url>" for pg in pages)
            wrote.append(self.write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n'))
            wrote.append(self.write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {url}/sitemap.xml\n"))
        self.check()
        print(f'Built "{self.layout}" layout: {len(self.projects)} projects, {len({s for s, _ in self.images})} pictures')
        print("Wrote: " + ", ".join(wrote))
        if WARN:
            print(f"\n{len(WARN)} things the 30-second audit would flag:")
            for rule, msg in sorted(set(WARN), key=lambda x: (x[0] if isinstance(x[0], int) else 99, x[1])):
                print(f"  rule {rule:>2}  {msg}")
        else: print("\nNothing left for the 30-second audit to flag from the content file.")
        if self.slots:
            first = [w for w, _ in self.slots if w.split(" · ")[-1] in ("headline", "proof", "name", "role")]
            print(f"\n{len(self.slots)} slots still to fill. They are visible on the site exactly as written, so it is not ready to publish:")
            for where, slot in self.slots: print(f"  {where:<34} {slot}")
            if first: print("  Slots in the headline or proof are the first thing a visitor reads. Rewrite those lines without them until the fact is known.")
        if picker: print(f"\nAll three grids, to choose from: {picker} (open it through a server). Delete compare/ before publishing.")
        if self.layout == "case": print("\nTo look at it: run  python3 -m http.server  in the site folder (project links need a server, not a double-click).")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--compare"]
    if len(args) != 1 or args[0] in ("-h", "--help"): sys.exit(__doc__)
    Site(args[0]).build(compare="--compare" in sys.argv)
