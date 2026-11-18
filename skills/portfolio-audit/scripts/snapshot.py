#!/usr/bin/env python3
"""Facts about a portfolio page, so the audit does not guess. Standard library only.

Usage:
  python3 snapshot.py URL [URL ...]      facts for each page (home, first project, about)
  python3 snapshot.py --text URL         the page's readable text, in reading order
A local .html file works in place of a URL."""
import json, re, struct, sys, time, urllib.request, urllib.error
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

UA = "Mozilla/5.0 (compatible; portfolio-audit/1.0)"
# Words that could sit on anyone's portfolio and so say nothing about this one (rule 1)
EMPTY = ["passionate", "multi-disciplinary", "multidisciplinary", "pixel-perfect", "pixel perfect", "crafting",
         "creative thinker", "storyteller", "problem solver", "user-centric", "user-centered", "delightful",
         "seamless", "innovative", "detail-oriented", "apasionad", "multidisciplinar"]
SKIP = {"script", "style", "noscript", "template", "svg"}
BLOCK = {"p", "div", "section", "article", "li", "br", "h1", "h2", "h3", "h4", "tr", "figcaption", "header", "footer"}
ASSET = re.compile(r"\.(jpe?g|png|gif|webp|avif|svg|mp4|webm|mov|pdf|zip|css|js|ico|woff2?)$", re.I)
MAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


class Redirect308(urllib.request.HTTPRedirectHandler):
    """Older Pythons do not follow 308."""
    def http_error_308(self, req, fp, code, msg, headers):
        return self.http_error_302(req, fp, 307, msg, headers)

OPENER = urllib.request.build_opener(Redirect308)


def get(url, limit=3_000_000):
    """Returns (status, final_url, body, seconds, headers). Never raises."""
    t = time.time()
    try:
        r = OPENER.open(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=15)
        body = r.read(limit)
        return r.status, r.geturl(), body, time.time() - t, dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, url, b"", time.time() - t, {}
    except Exception as e:
        return 0, url, str(e).encode(), time.time() - t, {}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta, self.links, self.imgs, self.heads, self.ld = {}, [], [], [], []
        self.sources, self.script_src, self.buttons = [], [], []
        self.title, self.lang, self.words, self.lines = "", "", [], [[]]
        self.videos = self.iframes = self.inline_bg = 0
        self._skip, self._in, self._buf, self._ld = 0, None, [], False

    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag == "html": self.lang = a.get("lang", "")
        if tag == "script":
            self._ld = a.get("type", "").lower() == "application/ld+json"
            if a.get("src"): self.script_src.append(a["src"])
        if tag in SKIP: self._skip += 1
        if tag in BLOCK and self.lines[-1]: self.lines.append([])
        if tag == "meta":
            k = a.get("property") or a.get("name")
            if k and a.get("content") is not None: self.meta[k.lower()] = a["content"].strip()
        if tag == "a" and a.get("href"): self.links.append(a["href"].strip())
        if tag == "img": self.imgs.append(a)
        if tag == "source" and a.get("type"): self.sources.append(a["type"].lower())
        if tag == "video": self.videos += 1
        if tag == "iframe": self.iframes += 1
        if "background" in (a.get("style") or "") and "url(" in a["style"]: self.inline_bg += 1
        label = " ".join(filter(None, (a.get("aria-label"), a.get("title"), a.get("data-email"), a.get("data-clipboard-text"))))
        if label and tag in ("button", "a", "div", "span"): self.buttons.append(label)
        if tag in ("title", "h1", "h2", "h3"): self._in, self._buf = tag, []

    def handle_endtag(self, tag):
        if tag in SKIP and self._skip: self._skip -= 1
        if tag == "script": self._ld = False
        if tag in BLOCK and self.lines[-1]: self.lines.append([])
        if tag == self._in:
            text = " ".join(" ".join(self._buf).split())
            if tag == "title": self.title = text
            elif text: self.heads.append((tag, text))
            self._in = None

    def handle_data(self, d):
        if self._ld: self.ld.append(d)
        if self._in: self._buf.append(d)
        if not self._skip and self._in != "title":
            self.words += d.split(); self.lines[-1] += d.split()


def ld_facts(blocks):
    """Types present, plus the fields of a Person that an audit cares about."""
    types, person = [], {}
    def walk(x):
        if isinstance(x, dict):
            t = x.get("@type"); ts = t if isinstance(t, list) else [t] if t else []
            types.extend(ts)
            if "Person" in ts and not person:
                for k in ("name", "jobTitle", "worksFor", "address", "knowsAbout", "sameAs"):
                    v = x.get(k)
                    if isinstance(v, dict): v = v.get("name") or v.get("addressLocality")
                    if isinstance(v, list): v = ", ".join(str(i.get("name", i) if isinstance(i, dict) else i) for i in v[:6])
                    if v: person[k] = str(v)[:140]
            for v in x.values(): walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
    for b in blocks:
        try: walk(json.loads(b))
        except Exception: types.append("(invalid JSON-LD)")
    return sorted(set(types)), person


