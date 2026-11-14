# Exports every SVG <figure> of HTML pages laid out as <src>/<Group>/<Page>/cours.html into an image bank.
# BANK_URL=https://cdn.jsdelivr.net/gh/<user>/<repo>@main/ python3 build_bank.py <src> <bank dir> [Group/Page ...]
# Sans liste de cours : tous les cours. Ne supprime jamais rien : chaque schéma porte
# l'empreinte de son contenu dans son nom (figNN-xxxxxxxx.svg), un schéma modifié donne un nouveau fichier.
import asyncio, hashlib, json, os, re, sys
from playwright.async_api import async_playwright

import os as _o
BASE = _o.environ.get('BANK_URL', 'https://cdn.jsdelivr.net/gh/<user>/<repo>@main/')
JS = r"""() => {
  const out = [];
  const figs = [...document.querySelectorAll('figure')];
  const props = ['fill','stroke','stroke-width','stroke-dasharray','stroke-linecap','stroke-linejoin','opacity','fill-opacity','stroke-opacity','font-size','font-weight','font-style','text-anchor','dominant-baseline','marker-end','marker-start','paint-order','letter-spacing'];
  const dflt = {opacity:'1','fill-opacity':'1','stroke-opacity':'1','font-style':'normal','stroke-dasharray':'none','marker-end':'none','marker-start':'none','stroke-linecap':'butt','stroke-linejoin':'miter','dominant-baseline':'auto','text-anchor':'start','paint-order':'normal','letter-spacing':'normal'};
  figs.forEach((fig, i) => {
    const src = fig.querySelector('svg');
    const cap = ((fig.querySelector('figcaption') || {}).textContent || '').replace(/\s+/g, ' ').trim();
    if (!src || src.querySelector('image') || fig.querySelector('img')) { out.push({n: i, skip: src ? 'image dans le svg' : 'pas de svg', cap}); return; }
    const clone = src.cloneNode(true);
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
    const vb = (src.getAttribute('viewBox') || '0 0 680 400').trim().split(/[\s,]+/).map(Number);
    const bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    bg.setAttribute('x', vb[0]); bg.setAttribute('y', vb[1]); bg.setAttribute('width', vb[2]); bg.setAttribute('height', vb[3]);
    bg.setAttribute('rx', '14'); bg.setAttribute('fill', '#ffffff');
    clone.insertBefore(bg, clone.firstChild);
    clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    clone.setAttribute('font-family', '-apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif');
    clone.setAttribute('width', vb[2]); clone.setAttribute('height', vb[3]);
    for (const a of ['class', 'aria-hidden']) clone.removeAttribute(a);
    clone.setAttribute('role', 'img');
    const svg = clone.outerHTML.replace(/\s+/g, ' ').replace(/(\d+\.\d{2})\d+/g, '$1');
    out.push({n: i, cap, svg});
  });
  const h1 = document.querySelector('h1');
  return {titre: (h1 ? h1.textContent : document.title).replace(/\s+/g, ' ').trim(), figs: out};
}"""


