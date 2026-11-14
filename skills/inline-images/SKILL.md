---
name: inline-images
description: Use whenever an answer includes images, diagrams or figures. Places each visual right under the sentence it illustrates, in the chat, instead of attachments piled up at the end.
---

# Inline images: every visual in its place

When Claude sends images as **file attachments**, the app decides where they go, usually all at the end. The reader no longer knows which image goes with which paragraph.

Only two things appear **exactly where Claude calls them**: the chat's drawing tool (the Visualizer, `show_widget`) and image search. This skill uses them.

## 1. The rule (blocking)

- Every visual appears right under the sentence it illustrates. Never grouped at the end.
- Never send a visual as an attachment inside an explanation.
- Work order:
  1. Prepare all visuals first, silently (find URLs, copy SVGs, run searches).
  2. Then write the answer piece by piece: text of a part → the call that displays its visual → text of the next part.
- If your environment only shows text sent through a messaging tool (for example `SendUserMessage`), send each piece of text with it, otherwise the text between tool calls may be hidden.
- Before each visual, one short line introduces it. After it, one line: 👀 **What to look at:** …

## 2. Where the visual comes from (first that exists)

**A. An image hosted in a public GitHub repo (fastest).** In `show_widget`, HTML mode, a single line:

```html
<img src="https://cdn.jsdelivr.net/gh/<user>/<repo>@main/<path>.svg" alt="<caption>" style="max-width:100%;border-radius:12px">
```

- jsDelivr is one of the few hosts the Visualizer accepts; it serves public repos only.
- Copy the URL exactly from the bank's index (`index.json` or a `README.md` per chapter).
- SVG or PNG both work. Give SVGs a white background inside the file (the chat may be dark).

**B. An SVG diagram from the user's own HTML pages, copied as is.** Use `scripts/figure_to_chat.py`: list the figures, export one as a standalone SVG with its colors inlined, then display it in `show_widget` inside `<div style="background:#fff;border-radius:12px;padding:8px 4px">…</div>`. Slower (Claude rewrites the SVG, 3 to 10 KB), but no redraw.

**C. Image search** (displays in place). Pick the simplest image; translate foreign labels under it.

**D. A diagram drawn from scratch** with the Visualizer: shapes that show the mechanism, 2 or 3 meaningful colors, at most 6 short labels.

**Never:** an attachment in the middle of an answer; all visuals at the end; a diagram typed in a code block or ASCII; copyrighted figures (textbooks, slides) uploaded to a public repo — redraw them instead (D).

## 3. Building an image bank (once, then automatic)

1. Put the diagrams in a public repo, one folder per chapter.
2. Name each file with a hash of its content (`fig06-6ba08680.svg`): a changed diagram gets a new name, so the CDN never serves an old version.
3. Keep an index with each diagram's caption and URL. `scripts/build_bank.py` does steps 2 and 3 from HTML pages that contain SVG figures.
4. Add new diagrams automatically (a scheduled task that runs the script and pushes).

## 4. Check before sending

1. Each visual sits right under the sentence it illustrates.
2. No attachment, nothing grouped at the end.
3. Every URL was copied from the index, not invented.