def image_size(b):
    """(width, height) of a PNG, GIF, JPEG or WebP from its first bytes, or None."""
    try:
        if b[:8] == b"\x89PNG\r\n\x1a\n": return struct.unpack(">II", b[16:24])
        if b[:3] == b"GIF": return struct.unpack("<HH", b[6:10])
        if b[:4] == b"RIFF" and b[8:15] == b"WEBPVP8":
            if b[15:16] == b"X": return (int.from_bytes(b[24:27], "little") + 1, int.from_bytes(b[27:30], "little") + 1)
            if b[15:16] == b" ": return tuple(x & 0x3FFF for x in struct.unpack("<HH", b[26:30]))
        if b[:2] == b"\xff\xd8":
            i = 2
            while i < len(b) - 9:
                if b[i] != 0xFF: i += 1; continue
                m = b[i + 1]
                if m in (0xC0, 0xC1, 0xC2): h, w = struct.unpack(">HH", b[i + 5:i + 9]); return (w, h)
                i += 2 + struct.unpack(">H", b[i + 2:i + 4])[0]
    except Exception: pass
    return None


def load(target):
    if re.match(r"https?://", target):
        status, url, body, secs, headers = get(target)
        if not body or status >= 400 or status == 0:
            print(f"Could not load {target}: status {status} {body[:200].decode('utf-8', 'replace')}"); return None
        return status, url, body, secs, headers
    return 200, target, open(target, "rb").read(), 0, {}


def text_mode(target):
    got = load(target)
    if not got: return 1
    p = Page(); p.feed(got[2].decode("utf-8", "replace"))
    print(f"# Text of {got[1]} ({len(p.words)} words; hidden and duplicated menu text may be included)\n")
    for l in p.lines:
        if l: print(" ".join(l))
    return 0


