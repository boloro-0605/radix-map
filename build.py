#!/usr/bin/env python3
"""УБ орон сууцны зураглал — дата боловсруулалт.

Оролт:  raw_sale.json, raw_rent.json — [[district, price, title, place, href], ...]
         (scrape.js-ийн үр дүн, худалдах/түрээсийн тус бүр 6 дүүрэг × 2 хуудас)
Гаралт: ub-realestate-map.html — template.html + embed хийсэн дата

Ажиллуулах: python3 build.py [хавтас]   (default: энэ файлын хавтас)
"""
import json, re, hashlib, statistics, sys, os
from datetime import date
from collections import defaultdict

BASE = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))

DIST_MN = {'sukhbaatar':'Сүхбаатар','han-uul':'Хан-Уул','bayanzurkh':'Баянзүрх',
           'bayangol':'Баянгол','songinokhairkhan':'Сонгинохайрхан','chingeltei':'Чингэлтэй'}

COORDS = {
 'Дөлгөөн нуур':(47.948,106.925),'Сүхбаатар, Хороо 11':(47.942,106.932),'11-р хороолол':(47.936,106.935),
 '100 айл':(47.930,106.927),'Сүхбаатар, Хороо 9':(47.945,106.918),'Сүхбаатар, Хороо 10':(47.938,106.922),
 'Сүхбаатар, Хороо 1':(47.912,106.923),'Сүхбаатар, Хороо 2':(47.914,106.930),'Сүхбаатар, Хороо 3':(47.917,106.928),
 'Сүхбаатар, Хороо 8':(47.921,106.930),'Сүхбаатар, Хороо 6':(47.918,106.918),'Сүхбаатар, Хороо 7':(47.923,106.921),
 'Сүхбаатар, Хороо 5':(47.920,106.925),'Сүхбаатар, Хороо 4':(47.919,106.932),
 'Орос 3-р сургуулийн ойролцоо':(47.920,106.912),'Америкын элчин сайдын яам':(47.925,106.935),'Бага тойрог':(47.919,106.920),
 'Яармаг':(47.868,106.785),'Хан-Уул, Хороо 11':(47.865,106.795),'Хан-Уул, Хороо 23':(47.852,106.768),
 'Нисэх':(47.850,106.765),'Хан-Уул, Хороо 15':(47.888,106.905),'Зайсан':(47.886,106.913),
 'River Garden':(47.893,106.930),'King Tower':(47.889,106.890),'Хан-Уул, Хороо 17':(47.878,106.870),
 'Хан-Уул, Хороо 3':(47.900,106.888),'Хан-Уул, Хороо 20':(47.880,106.858),'19-р хороолол':(47.900,106.895),
 'Хан-Уул, Хороо 16':(47.895,106.912),'Мишээл':(47.881,106.856),'Хан-Уул, Хороо 4':(47.897,106.878),
 'Хан-Уул, Хороо 2':(47.902,106.892),'Хан-Уул, Хороо 1':(47.905,106.898),'Хан-Уул, Хороо 8':(47.885,106.845),
 'Хан-Уул, Хороо 10':(47.870,106.800),'Хан-Уул, Хороо 21':(47.860,106.830),'Хан-Уул, Хороо 25':(47.848,106.760),
 'Хан-Уул, Хороо 12':(47.862,106.788),'Хан-Уул, Хороо 14':(47.890,106.940),'Буянт-Ухаа':(47.858,106.772),
 'Хан-Уул, Хороо 22':(47.875,106.930),'Хан-Уул, Хороо 24':(47.883,106.850),
 'Баянзүрх, Хороо 26':(47.916,106.958),'Сансар':(47.923,106.945),'13-р хороолол':(47.918,106.968),
 '16-р хороолол':(47.928,106.995),'Үндэсний цэцэрлэгт хүрээлэн':(47.902,106.948),'Офицеруудын ордон':(47.918,106.952),
 '15-р хороолол':(47.925,106.975),'Улиастай':(47.912,107.030),'Ботаник':(47.933,106.992),
 'Баянзүрх, Хороо 1':(47.920,106.955),'Баянзүрх, Хороо 3':(47.915,106.980),'Баянзүрх, Хороо 4':(47.922,106.940),
 'Баянзүрх, Хороо 6':(47.926,106.962),'Баянзүрх, Хороо 13':(47.930,106.955),'Баянзүрх, Хороо 14':(47.925,106.968),
 'Баянзүрх, Хороо 18':(47.930,106.948),'6 буудал':(47.940,106.960),'Шар хад':(47.945,106.975),
 'Баянзүрх, Хороо 33':(47.918,106.990),'Дүнжингарав':(47.908,106.985),'Цайз':(47.915,107.000),
 'Нарны хороолол':(47.908,106.858),'10-р хороолол':(47.921,106.858),'3, 4 хороолол':(47.916,106.878),
 'Модны 2':(47.906,106.848),'Алтай хотхон':(47.902,106.862),'Баянгол, Хороо 2':(47.918,106.868),
 'Баянгол, Хороо 24':(47.908,106.868),'Баянгол, Хороо 26':(47.905,106.842),'Баянгол, Хороо 20':(47.912,106.850),
 'Баянгол, Хороо 22':(47.910,106.845),'Баянгол, Хороо 11':(47.915,106.860),'Баянгол, Хороо 33':(47.912,106.838),
 'Гэмтлийн эмнэлэг':(47.919,106.850),'Төмөр зам':(47.905,106.870),'Ард Аюушийн өргөн чөлөө':(47.918,106.845),
 '21-р хороолол':(47.926,106.800),'1-р хороолол':(47.918,106.837),'5 шар':(47.923,106.825),
 'Сонгинохайрхан, Хороо 19':(47.930,106.775),'Толгойт':(47.933,106.770),'Баянхошуу':(47.952,106.858),
 'Сонгинохайрхан, Хороо 15':(47.928,106.790),'Сонгинохайрхан, Хороо 18':(47.925,106.812),
 'Зүүн салаа':(47.940,106.805),'Москва хороолол':(47.920,106.830),'Дархан хороолол':(47.916,106.842),
 'Баянбүрд':(47.926,106.903),'Чингэлтэй, Хороо 6':(47.930,106.912),'Чингэлтэй, Хороо 3':(47.923,106.908),
 'Чингэлтэй, Хороо 4':(47.925,106.910),'Тэнгис кино театр':(47.924,106.906),'40 мянгат':(47.921,106.913),
 '5-р сургуулийн ойролцоо':(47.928,106.900),'50-р сургуулийн ойролцоо':(47.931,106.897),
 'Чингэлтэй, Хороо 10':(47.940,106.898),'Чингэлтэй, Хороо 12':(47.945,106.895),'Хайлааст':(47.952,106.892),
 'Чингэлтэй, Хороо 1':(47.920,106.917),'Чингэлтэй, Хороо 2':(47.922,106.912),'Чингэлтэй, Хороо 5':(47.927,106.907),
 'Цирк':(47.9155,106.9145),'Жуковын музей':(47.918,106.947),'Хүннү':(47.860,106.792),
 'Улаанхуаран':(47.928,107.005),'Ханын материал':(47.935,106.955),'Баянмонгол хороолол':(47.914,106.872),
 'Гандан':(47.921,106.894),'Зурагт':(47.930,106.845),'Хармодон':(47.905,106.838),
}
DIST_DEFAULT = {'sukhbaatar':(47.925,106.926),'han-uul':(47.885,106.86),'bayanzurkh':(47.92,106.965),
 'bayangol':(47.912,106.86),'songinokhairkhan':(47.925,106.81),'chingeltei':(47.928,106.905)}


