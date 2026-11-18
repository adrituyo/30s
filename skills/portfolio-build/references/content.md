# The content file: `portfolio.json`

One file holds the whole portfolio. Paths to images are relative to the folder the file is in. Text fields
accept `**double asterisks**` for emphasis and `*single asterisks*` for the title of a work, nothing else.
A `[slot in brackets]` marks a fact still to come: it shows on the site as written and the build lists it. A complete example is in
`assets/example/portfolio.json`.

```json
{
  "layout": "index",
  "site":    { ... },
  "person":  { ... },
  "theme":   { ... },
  "authorship": "...",
  "ask": "...",
  "labels":  { ... },
  "facts": [ ["Based in", "Lisbon"], ... ],
  "projects": [ { ... }, ... ]
}
```

## `layout`

`"index"`, `"columns"` or `"case"`. See `grids.md`.

## `site`

| Field | What it is |
|---|---|
| `url` | The address the site will live at, such as `https://name.com`. Needed for the sitemap and share links. Leave it out until it is known. |
| `lang` | Language code of the text: `en`, `es`, `pt`… |
| `share_image` | A 1200×630 picture for link previews, as a path or full address. |
| `title` | Optional. The browser and search title. Built as `Name — Role, Employer (City)` if left out. |
| `description` | Optional. Built from the headline and proof if left out. |

## `person`

| Field | What it is |
|---|---|
| `name` | The name they work under. |
| `role` | Current role or what they are: "Senior Product Designer", "Art director". |
| `employer` | Optional. `{ "name": "...", "url": "..." }`. Shown as `Role @ Employer`. |
| `city` | Optional. Where they are based. |
| `photo` | Optional. A square portrait. |
| `email` | The one address to write to. Also shown in the dock, the bar that keeps name and contact on screen while the visitor scrolls. |
| `headline` | One sentence: what they make, for whom, with a fact. Rule 1. |
| `proof` | One or two sentences of names and numbers. Rule 3. |
| `links` | Up to three: `[ { "label": "LinkedIn", "url": "..." } ]`. The label is shown as written, so `"@handle"` works. More than three competes with the email. |

## `theme`

Everything here is optional. This block is the look; the rest of the file is the content.

| Field | What it is | Default |
|---|---|---|
| `mode` | `"dark"`, `"light"` or `"auto"` (follows the visitor's system) | `dark` |
| `accent` | One colour, used sparingly: the active item, hover on the email | near-white |
| `font` | CSS font family for text, such as `"Inter", system-ui, sans-serif` | system font |
| `mono` | CSS font family for small labels (numbers, role lines, tags), if they should differ from the text | the same as `font` |
| `font_url` | A stylesheet address that loads those fonts, if they are not system fonts | none |
| `radius` | Corner radius of pictures, in pixels. `0` for square corners | `14` |
| `gap` | Space between pictures, in pixels | `8` |
| `ratio` | `columns` layout only: the proportion every tile is cropped to, such as `"16/9"` | `4/3` |

## `authorship`, `ask`, `facts`

- `authorship`: one site-wide sentence on whose work this is, shown at the end of every page. It covers
  projects with no `role` of their own. Example: "I am the designer and author of every project here; where a
  team was involved, it is named."
- `ask`: one sentence above the email saying what to write for. Rule 10.
- `facts`: pairs shown as a plain list, for readers and for machines: based in, years of experience, clients
  or employers, focus, awards, what they are available for.
- `labels`: optional. Replaces the template's own words. English and Spanish are built in and chosen by
  `site.lang`; for another language give all of them: `skip`, `about`, `index`, `facts`, `authorship`,
  `decision`, `the_decision`, `result`, `before`, `after`, `personal`, `freelance`, `read`, `all`, `next`,
  `portrait`, `role`, `team`, `year`, `for`, `close`, `previous`, `contact`.

## `projects`

In the order they should be seen. Strongest and most relevant first.

| Field | What it is |
|---|---|
| `title` | The project name. |
| `id` | Optional. Short name used in addresses. Made from the title if left out. |
| `tags` | The kind of work: "Brand identity, Packaging". |
| `summary` | One line on what it is. Always visible. Rule 6. |
| `role` | Their part: "Lead designer", "Art direction and 3D". Rule 7. |
| `team` | "solo", "with 2 engineers", "team of 6". Also the place for credits: "art direction by …", "text by …". |
| `year` | When. |
| `client` | Who it was for, when it was client work. Free text: "Ledger Bank", "A friend's app, freelance". |
| `relationship` | Use when there is no `client` to name: `"personal"` for a self-initiated concept, `"employer"` for work done at their job, `"freelance"` for a client that cannot be named. Rule 7. |
| `decision` | One thing they chose and why. Shown in large type in the `case` layout. Rule 8. |
| `result` | What shipped or what changed. Shown on the home card and the project page in `case`. Rule 9. |
| `cover` | `case` layout only. The picture on the home card. If left out: the first picture, or the "after" of a before/after. Set it when the first picture is tall, since the card is wide. |
| `cover_ratio` | `case` layout only. Proportion of the home card picture, such as `1.78`. Between 1.6 and 2.2 by default. |
| `ratio` | `columns` layout only. Overrides the theme's tile proportion for this project. |
| `rows` | The body of the project, top to bottom. See below. |

### `rows`

Each entry is one row:

```json
"rows": [
  { "src": "images/hero.jpg", "alt": "Home screen with the new balance card" },
  [ "images/a.jpg", "images/b.jpg" ],
  { "note": "We kept two button styles instead of five, because every extra one doubled review time.", "label": "Decision" },
  { "before": "images/old.jpg", "after": "images/new.jpg", "caption": "Checkout" }
]
```

- **A picture:** a path, or `{ "src", "alt" }`. Fills the row. The `alt` is also the caption in the viewer.
- **Two or three pictures:** a list. They share the row at one height, each at its own proportions, so a tall
  cover beside a wide spread comes out narrow beside wide.
- **A note:** two lines of text between pictures. `label` defaults to "Decision".
- **Before and after:** two pictures of the same proportions with a slider between them. Each side can be a
  path or `{ "src", "alt" }`.
- **A video:** `{ "src": "images/loop.mp4", "ratio": 1.78, "alt": "..." }`. Give the proportion; it cannot be
  read from the file.

In the `columns` layout the rows are flattened: every picture becomes one equal tile and notes move to the top
of the project.
