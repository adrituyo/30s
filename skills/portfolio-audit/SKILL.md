---
name: portfolio-audit
description: Audits a design portfolio the way a hiring manager or client actually reads it, in a first pass of about 30 seconds, and returns what they would understand, what they would miss, and the fixes that matter most, with rewritten copy. Use this whenever someone shares a portfolio URL or portfolio files and asks for a review, critique, roast, feedback, a second opinion, "why am I not getting interviews or clients", "is my portfolio good enough", "what would a recruiter think", or help improving a personal site, case study page or showreel page before applying for a role or pitching a client, even if they never say the word "audit". Works for designers, art directors, design leads, illustrators, motion and 3D artists, photographers and design engineers.
---

# Portfolio audit: the 30-second test

The first pass over a portfolio is short. A reviewer with forty tabs open decides in well under a minute
whether this one gets a real look. Only the people who pass that filter get the five or ten careful minutes
that follow. So the audit asks one question before any other: **what does a stranger understand in 30 seconds,
and is it enough to keep them reading?**

You are not judging taste. Plenty of beautiful portfolios fail this test and plenty of plain ones pass it.
You are judging whether the page communicates: who this is, what they do, at what level, for whom, and how to
reach them.

## What you need before you start

- **The portfolio.** A URL, or local files.
- **The target.** The role or client the portfolio is aimed at ("senior product designer at a fintech",
  "freelance brand work for restaurants"). Every rule is judged against it, because a portfolio is only good
  *for something*. If the person did not say, infer the most likely target from the first sentence of the page,
  state your assumption in the report, and carry on. Do not stop to ask.

## How to run it

Paths below are relative to this skill's folder.

### 1. Collect facts first

Run the bundled script on the home page, the first project page if there is one, and the about page if there
is one. It reports what is actually in the pages so you do not guess:

```bash
python3 scripts/snapshot.py https://example.com https://example.com/first-project https://example.com/about
python3 scripts/snapshot.py --text https://example.com/first-project     # the readable text of a page
```

The snapshot gives the title, description, share card (with its real size), headings, the first words a
visitor reads, images, contact links, structured data, script weight, and whether `robots.txt`, `sitemap.xml`
and `llms.txt` exist. It also flags contradictions it can see, such as a different number of years in the
description and on the page.

Read its notes carefully:

- **Empty shell** (no text at all in the HTML): the page is drawn by JavaScript. That is a real finding for
  rule 15. Everything else about the content is *unknown*, not missing, until you see the page in a browser or
  in screenshots. Without either, mark the rules that depend on content as not checked instead of digging
  through script bundles.
- **Very little text**: the page is in the HTML but sparse (a canvas, a single statement). Counts of images
  mean little here; look at the page.

Read the about page. Facts that would pass the first screen (years, employers, team size, a statement of
authorship) are often written there and nowhere a 30-second visitor looks. That gap is one of the most useful
things an audit can find.

### 2. Look at the first screen

If you have a browser or screenshot tool, capture the first screen at desktop size (about 1440×900) and at
phone size (about 390×844) **without scrolling**, after the page has settled. This is the most important
evidence. If the person gave you screenshots, use them the same way.

If a screenshot and the HTML disagree (the HTML has a headline, the capture shows an empty screen), suspect
the capture: entrance animations and lazy loading often leave a first capture blank. Capture again if you can.
If you cannot, report both and say which one you trust, and do not fail a rule on a capture you doubt.

If you have no way to see the page, say so at the top of the report: the audit is based on text and code, and
layout, hierarchy and image quality were not seen.

### 3. Walk it like a reviewer

Follow the path a reviewer follows, and note what you learn at each step, not what you could find by digging:

| Seconds | What the reviewer does | What they should come away with |
|---|---|---|
| 0–5 | Reads the first screen | Who this is, what they do, at what level |
| 5–15 | Scrolls and scans | Real work, the best of it first, and what kind of work it is |
| 15–30 | Opens or stops at one project | What this person's part was, and one thing they decided |
| Exit | Leaves or acts | One obvious way to get in touch, and a reason to |

For the third step, use the first project the page offers:

- **A project page:** open it and judge its first screen.
- **A one-page site** (sections, a grid, a lightbox): the first section or tile *is* the project. Judge what
  it says where it stands. Having no project pages is not a failure in itself; having nowhere that says role,
  decision or result is.
- **A canvas, horizontal or single-screen site:** "one scroll away" becomes "one obvious gesture away".
- **A link to an outside product or shop:** note where it goes, then use the first project on the site itself.

### 4. Check against the rules

Read `references/rules.md` and mark each rule:

- **Pass**: a reviewer gets what the rule is for. If you are hesitating between Pass and Weak and the page
  communicates, it is a Pass. A page that breaks the letter of a rule and still communicates passes.
- **Weak**: a reviewer would notice the gap, and it costs something.
- **Fail**: the thing is absent, or it actively works against the person.
- **Not checked**: you could not see what the rule needs. Never mark from assumption.

