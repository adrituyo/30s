# Portfolio Skills — your portfolio gets 30 seconds

> Two skills for AI agents, by Owi (Head of Design at Tuyo). One audits a design portfolio the way the person hiring reads it, in a first look of about 30 seconds. The other builds a portfolio that passes that look. 17 rules, 3 grids, free and open source (MIT).

- Page: https://30s.design/
- Source: https://github.com/adrituyo/portfolio-skills
- Install: `npx skills@latest add adrituyo/portfolio-skills`
- Works with: agents that load skills (Claude Code and others supported by the `skills` installer)

## The 30-second theory

Nobody spends more than 30 seconds on a portfolio the first time. Whoever is hiring has forty tabs open. The first look decides which ones get a real read, and it goes the same way every time:

| Seconds | What the reviewer does | What they are asking |
|---|---|---|
| 0–5 | Reads the first screen | Who is this, and at what level? |
| 5–15 | Scrolls and scans | Is the work real, and is the best of it first? |
| 15–30 | Stops at one project | What was their part, what did they decide, and what changed because of it? |

Then they leave, or they write to you. Both skills are built around those three moments.

## Portfolio Audit (`/portfolio-audit`)

Find out what a stranger takes from your portfolio in 30 seconds, and what to fix first.

Use it when you are about to apply and want to see it with fresh eyes, when you keep sending it and nobody writes back, or when you just redesigned it and can no longer tell if it works.

- **You say:** "Audit my portfolio: yourname.com. I'm applying for senior product roles."
- **It does:** looks at your first screen on desktop and on a phone; walks the page the way a reviewer does (first screen, scan, one project); marks the 17 rules against what it actually saw.
- **You get:** a verdict, a score (rules that pass, are weak, or fail), what a stranger understands in 30 seconds, the three fixes that matter most with the copy rewritten, what already works, what it could not check, and all 17 rules with the evidence from your page.

It never invents a fact about you. When a better headline needs a number it does not have, it leaves a slot such as `[N] years` or `[team size]`.

## The 17 rules

Grouped by the moment a reviewer meets them. None is about taste: a plain portfolio can pass all seventeen and a beautiful one can fail half.

### First screen (0–5 s): Who is this, and at what level?

1. **Say what you do, in one sentence.** A line that could not sit on anyone else's site.
2. **Show work on the first screen.** The claim needs evidence before the first scroll.
3. **Signal level and proof.** Years, names, numbers. Specific and checkable.

### The scan (5–15 s): Is the work real, and is the best of it first?

4. **Strongest, most relevant work first.** Most visitors see one project. Choose which.
5. **Few projects, each one edited.** You are judged by the weakest piece you show.
6. **Readable at a glance.** Title and one line, always visible. No hover.

### One project (15–30 s): What did this person actually do?

7. **Say what your part was.** Role, team, and client or personal concept.
8. **Show one decision.** What you chose and why, not the process you followed.
9. **Show the change.** Before and after, a result, or what shipped.

### The exit (after 30 s): How do I reach them, and for what?

10. **One clear ask, one way to reach you.** A visible email and a reason to write.
11. **Aimed at something.** After 30 seconds, hired for what?

### Everything around it (at any moment): Does anything get in the way?

12. **Works on a phone.** Links are opened from chats and feeds.
13. **Loads fast.** A slow first screen spends the 30 seconds on nothing.
14. **Shares well.** The preview card is seen before the page.
15. **Readable by machines.** Recruiters search, and ask AI assistants for names.
16. **No friction.** No passwords, loaders, dead links or cursor tricks.
17. **Always within reach.** Your name and your email stay on screen at every scroll.

The full rules, each with why it matters, how to check it and how to fix it: https://github.com/adrituyo/portfolio-skills/blob/main/skills/portfolio-audit/references/rules.md

## Portfolio Build (`/portfolio-build`)

Turn a folder of work and a few facts about you into a finished portfolio that already passes the 30 seconds.

Use it when you have the work and no site to show it, when the audit says the problem is the structure and not the copy, or when you want to see your work in another grid without starting over.

- **You say:** "Build my portfolio from this folder. I'm a product designer, aiming at senior fintech roles."
- **It does:** asks only for what it cannot find; shows you the three grids, says which it would pick and why, and builds the one you choose; writes the headline, proof and one line per project from your facts; sets the look from your brand (typeface, colour, corners, spacing).
- **You get:** a finished static site in a folder, with nothing to install. Change one content file and build again. It ends by listing, by rule number, what an audit would still flag.

## The three grids

| Grid | What it is | Best for | Seen in the first 5 seconds |
|---|---|---|---|
| Index | Your name, headline and email stay fixed on the left while the work scrolls large on the right. | Art direction, brand, 3D, illustration | Who you are and your first piece, side by side |
| Columns | A short header, then every piece at one size, two across. It reads as a body of work. | Film, motion, photography | Your line, then two pieces at once |
| Case | A large statement, one card per project with its result, and a page each for role, decision and outcome. | Product, UX, design leadership | Your statement at full size, then the first project |

## Credits

Made by Owi (https://theartofvisual.com, @owisixseven on X: https://x.com/owisixseven), Head of Design at Tuyo. Several rules build on Karl's (https://x.com/_kejk) writing on portfolios.
