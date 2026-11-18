---
name: portfolio-build
description: Builds or rebuilds a designer's portfolio website so a reviewer understands it in 30 seconds, from one content file and one of three proven page grids (a fixed profile beside full-width work, an even two-column grid, or one long case study per project). Use this whenever someone wants to make a portfolio site, start a personal site for their design work, redo or restructure an existing portfolio, turn a folder of project images or a Behance/Dribbble/Notion page into their own site, choose a layout or grid for a portfolio, or apply the fixes from a portfolio audit, even if they only say "I need a portfolio" or "make my site better". For designers, art directors, design leads, illustrators, motion and 3D artists, photographers and film makers.
---

# Portfolio build

A portfolio gets about 30 seconds on the first visit. This skill builds one that spends those seconds well:
who you are and what you do on the first screen, real work beside it, your part in each project stated, and
one clear way to reach you.

It fixes the **structure** and leaves the **look** to the person. The three grids decide where things go and
in what order. Typeface, colour, corner radius and spacing are theirs, set in one small block. Two portfolios
built with this skill should read the same way and look nothing alike.

Paths below are relative to this skill's folder.

## How it works

One file, `portfolio.json`, holds everything: who the person is, the projects, the chosen grid and the look.
One command turns it into a static site (plain HTML and CSS, no framework, nothing to install):

```bash
python3 scripts/build.py path/to/their-site/portfolio.json
```

The site is written next to the content file. The script then prints two lists: what a 30-second audit would
still flag, each line tied to a rule number (`references/rules.md` has the seventeen in one line each), and every
`[slot]` still waiting for a fact. Treat both as the to-do list.

## Steps

### 1. Find out what the portfolio is for

Ask for, or work out from what you were given:

- **The target.** The role or client it is aimed at. It decides the headline, the order and what is left out.
- **The work.** Which projects, and for each: what it was, their part, who it was for, the year, one thing
  they decided and what happened as a result.
- **The material.** Where the images and videos are.

If they have an existing site, read it first and carry over what is there. If the `portfolio-audit` skill is
available and they have a live site, running it first tells you exactly what to change.

Ask only for what you cannot find. A person with a folder of images and a LinkedIn page has already given you
most of it. If nobody is there to answer, carry on with what you have and use slots (step 3).

Material the person is unsure about (a sketchbook, a student project, something old) stays out. They doubted it
for a reason, and a portfolio is judged by its weakest piece. Say what you left out and why. Three strong
projects are a complete portfolio; do not pad to reach four.

### 2. Let the person choose the grid

Read `references/grids.md`. It describes the three grids and who each one suits. The grid decides how the
whole site reads, so it is the person's choice, not yours. Your part is to make it an easy one.

Before you build, name the three in one short message, one line each, say which you recommend for their work
and target and why, and ask which they want. Put it together with anything else you need to ask in step 1, so
there is one round of questions and not two.

- If they already named a grid, use it and do not reopen the question.
- If they pick a different one from your recommendation, build theirs. Say once what it costs them if it
  matters (for example, `index` has no place for a decision and a result), then drop it.
- If they are unsure, or nobody is there to answer, go ahead with your recommendation and build with
  `--compare` in step 5, so all three are there to open side by side.

Switching later is one word in the file, so nobody is locked in. That is a reason to offer the choice lightly,
not a reason to skip it.

### 3. Write the content file

Copy `assets/example/portfolio.json` as a starting point and read `references/content.md` for every field.
Put it in the folder that will become the site, with the images beside it. The example uses the `case` grid;
for `index` and `columns`, `decision` and `result` are optional and before/after rows are rarely needed.

How to write the parts that matter most:

- **Headline:** one sentence that says what they make and for whom, with a fact in it. It should not fit on
  anyone else's site. "Product designer for fintech apps. Eight years, most recently lead on the savings flow
  at Ledger." Not "Multi-disciplinary creative passionate about crafting experiences."
- **Proof:** the three or four strongest names or numbers, right after the headline.
- **Order:** the project that best fits the target goes first, whatever its date. Four to eight projects.
  Side disciplines (film for an art director, illustration for a product designer) are better as a second
  site with its own content file than mixed in.
- **Each project:** a one-line summary, the role, and whether it was for a client, an employer or a personal
  concept. For product and leadership targets, add the decision and the result.
