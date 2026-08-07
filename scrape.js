// unegui.mn-ээс зар татах — Browser pane-ийн javascript_tool дотор ажиллуулна.
// ЧУХАЛ: эхлээд unegui.mn-ийг browser tab-д нээсэн байх ёстой (same-origin fetch ашигладаг).
// KIND='sale' эсвэл KIND='rent' гэж эхний мөрийг сольж 2 удаа ажиллуулна.
// Үр дүн нь том тул tool result файлд хадгалагдана — тэр файлыг README-ийн parse_result.py-аар боловсруулна.
(async () => {
  const KIND = 'sale'; // 'sale' | 'rent'
  const CATS = {
    sale: {
      'han-uul': 'https://www.unegui.mn/l-hdlh/l-hdlh-zarna/oron-suuts-zarna/ub-hanuul/',
      'bayanzurkh': 'https://www.unegui.mn/l-hdlh/l-hdlh-zarna/oron-suuts-zarna/ub-bayanzrh/',
      'bayangol': 'https://www.unegui.mn/l-hdlh/l-hdlh-zarna/oron-suuts-zarna/ub-bayangol/',
      'sukhbaatar': 'https://www.unegui.mn/l-hdlh/l-hdlh-zarna/oron-suuts-zarna/ulan-bator/?cities=1',
      'songinokhairkhan': 'https://www.unegui.mn/l-hdlh/l-hdlh-zarna/oron-suuts-zarna/ub-songinohajrhan/',
      'chingeltei': 'https://www.unegui.mn/l-hdlh/l-hdlh-zarna/oron-suuts-zarna/ub-chingeltej/',
    },
    rent: {
      'han-uul': 'https://www.unegui.mn/l-hdlh/l-hdlh-treesllne/oron-suuts/ub-hanuul/',
      'bayanzurkh': 'https://www.unegui.mn/l-hdlh/l-hdlh-treesllne/oron-suuts/ub-bayanzrh/',
      'bayangol': 'https://www.unegui.mn/l-hdlh/l-hdlh-treesllne/oron-suuts/ub-bayangol/',
      'sukhbaatar': 'https://www.unegui.mn/l-hdlh/l-hdlh-treesllne/oron-suuts/ulan-bator/?cities=1',
      'songinokhairkhan': 'https://www.unegui.mn/l-hdlh/l-hdlh-treesllne/oron-suuts/ub-songinohajrhan/',
      'chingeltei': 'https://www.unegui.mn/l-hdlh/l-hdlh-treesllne/oron-suuts/ub-chingeltej/',
    },
  };
  const out = [];
  for (const [d, base] of Object.entries(CATS[KIND])) {
    for (let p = 1; p <= 2; p++) {
      const url = p === 1 ? base : base + (base.includes('?') ? '&' : '?') + 'page=' + p;
      const res = await fetch(url, { credentials: 'include' });
      const doc = new DOMParser().parseFromString(await res.text(), 'text/html');
      doc.querySelectorAll('.advert.js-item-listing').forEach(ad => {
        const g = s => (ad.querySelector(s)?.textContent || '').replace(/\s+/g, ' ').trim();
        const href = ad.querySelector('a.advert__content-title')?.getAttribute('href') || '';
        out.push([d, g('.advert__content-price span'), g('.advert__content-title').slice(0, 90), g('.advert__content-place'), href.slice(0, 60)]);
      });
      await new Promise(r => setTimeout(r, 400)); // сайтад ачаалал өгөхгүй
    }
  }
  return JSON.stringify(out);
})()
