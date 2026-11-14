# Copies an SVG diagram from an HTML study page, colors inlined, so Claude can display it in place in the chat.
# python3 figure_to_chat.py page.html            -> lists the figures (n, type, caption)
# python3 figure_to_chat.py page.html 5 fig.svg  -> writes figure 5 as a standalone SVG
# Needs: pip install playwright && playwright install chromium
import asyncio, sys, os
from playwright.async_api import async_playwright
JS = r"""(i) => {
  const figs = [...document.querySelectorAll('figure')];
  if (i < 0) return figs.map((f, k) => k + ' | ' + (f.querySelector('svg') ? 'svg' : (f.querySelector('img') ? 'image' : '?')) + ' | ' + ((f.querySelector('figcaption') || {}).textContent || '').trim().slice(0, 90)).join('\n');
  const src = figs[i].querySelector('svg'); if (!src) return 'NO SVG';
  const clone = src.cloneNode(true);
  const props = ['fill','stroke','stroke-width','stroke-dasharray','stroke-linecap','stroke-linejoin','opacity','fill-opacity','stroke-opacity','font-size','font-weight','font-style','text-anchor','dominant-baseline','marker-end','marker-start','paint-order','letter-spacing'];
  const dflt = {opacity:'1','fill-opacity':'1','stroke-opacity':'1','font-style':'normal','stroke-dasharray':'none','marker-end':'none','marker-start':'none','stroke-linecap':'butt','stroke-linejoin':'miter','dominant-baseline':'auto','text-anchor':'start','paint-order':'normal','letter-spacing':'normal'};
  const S = [src, ...src.querySelectorAll('*')], C = [clone, ...clone.querySelectorAll('*')];
  S.forEach((el, k) => {
    const cs = getComputedStyle(el), c = C[k], txt = el.tagName === 'text' || el.tagName === 'tspan';
    let st = '';
    for (const p of props) {
      if (!txt && p.startsWith('font')) continue;
      const v = cs.getPropertyValue(p);
      if (!v || dflt[p] === v) continue;
      st += p + ':' + v + ';';
    }
    c.removeAttribute('class');
    for (const a of ['fill','stroke','stroke-width']) if ((c.getAttribute(a) || '').startsWith('var(')) c.removeAttribute(a);
    if (st) c.setAttribute('style', st);
  });
  clone.setAttribute('font-family', '-apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif');
  clone.setAttribute('width', '100%'); clone.removeAttribute('height');
  return clone.outerHTML.replace(/\s+/g, ' ').replace(/(\d+\.\d{2})\d+/g, '$1');
}"""
async def main():
    path = os.path.abspath(sys.argv[1]); i = int(sys.argv[2]) if len(sys.argv) > 2 else -1
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1100, 'height': 900})
        await pg.goto('file://' + path)
        res = await pg.evaluate(JS, i)
        await b.close()
    if i < 0: print(res); return
    open(sys.argv[3], 'w', encoding='utf-8').write(res); print('bytes', len(res))
asyncio.run(main())