def snapshot(target):
    got = load(target)
    if not got: return 1
    status, url, body, secs, headers = got
    html = body.decode("utf-8", "replace")
    p = Page(); p.feed(html)
    web = bool(re.match(r"https?://", url)); host = urlparse(url).netloc
    text = " ".join(p.words); low = text.lower()
    h1 = [t for k, t in p.heads if k == "h1"]
    shell = len(p.words) < 30 and not h1          # nothing for a reader: drawn in the browser by JavaScript
    sparse = not shell and len(p.words) < 80

    internal, external, mail = [], [], []
    for h in p.links:
        if h.startswith("mailto:"): mail.append(h[7:].split("?")[0])
        elif h.startswith(("#", "javascript:", "tel:")): continue
        else:
            full = urljoin(url, h).split("#")[0]
            if urlparse(full).netloc == host:
                if not ASSET.search(urlparse(full).path): internal.append(full)
            else: external.append(full)
    internal = sorted({u.rstrip("/") for u in internal} - {url.rstrip("/")})
    ext_hosts = sorted({urlparse(u).netloc.replace("www.", "") for u in external if urlparse(u).netloc})
    plain_mail = sorted(set(MAIL.findall(text)) - set(mail))
    mail_buttons = [b for b in p.buttons if re.search(r"e-?mail|correo", b, re.I)]

    fmt = {}
    for i in p.imgs:
        src = (i.get("src") or i.get("data-src") or "").split("?")[0].lower()
        ext = src.rsplit(".", 1)[-1] if "." in src.rsplit("/", 1)[-1] else "other"
        fmt[ext] = fmt.get(ext, 0) + 1
    modern = [n for n, k in (("AVIF", "image/avif"), ("WebP", "image/webp")) if k in p.sources or f".{n.lower()}" in html]
    css_bg = p.inline_bg + len(re.findall(r"background(?:-image)?\s*:[^;}]*url\(", html))

    def line(k, v): print(f"{k:<26}{v}")
    unknown = "unknown (page is drawn by JavaScript; look in a browser)"
    print(f"# Snapshot of {url}\n")
    if shell:
        print("NOTE: the HTML holds no readable content. The page is drawn in the browser by JavaScript, so search\n"
              "engines, AI agents and this script see an empty shell. That is a finding for rule 15. Everything about\n"
              "the content below is unknown, not absent: check it in a browser or from screenshots.\n")
    elif sparse:
        print("NOTE: the page has very little text. It is in the HTML (not an empty shell), but work shown through\n"
              "canvas, video or CSS will not appear in the counts below. Confirm what is visible in a browser.\n")
    print("## Response")
    line("Status", status)
    if secs: line("HTML received in", f"{secs:.2f} s from this machine. Says the server is quick, not that the page appears quickly")
    line("HTML size", f"{len(body) / 1024:.0f} KB")
    if headers: line("Server / cache", f"{headers.get('Server', '?')} · {headers.get('Cache-Control', 'no cache header')}")
    if web and p.script_src:
        total = 0; n = 0
        for s in p.script_src[:12]:
            st, _, b, _, hd = get(urljoin(url, s), 5_000_000)
            if st == 200: total += len(b); n += 1
        line("External scripts", f"{len(p.script_src)} files, {total / 1024:.0f} KB uncompressed" + (f" (first {n} measured)" if len(p.script_src) > n else ""))

    print("\n## What search and share cards show")
    line("Title", f"{p.title!r} ({len(p.title)} characters)")
    desc = p.meta.get("description", "")
    line("Description", repr(desc) if desc else "MISSING")
    line("Share title", p.meta.get("og:title", "MISSING"))
    line("Share description", p.meta.get("og:description", "MISSING"))
    og = p.meta.get("og:image")
    if og and web:
        st, _, b, _, hd = get(urljoin(url, og), 6_000_000)
        size = image_size(b) if st == 200 else None
        line("Share image", f"{og} · " + (f"{len(b) / 1024:.0f} KB" + (f", {size[0]}×{size[1]}" if size else "") if st == 200 else f"DOES NOT LOAD (status {st})"))
    else: line("Share image", og or "MISSING")
    line("Card type", p.meta.get("twitter:card", "not set"))
    line("Language", p.lang or "not set")
    vp = p.meta.get("viewport")
    line("Viewport tag (phone)", "MISSING" if not vp else "yes" + (" · blocks pinch zoom (user-scalable=no or maximum-scale=1)" if re.search(r"user-scalable\s*=\s*(no|0)|maximum-scale\s*=\s*1(\.0)?\b", vp) else ""))

    print("\n## What a visitor reads first")
    line("Main heading (h1)", unknown if shell else h1 if h1 else "NONE")
    line("First 60 words", unknown if shell else " ".join(p.words[:60]))
    line("Words of text in HTML", len(p.words))
    found = [b for b in EMPTY if b in low]
    line("Empty words (rule 1)", ", ".join(found) if found else "none")
    yrs = lambda s: set(re.findall(r"\b(\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty)\+?\s+years?\b", s.lower()))
    if desc and yrs(desc) and yrs(text) and not (yrs(desc) & yrs(text)):
        line("CONTRADICTION", f"description says {sorted(yrs(desc))} years, the page says {sorted(yrs(text))} years")
    if not shell:
        print("\n## Headings (first 25)")
        for k, t in p.heads[:25]: print(f"  {k}  {t[:90]}")

    print("\n## Work and media")
    if shell: line("Images, video", unknown)
    else:
        kinds = ", ".join(f"{v} {k}" for k, v in sorted(fmt.items(), key=lambda x: -x[1]))
        line("Images in HTML", f"{len(p.imgs)}" + (f" ({kinds})" if kinds else "") + (f" · with {' and '.join(modern)} versions" if modern else " · no AVIF or WebP seen"))
        if css_bg or len(p.imgs) < 3: line("", f"{css_bg} more set as CSS backgrounds in the HTML; images set in stylesheets or canvas are not counted")
        line("Without alt text", sum(1 for i in p.imgs if not (i.get("alt") or "").strip()))
        line("Lazy-loaded", sum(1 for i in p.imgs if i.get("loading") == "lazy"))
        line("Videos / embeds", f"{p.videos} video, {p.iframes} iframe (weight not measured)")

    print("\n## Ways out")
    if shell: line("Contact and links", unknown)
    else:
        ways = []
        if mail: ways.append("link: " + ", ".join(sorted(set(mail))))
        if plain_mail: ways.append("plain text, not a link: " + ", ".join(plain_mail))
        if mail_buttons: ways.append(f"button ({mail_buttons[0]!r}); address may not be visible")
        line("Email", " · ".join(ways) or "NONE in the HTML (look for a form)")
        line("LinkedIn", "linked" if any("linkedin.com" in h for h in ext_hosts) else "not linked on this page")
        line("Other sites linked", ", ".join(ext_hosts[:15]) or "none")
        line("Internal pages linked", f"{len(internal)} (files and images left out)")
        for u in internal[:25]: print(f"  {u}")

    print("\n## For machines")
    types, person = ld_facts(p.ld)
    line("Structured data", ", ".join(types) or "NONE")
    for k, v in person.items(): line(f"  Person.{k}", v)
    if web:
        root = f"{urlparse(url).scheme}://{host}"
        s404, _, b404, _, _ = get(f"{root}/this-page-should-not-exist-7f3a", 200_000)
        soft = s404 == 200
        if soft: line("Missing pages", "return status 200 with the normal page (no real 404); broken links go unnoticed")
        for f in ("robots.txt", "sitemap.xml", "llms.txt"):
            s, _, b, _, hd = get(f"{root}/{f}", 200_000)
            ok = s == 200 and b and b"<html" not in b[:400].lower() and b"<!doctype html" not in b[:400].lower()
            line(f"/{f}", "yes" if ok else "no (the server answers with the normal page instead)" if s == 200 else f"no ({s})")
    print()
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"): sys.exit(__doc__)
    if args[0] == "--text": sys.exit(max(text_mode(a) for a in args[1:]) if args[1:] else __doc__)
    sys.exit(max(snapshot(a) for a in args))