When you saw only part of what a rule needs (the phone's first screen but not the rest), mark it on what you
saw, add "(partly)" to the result, and list the unseen part under "Not checked". When desktop and phone
differ, the rule takes the worse of the two.

### 5. Write the report

Use the format below. Write in the language the person wrote to you in. Quote the page in its own language,
and write rewritten copy in the page's language too, since it is meant to be pasted in.

## Report format

```markdown
# 30-second audit: [name or site]

**Target:** [the role or client, and whether it was given or assumed]
**Verdict:** [one or two sentences. If they asked a yes/no question, answer it first. Then: would this pass
the first filter for that target, and why]
**Score:** [N] of 16 rules pass · [N] weak · [N] fail · [N] not checked ([N] partly)
**Based on:** [what you saw: live page in a browser, screenshots, HTML only]

## What a stranger understands in 30 seconds
| Question | What the page says |
|---|---|
| Who is this? | ... |
| What do they do? | ... |
| At what level? | ... |
| For whom? | ... |
| What was their part in the work? | ... |
| How do I reach them? | ... |

(Write what is actually communicated in that time. If it is not there, write "Not clear" and where you
eventually found it, if you did.)

## The three fixes that matter most
1. **[Fix]** · [why it costs them, in one sentence] · [the concrete change, with rewritten copy where it applies]
2. ...
3. ...

## All rules
| # | Rule | Result | Evidence |
|---|---|---|---|

## What already works
[Two or three things worth keeping, so they are not lost in the next redesign.]

## Not checked
[What you could not see, and how the person can check it themselves.]
```

The score counts rules; the verdict predicts what a reviewer does. They can differ: a well-known name or one
famous employer can carry a page past the filter with half the rules weak, and a tidy page can pass most rules
and still be aimed at nothing. When they differ, say why in the verdict.

## How to judge well

**Order fixes by what a reviewer loses, not by how easy they are.** A vague headline on the first screen
outweighs ten technical details further down. The three fixes should be the three that change the first
30 seconds most.

**Be specific enough to act on.** "Improve your headline" helps nobody. Quote the current one and write a
better one. The same goes for project intros and the contact line.

**Rewrite only with facts found on the site.** Any page of the site counts, and say where you found the fact.
When a better line needs something you do not know (years, a client, team size, a number), leave a slot in
square brackets, such as `[N] years` or `[client]`, and say what to fill in. Inventing a credential for
someone is the one mistake here that can really hurt them.

**Separate what you saw from what you infer.** "The phone layout stacks to one column" is an observation.
"Probably slow on mobile data" is an inference, and should be worded as one or left out.

**Flag contradictions.** Six years in one place and ten in another, two different job titles, a year that is
out of date. A reviewer who spots one stops trusting the rest. They belong under rule 3.

**Say so when the problem is the work, not the page.** Sometimes the honest answer to "is this good enough for
X" is that the portfolio shows no work of kind X. No headline fixes that. Say it plainly in the first fix,
then say what work would close the gap, and keep the presentation fixes for after.

**Weigh the rules by what the target is hired for.**

- *Product and UX designers* are hired on reasoning: role, decisions and outcomes carry the most weight.
- *Design leads, heads of design, managers* are hired on scope: team size, who they hired and grew, what
  shipped under them, how long. Beautiful solo work under a leadership headline reads as a mismatch, so rules
  3, 4 and 11 carry the most weight, and the first project should be one they led.
- *Illustrators, photographers, 3D and motion artists, art directors* are hired on the work itself: image
  quality, editing and order carry it. A caption is enough; do not ask for a written case study.
- *Design engineers and creative developers:* the site itself is a piece of work. Credit its interaction and
  build quality as evidence, and expect the first sentence to say that they build, not only design.

**Be direct, and kind.** The person asked because something is not working. Say what is wrong plainly, then
say what to do. "Roast" and "be brutal" mean be blunt and skip the cushioning; they do not change the format,
and they are not a licence to sneer. The goal is that they fix it this week.

**Mind what a public ask reveals.** If the person has a job and the target is another job, do not write a
closing line that announces they are looking. Offer a neutral one ("Building a design team? Let's talk.").

**Do not redesign.** Typeface, colour and layout style are theirs. Comment on them only when they stop the
page from communicating: text that cannot be read, work that cannot be seen, navigation that cannot be found.

## When the input is unusual

- **A single case study or a PDF deck:** run steps 3 to 5 on it and skip the rules that only apply to a whole
  site. Count them as not checked.
- **A Behance, Dribbble, Read.cv or Notion page:** audit it the same way, and mention what the platform itself
  prevents (share card, own domain, structured data) separately from what the person can change.
- **A page that sells several things** (a job, freelance work, a course, a product): take the offer in the
  first sentence as the target, and count the rest against rule 11.
- **Password-protected work:** do not try to get around it. Note that a locked first project ends most
  30-second visits, and audit what is public.
- **Someone else's portfolio:** audit it if asked, as private feedback. It is still a person's work.
