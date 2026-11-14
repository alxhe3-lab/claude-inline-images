# claude-inline-images

I study medicine and I use Claude a lot to explain my courses. One thing kept annoying me: when Claude added diagrams to an explanation, they all showed up at the very end of the answer. So I'd read three paragraphs, scroll down, and have no idea which picture went with what.

After a few evenings of testing, I found a way to get each image exactly where it should be, right under the sentence it explains. This repo is that method, plus the skill and the scripts I use.

<p align="center"><img src="examples/example.svg" alt="Before: images at the end. After: each image under its sentence." width="560"></p>

## Why the images end up at the end

When Claude sends an image as a file, the app decides where to put it, and it's usually at the bottom. The only things that show up exactly where Claude puts them are drawings made with the chat's visual tool (the "Visualizer") and image search results.

So the idea is simple: send every image through the Visualizer.

## What I tried

- Images sent as files: always at the end. Useless for explanations.
- Claude redrawing every diagram in the Visualizer: works, but slow, and my course diagrams are complicated.
- Pasting my own SVG diagrams into the Visualizer: works, but Claude has to rewrite the whole file each time (20 to 40 seconds per diagram).
- Embedding the image as base64: works, but way too heavy for a real figure.
- A plain `<img>` tag pointing to my diagrams on GitHub through jsDelivr: works, shows up instantly, one line per image. That's the one I kept.

The Visualizer blocks almost every image host, but `cdn.jsdelivr.net` is allowed, and it serves any file from a public GitHub repo.

## How to do it

1. Put your diagrams (SVG or PNG) in a public GitHub repo. If they're SVGs, give them a white background inside the file, otherwise they're hard to read in dark mode.
2. Put a short hash of the content in each file name (`fig06-6ba08680.svg`). If you change a diagram, it gets a new name, so you never get an old cached version.
3. Keep an index with the caption and the link of each diagram, so Claude can pick the right one.
4. Install the [`inline-images`](skills/inline-images/SKILL.md) skill. Claude then writes a part, shows its diagram with one line like this, and continues:

```html
<img src="https://cdn.jsdelivr.net/gh/<user>/<repo>@main/<chapter>/fig06-6ba08680.svg" style="max-width:100%;border-radius:12px">
```

My own diagram bank, built this way: [schemas-medecine](https://github.com/alxhe3-lab/schemas-medecine).

## What's in the repo

- `skills/inline-images/SKILL.md`: the skill (each image in its place, never as a file, where to take images from).
- `skills/inline-images/scripts/figure_to_chat.py`: grabs one SVG diagram from an HTML page, colors included.
- `skills/inline-images/scripts/build_bank.py`: turns a folder of HTML pages into a full diagram bank (hashed names, `index.json`, a README per page).

The scripts need `pip install playwright` and `playwright install chromium`.

To install the skill in the Claude app, download `inline-images.zip` from [Releases](../../releases) and upload it in Settings → Skills. With Claude Code, copy the folder into `~/.claude/skills/`.

## Limits

The repo has to be public, since jsDelivr only serves public repos. So don't put textbook figures or your teachers' slides in it; redraw those instead. I tested all this in November 2026, so it may change if the app changes its rules.

If it saves you some scrolling, a star is appreciated.

---

**En français.** Quand Claude met des schémas dans une explication, ils arrivent souvent tous à la fin. La solution que j'ai trouvée : mettre ses schémas sur un dépôt GitHub public et les faire afficher par l'outil de dessin du chat avec une simple balise `<img>` qui passe par jsDelivr. Chaque image s'affiche alors juste sous la phrase qu'elle explique. Le skill et les scripts sont dans le dépôt.