def parse_price(s):
    s2 = s.replace(',', '.')
    m = re.search(r'([\d.]+)\s*(сая|мян|[Тт]эрбум)', s2)
    if not m:
        return None
    v = float(m.group(1))
    if 'мян' in m.group(2):
        return v / 1000
    if 'эрбум' in m.group(2):
        return v * 1000
    return v


def parse_area(t):
    m = re.search(r'([\d.]+)\s*(?:м2|м²|мкв|m2|mkv|м\.кв|мк|m²)', t.replace(',', '.'), re.I)
    return float(m.group(1)) if m else None


def parse_rooms(t):
    m = re.search(r'(\d)\s*(?:өрөө|oroo|уруу)', t, re.I)
    return int(m.group(1)) if m else None


def coord_for(d, nb):
    if nb in COORDS:
        return COORDS[nb], True
    base = DIST_DEFAULT[d]
    h = int(hashlib.md5(nb.encode()).hexdigest(), 16)
    return (base[0] + ((h % 100) - 50) * 0.0002, base[1] + (((h // 100) % 100) - 50) * 0.0005), False


def process(raw, mode):
    out = []
    for d, price, title, place, href in raw:
        p = parse_price(price)
        a = parse_area(title)
        r = parse_rooms(title)
        nb = place.split(',', 1)[1].strip() if ',' in place else place
        if not p or not a or not (15 <= a <= 400):
            continue
        if mode == 's':
            if not (10 < p):
                continue
            ppm = round(p / a, 2)          # сая ₮/м²
            if not (1.0 < ppm < 20):
                continue
        else:
            if not (0.3 <= p <= 25):
                continue
            ppm = round(p * 1000 / a, 1)   # мянган ₮/м²/сар
            if not (10 <= ppm <= 120):
                continue
        (lat, lng), exact = coord_for(d, nb)
        out.append({'d': DIST_MN[d], 'nb': nb, 'lat': round(lat, 4), 'lng': round(lng, 4), 'x': exact,
                    'p': p, 'a': a, 'r': r, 'ppm': ppm, 't': title,
                    'u': 'https://www.unegui.mn' + href, 'm': mode})
    return out


def day_aggregates(combined, mode):
    rows = [l for l in combined if l['m'] == mode]
    if not rows:
        return None
    med = lambda v: round(statistics.median(v), 2)
    entry = {'city': [len(rows), med([l['ppm'] for l in rows])], 'dist': {}, 'nb': {}}
    by_d, by_nb = {}, {}
    for l in rows:
        by_d.setdefault(l['d'], []).append(l['ppm'])
        by_nb.setdefault(l['nb'], []).append(l['ppm'])
    for d, v in by_d.items():
        entry['dist'][d] = [len(v), med(v)]
    for nb, v in by_nb.items():
        if len(v) >= 3:
            entry['nb'][nb] = [len(v), med(v)]
    return entry


def update_history(combined):
    """Өдөр бүрийн медиан үзүүлэлтийг history.json-д хуримтлуулна (нэг өдөрт нэг бичлэг)."""
    path = os.path.join(BASE, 'history.json')
    history = json.load(open(path)) if os.path.exists(path) else []
    today = date.today().isoformat()
    history = [h for h in history if h['date'] != today]
    history.append({'date': today,
                    's': day_aggregates(combined, 's'),
                    'r': day_aggregates(combined, 'r')})
    history.sort(key=lambda h: h['date'])
    json.dump(history, open(path, 'w'), ensure_ascii=False)
    return history


def main():
    raw_sale = json.load(open(os.path.join(BASE, 'raw_sale.json')))
    raw_rent = json.load(open(os.path.join(BASE, 'raw_rent.json')))
    combined = process(raw_sale, 's') + process(raw_rent, 'r')
    history = update_history(combined)

    tpl = open(os.path.join(BASE, 'template.html')).read()
    embed = '<script>const DATA=' + json.dumps(combined, ensure_ascii=False, separators=(',', ':')) + ';</script>'
    html = tpl.replace('<script src="data:text/javascript;base64,__DATA_B64__"></script>', embed)
    hist_embed = '<script>const HISTORY=' + json.dumps(history, ensure_ascii=False, separators=(',', ':')) + ';</script>'
    html = html.replace('<script src="data:text/javascript;base64,__HISTORY_B64__"></script>', hist_embed)
    json.dump(combined, open(os.path.join(BASE, 'listings_today.json'), 'w'), ensure_ascii=False)
    html = re.sub(r'\d{4}-\d{2}-\d{2}-ны түүвэр', date.today().isoformat() + '-ны түүвэр', html)
    out_path = os.path.join(BASE, 'ub-realestate-map.html')
    open(out_path, 'w').write(html)
    open(os.path.join(BASE, 'index.html'), 'w').write(html)  # GitHub Pages-д зориулсан хуулбар

    ns = sum(1 for l in combined if l['m'] == 's')
    nr = len(combined) - ns
    print(f'OK: {out_path}')
    print(f'түүх: {len(history)} өдрийн дата хуримтлагдсан')
    print(f'худалдах {ns} зар (raw {len(raw_sale)}), түрээс {nr} зар (raw {len(raw_rent)})')
    for mode, unit in (('s', 'сая ₮/м²'), ('r', 'мян ₮/м²·сар')):
        v = [l['ppm'] for l in combined if l['m'] == mode]
        if v:
            print(f"  медиан {'худалдах' if mode=='s' else 'түрээс'}: {statistics.median(v):.1f} {unit}")


if __name__ == '__main__':
    main()