def readme_racine(dst, index):
    import collections
    mats = collections.OrderedDict()
    for k in sorted(index, key=lambda k: (k.split('/')[0], k.split('/')[1][:2], int(re.sub(r'\D', '', k.split('/')[1]) or 0))):
        m, c = k.split('/'); mats.setdefault(m, []).append((c, index[k]))
    total = sum(len(v['schemas']) for v in index.values())
    L = ['# Schémas de médecine en français 🩺', '',
     f'**{total} schémas clairs et colorés** pour la 1re année de médecine : physiologie, biochimie, biophysique, anatomie et embryologie. En français, libres d\'utilisation (CC BY 4.0). De nouveaux schémas arrivent après chaque cours.', '',
     'Chaque schéma répond à une question (« Où se place le potentiel de repos, et pourquoi ? ») et se lit en quelques secondes : des couleurs qui ont un sens, des flèches, des étiquettes posées sur le dessin.', '', '<p align="center">']
    for k in ['Biophysique/TP5', 'Biochimie/CM2', 'Physiologie/CM2', 'Anatomie/CM2']:
        s = index.get(k, {}).get('schemas', [])
        if s: L.append(f'<img src="{s[min(4, len(s) - 1)]["fichier"]}" alt="{s[min(4, len(s) - 1)]["legende"]}" width="48%">')
    L += ['</p>', '', '## Par matière', '']
    for m, cs in mats.items():
        L += [f'### {m} ({sum(len(v["schemas"]) for _, v in cs)} schémas)', '']
        L += [f'- [{c} · {v["titre"]}]({m}/{c}/) : {len(v["schemas"])} schémas' for c, v in cs] + ['']
    L += ['## D\'où viennent-ils ?', '', 'Ils sont tirés de cours « optimisés » : pour chaque cours ou TP, Claude (l\'IA d\'Anthropic) croise l\'enregistrement du cours, les notes et les diapos, puis fait une page de révision illustrée. Les schémas en sont extraits automatiquement chaque soir, en SVG.', '',
     'Ils suivent les cours d\'une faculté francophone : vérifie toujours avec ton propre cours, ton prof a le dernier mot. Une erreur ? Ouvre une *issue*.', '',
     '## Les utiliser', '', '- **Dans un document ou une page web** : chaque schéma est un fichier `.svg`, net à toutes les tailles.',
     '- **Dans une conversation avec Claude** : `<img src="https://cdn.jsdelivr.net/gh/alxhe3-lab/schemas-medecine@main/<chemin>" style="max-width:100%">` dans l\'outil de dessin du chat. Voir [le guide](https://github.com/alxhe3-lab/claude-explain-like-chatgpt/blob/main/docs/images-inline.md).',
     '- `index.json` liste tous les schémas : matière, cours, légende, adresse.', '', '## Licence', '',
     '[Creative Commons BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.fr) : copie, modifie et partage librement, en citant « schemas-medecine, alxhe3-lab ».', '',
     'Si ça t\'aide pour tes révisions, une ⭐ aide d\'autres étudiants à trouver le dépôt.', '', '---', '',
     f'*{total} diagrams for first-year medical students, in French, updated after every lecture. Free to use (CC BY 4.0).*', '']
    open(os.path.join(dst, 'README.md'), 'w', encoding='utf-8').write('\n'.join(L))

async def main():
    src, dst = sys.argv[1], sys.argv[2]
    wanted = set(sys.argv[3:])
    cours = []
    for mat in sorted(os.listdir(src)):
        d = os.path.join(src, mat)
        if not os.path.isdir(d) or mat.startswith(('_', '.')): continue
        for c in sorted(os.listdir(d), key=lambda x: (x[:2], int(re.sub(r'\D', '', x) or 0))):
            f = os.path.join(d, c, 'cours.html')
            if os.path.isfile(f) and (not wanted or f'{mat}/{c}' in wanted): cours.append((mat, c, f))
    index_path = os.path.join(dst, 'index.json')
    index = json.load(open(index_path, encoding='utf-8')) if os.path.exists(index_path) else {}
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1100, 'height': 900})
        for mat, c, f in cours:
            await pg.goto('file://' + os.path.abspath(f))
            res = await pg.evaluate(JS)
            os.makedirs(os.path.join(dst, mat, c), exist_ok=True)
            figs = []
            for fg in res['figs']:
                if 'svg' not in fg: continue
                h = hashlib.sha1(fg['svg'].encode()).hexdigest()[:8]
                name = f"fig{fg['n']:02d}-{h}.svg"
                path = os.path.join(dst, mat, c, name)
                if not os.path.exists(path): open(path, 'w', encoding='utf-8').write(fg['svg'])
                figs.append({'n': fg['n'], 'legende': fg['cap'], 'fichier': f'{mat}/{c}/{name}', 'url': BASE + f'{mat}/{c}/{name}', 'octets': len(fg['svg'])})
            index[f'{mat}/{c}'] = {'titre': res['titre'], 'schemas': figs, 'ignores': [x['n'] for x in res['figs'] if 'svg' not in x]}
            lines = [f'# {res["titre"]}', '', f'{len(figs)} schémas. Pour en afficher un dans le chat : `<img src="URL" style="max-width:100%">`.', '']
            for x in figs:
                lines += [f'## {x["n"]}. {x["legende"] or "(sans légende)"}', '', f'![{x["legende"]}]({os.path.basename(x["fichier"])})', '', f'`{x["url"]}`', '']
            open(os.path.join(dst, mat, c, 'README.md'), 'w', encoding='utf-8').write('\n'.join(lines))
            print(f'{mat}/{c}: {len(figs)} schémas, {len(res["figs"]) - len(figs)} ignorés')
        await b.close()
    json.dump(index, open(index_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

asyncio.run(main())