- **Role:** their current title as it is, not the one they are applying for.
- **Ask:** one sentence above the email that says what to write for.
- **Language:** write in the language of their audience and set `site.lang`. The template's own words (Index,
  Facts, Next…) follow it for English and Spanish; for any other language, set them in `labels`.

Use only facts the person gave you or that are on their existing pages. A fact you worked out yourself, such as
a client's name read from a file name, may be used, but tell the person it was inferred so they can confirm it.

Where a fact is missing, write a slot in square brackets (`[year]`, `[team size]`, `[what shipped]`). Slots
appear on the site exactly as written and the build lists every one, so:

- Keep the headline free of slots: write it from what you do know. A slot in the first sentence is the first
  thing a visitor reads.
- If a whole field is unknown and optional (`city`, `team`, `site.url`), leave the field out instead.
- For work with no outcome, say the true thing: "Shipped in 2024; I do not have the numbers", "Concept, not
  launched". That is a result. An empty promise of impact is not.
- A site with slots is a draft. Say so plainly at hand-over.

A portfolio with an honest gap is fine. A portfolio with an invented client is a problem in an interview.

### 4. Set the look

In the `theme` block: light or dark, one accent colour, the typeface, corner radius, gap between images. If
the person has a brand or an existing site, take these from it. If they have nothing, choose a typeface and
accent that suit their work and say what you chose. Do not copy the look of the example or of any other
designer's site.

A typeface that is not on every device needs `font_url` to load it; naming it in `font` alone falls back to
the system font for most visitors. Either give both, or choose a stack of system fonts.

### 5. Build, look, fix

Run the build. If the person has not chosen a grid themselves, add `--compare`:

```bash
python3 scripts/build.py path/to/their-site/portfolio.json --compare
```

It also writes the same content in all three grids to a `compare/` folder, with a page that links them.
Show the person that page and let them pick. `compare/` is for choosing only: delete it before publishing.

Then look at it in a browser at desktop and phone width if you can: start
`python3 -m http.server` in the site folder (the `case` grid links to project folders, which need a server)
and check the first screen yourself: name, what they do, proof, a way to reach them, and a real piece of work,
without scrolling.

If you cannot open a browser, say so at hand-over, and at least keep the headline and proof to about 45 words
together, which is what fits above the first picture on a phone.

Work through the list the script printed. Fix what you can from the content (a missing role line, a heavy
image, a long headline). Hand the rest to the person as a short list of what only they can supply.

### 6. Hand over

Tell them: which grid and whether they chose it or you did (and that the other two are one word away, or in
`compare/` if you built it), what you wrote for the headline, what you left out, anything you inferred, the
slots still to fill, what the audit list still shows, and how to change things (edit `portfolio.json`, run the
build again). The folder is a complete static site: it can be published on any static host by uploading it as
it is.

Two things only they can supply, so ask for them here: the address the site will live at (`site.url`), and a
1200×630 picture for link previews (`site.share_image`); a crop of the first project's best picture does the
job.

## Images

- Export at 2000 px wide at most, as AVIF or WebP, under about 500 KB each. The build warns about heavier ones.
  JPEG, PNG and SVG work too.
- A smaller copy for phones is used automatically when the files are named as a pair: `shot-lg.jpg` in the
  content file and `shot-sm.jpg` beside it. An `.avif` with the same names is offered first to browsers that
  read it.
- Give each picture an `alt` that says what it shows. Without one the project title is used, which tells a
  search engine or an AI assistant very little. If you have not seen the pictures, say which piece each one
  is and ask the person to describe them.
- Short looping videos (`.mp4`, `.webm`) work as tiles. They play muted, only while on screen. Give them a
  `ratio`.

## What not to do

- Do not add an intro animation, a loader, a custom cursor or scroll effects that delay the content. The
  template shows the first screen at once on purpose.
- Do not hide project titles behind hover. Phones have no hover.
- Do not remove the dock, the small bar with the name and the email that appears once the contact block has
  scrolled away. A reviewer decides to write in the middle of a project, not at the end of the page.
- Do not pad thin work with process pictures (sticky notes, personas). One decision, said plainly, is worth
  more.
- Do not edit the generated HTML by hand: the next build overwrites it. Change the content file, or the
  template in `assets/template/` if the structure itself needs to change.
