// unegui.mn-ээс зар татах — Browser pane-ийн javascript_tool дотор ажиллуулна.
// ШААРДЛАГА: эхлээд unegui.mn-ийн аль нэг хуудас browser tab-д нээгдсэн байх (same-origin fetch).
//
// 2026-09 сайтын шинэчлэлтэд тохирсон хувилбар:
//  - Дүүргийн URL-ууд найдваргүй болсон тул ерөнхий ангиллын хуудсуудаар татаж,
//    дүүргийг зарын байршлын мөрөөс ("Улаанбаатар — Хан-Уул — Хүннү") гаргана.
//  - Үнийг schema.org [itemprop=offers] элементээс авна (зурагны "1/15" тоолууртай
//    наалдахаас сэргийлж) — textContent-ээс regex-ээр авч БОЛОХГҮЙ!
//  - Гаралтын мөр: [дүүрэг(монголоор), үнэ, гарчиг, place, href]
//    place формат хуучин хэвээр: "Дүүрэг, Дүүрэг, Хороо N" эсвэл "Дүүрэг, Хороолол"
//
// Хэрэглээ: KIND болон PAGES-ийг тохируулаад ажиллуулна. 30 сек timeout-д багтаахын
// тулд нэг дуудалтад ~7 хуудас; шаардлагатай бол PAGES-ийг хувааж 2 дуудалт хийнэ.
(async () => {
  const KIND = 'sale'; // 'sale' | 'rent'
  const PAGES = [1, 7]; // [эхлэх, дуусах] хуудас
  const BASE = KIND === 'sale'
    ? 'https://www.unegui.mn/l-hdlh/l-hdlh-zarna/oron-suuts-zarna/'
    : 'https://www.unegui.mn/l-hdlh/l-hdlh-treesllne/oron-suuts/';

  const parse = (doc) => {
    const out = [], seen = new Set();
    doc.querySelectorAll('li').forEach(li => {
      const a = li.querySelector('a[href^="/adv/"]');
      if (!a) return;
      const href = a.getAttribute('href');
      if (seen.has(href)) return;
      const priceEl = li.querySelector('[itemprop="offers"] span, [itemprop="price"]');
      const price = priceEl ? (priceEl.getAttribute('content') || priceEl.textContent).trim() : null;
      if (!price || !/₮/.test(price)) return;
      let locTxt = null;
      for (const e of li.querySelectorAll('*')) {
        const own = [...e.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join(' ').trim();
        if (own.includes('Улаанбаатар —') && own.length < 130) { locTxt = own; break; }
      }
      if (!locTxt) return;
      const lm = locTxt.match(/Улаанбаатар\s*—\s*([^—]+?)\s*—\s*(.+)$/);
      if (!lm) return;
      seen.add(href);
      let title = '';
      li.querySelectorAll('a[href^="/adv/"]').forEach(x => { const s = x.textContent.trim(); if (s.length > title.length) title = s; });
      const dist = lm[1].trim(), nb = lm[2].trim();
      const km = nb.match(/^(\d+)-р хороо/);
      const place = km ? `${dist}, ${dist}, Хороо ${km[1]}` : `${dist}, ${nb}`;
      out.push([dist, price, title.slice(0, 90), place, href.slice(0, 60)]);
    });
    return out;
  };

  const out = [];
  for (let p = PAGES[0]; p <= PAGES[1]; p++) {
    const url = BASE + (p > 1 ? '?page=' + p : '');
    const res = await fetch(url, { credentials: 'include' });
    const doc = new DOMParser().parseFromString(await res.text(), 'text/html');
    out.push(...parse(doc));
    await new Promise(r => setTimeout(r, 200));
  }
  return JSON.stringify(out);
})()
