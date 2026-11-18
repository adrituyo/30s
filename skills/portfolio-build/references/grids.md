# The three grids

Each grid is a different answer to the same question: in 30 seconds, what does this kind of work need the
reviewer to see? Set it with `"layout"` in `portfolio.json`. Switching later means changing that one word.

| `layout` | In one line | Best for |
|---|---|---|
| `index` | Who you are stays fixed on the left; work runs large on the right | Art direction, brand, 3D, illustration, mixed visual work |
| `columns` | A short header, then every piece the same size, two across | Film, motion, photography, any work made of many equal pieces |
| `case` | A big statement, one card per project, one page to read per project | Product and UX design, design leadership, strategy |

## `index`: profile beside the work

**What the reviewer gets.** On a desktop the first screen shows both halves of the answer at once: on the
left, a card with the name, role, headline, proof and email; on the right, the first project at full size. The
card stays in place while the work scrolls, so the reviewer never loses track of whose work it is or how to
write to them. Under the card, a numbered list of projects shows how much there is and jumps to any of them.

**How the work is laid out.** Each project is a section on the same page: a thin header (number, title, role
line, one-line summary, tags) and then rows of one, two or three pictures at their own proportions. Decision
notes and before/after pairs sit between rows. Clicking a picture opens it whole.

**On a phone.** The card comes first, then the work in one column. Keep the headline and proof short, or the
card pushes the first picture off the first screen.

**Choose it when** the pictures carry the argument and a line of text per project is enough. It suits four to
eight projects of five to ten pictures each.

**Avoid it when** each project needs paragraphs of explanation (use `case`), or when there are forty similar
pieces (use `columns`).

## `columns`: an even grid

**What the reviewer gets.** A compact header across the top (name and role, headline, contact) and then work
straight away, two pieces across, all cropped to one proportion. Nothing is bigger than anything else, so the
eye reads it as a body of work and compares pieces easily.

**How the work is laid out.** Projects are sections with the same thin header as `index`; inside each, every
picture or video becomes one tile. The proportion is set once in the theme (`"ratio": "16/9"` for film,
`"4/3"` or `"1/1"` for stills) and can be changed per project. Tiles are cropped to fit, so choose a
proportion close to the material.

**On a phone.** One column, same order.

**Choose it when** the pieces are of one kind and roughly equal weight: a reel broken into films, a
photography series, a set of posters, motion loops. It is also the right grid for a side discipline published
as its own site.

**Avoid it when** one hero image per project matters more than the set, or when pieces have very different
proportions (tall phone screens beside wide banners will be cropped badly).

## `case`: one project, one page

**What the reviewer gets.** The home page opens with the headline as a large statement and the proof under
it, then one card per project: a wide cover, the title, the role line, the summary and the result. A reviewer
can read the result of every project without opening any. Each card leads to a page for that project.

**How a project page is laid out.** Title and summary; a row of four facts (role, team, year, for whom); the
decision in large type; the pictures, with notes and before/after pairs between them; what changed; a link to
the next project. Text sits in a narrow column for reading and pictures run wider.

**On a phone.** The same, in one column. The statement and the first cover both fit on the first screen if the
headline stays under about 25 words.

**Choose it when** the person is hired for reasoning or scope: product and UX designers, design leads and
heads of design, researchers, strategists. This is the grid where role, decision and result are required: the
build flags every project that lacks them.

**Avoid it when** there is nothing to say beyond the pictures. Empty fact rows and one-line pages make strong
visual work look thin; use `index`.

## Choosing quickly

1. Is the person hired for decisions and outcomes (product, UX, leadership)? → `case`
2. Is the work many pieces of one kind (film, photo, motion, posters)? → `columns`
3. Otherwise → `index`

When two fit, pick by the target, not by the past: a brand designer applying for a head of design role should
use `case`, because the role is judged on scope and decisions.

## What all three share

- The first screen says who, what and at what level, and shows a way to reach the person.
- Every project shows its title, a summary and a role line without hover or click.
- The page ends with plain facts, one ask and the email in large type.
- **The dock.** Between those two points the name, the role and the email follow the visitor in a small bar
  at the bottom of the screen. It appears when the contact block scrolls out of view and steps aside at the
  end of the page, where the email is already there in large type. In `index` on a desktop the profile card
  never leaves, so the dock never shows; on a phone, and in the other two grids, it does. It needs
  `person.email`.
- Titles, descriptions, share tags, structured data and a sitemap are written for search engines and AI
  assistants.
- Nothing waits on an animation: what is on the first screen appears at once.
