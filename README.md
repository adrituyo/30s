# Portfolio skills

Agent skills for designers' portfolios. The first pass over a portfolio lasts well under a minute; these
skills make yours easy to take in and easy to understand in that time.

## Skills

| Skill | What it does |
|---|---|
| `portfolio-audit` | Reads a portfolio the way a reviewer does in 30 seconds and returns what they understand, what they miss and the three fixes that matter most, with rewritten copy. |
| `portfolio-build` | Builds a portfolio from one content file and one of three grids (`index`, `columns`, `case`), then lists what the audit would still flag. |

## Use

Install:

```
npx skills@latest add adrituyo/portfolio-skills
```

Then give your agent a URL:

```
audit my portfolio https://example.com, I'm applying for senior product designer roles
```

## Build

```
python3 skills/portfolio-build/scripts/build.py path/to/portfolio.json
```

Start from `skills/portfolio-build/assets/example/portfolio.json`.

## Layout

```
skills/
├── portfolio-audit/
│   ├── SKILL.md              how the audit runs and the report format
│   ├── references/rules.md   the 16 rules, each with its reason, check and fix
│   └── scripts/snapshot.py   facts about a page (title, share card, first words, images, structured data)
└── portfolio-build/
    ├── SKILL.md              the steps: target, grid, content file, look, build
    ├── references/           the three grids, every field of the content file, the rules in one line each
    ├── scripts/build.py      content file in, static site out, plus what the audit would still flag
    └── assets/               the template (CSS and JS) and a neutral example
site/                         the page that presents the skills
```

## Credit

Several rules build on Karl's ([@_kejk](https://x.com/_kejk)) writing on portfolios.

## License

MIT. See `LICENSE`.
