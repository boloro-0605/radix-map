#!/usr/bin/env python3
"""Захиалга ↔ зарын автомат тохируулга (Radix Properties).

Оролт:  requests.json — худалдан авагч/түрээслэгчийн захиалгууд
        listings_today.json — build.py-ийн өнөөдрийн парс хийсэн зарууд
        seen.json — захиалга бүрд аль хэдийн мэдэгдсэн зарын URL-ууд
Гаралт: шинэ тохирлуудыг stdout-д хэвлэж, matches_report.md-д нэмнэ.

Захиалгын бүтэц (requests.json):
  id          — дугаар
  active      — true үед л шалгана
  client      — захиалагчийн нэр
  phone       — холбоо барих (тайланд гарна)
  mode        — "s" (худалдаж авах) | "r" (түрээслэх)
  districts   — ["Баянзүрх", ...] (хоосон бол бүх дүүрэг)
  neighborhoods — ["Сансар", ...] нэрэнд агуулагдах хэсэгчилсэн тохирол (заавал биш)
  rooms       — [2, 3] (хоосон бол хамаагүй; 5 = 5+)
  min_area / max_area — м²
  min_price / max_price — сая ₮ (түрээс бол сарын үнэ, сая ₮)
  note        — тэмдэглэл
"""
import json, os
from datetime import date

BASE = os.path.dirname(os.path.abspath(__file__))


def load(name, default):
    p = os.path.join(BASE, name)
    return json.load(open(p)) if os.path.exists(p) else default


def matches(req, l):
    if l['m'] != req.get('mode', 's'):
        return False
    if req.get('districts') and l['d'] not in req['districts']:
        return False
    if req.get('neighborhoods') and not any(nb.lower() in (l['nb'] or '').lower() for nb in req['neighborhoods']):
        return False
    if req.get('rooms'):
        r = l.get('r')
        ok = any((want == 5 and r and r >= 5) or r == want for want in req['rooms'])
        if not ok:
            return False
    a, p = l.get('a'), l.get('p')
    if req.get('min_area') and (not a or a < req['min_area']):
        return False
    if req.get('max_area') and (not a or a > req['max_area']):
        return False
    if req.get('min_price') and (not p or p < req['min_price']):
        return False
    if req.get('max_price') and (not p or p > req['max_price']):
        return False
    return True


def main():
    listings = load('listings_today.json', [])
    reqs = load('requests.json', [])
    seen = load('seen.json', {})
    today = date.today().isoformat()
    lines = []
    total = 0

    for req in reqs:
        if not req.get('active'):
            continue
        rid = str(req['id'])
        seen_urls = set(seen.get(rid, []))
        new = [l for l in listings if matches(req, l) and l['u'] not in seen_urls]
        if not new:
            continue
        total += len(new)
        mode_mn = 'худалдаж авах' if req.get('mode', 's') == 's' else 'түрээслэх'
        lines.append(f"\n### Захиалга #{rid} — {req.get('client', '?')} ({mode_mn}) {req.get('phone', '')}")
        if req.get('note'):
            lines.append(f"_{req['note']}_")
        for l in sorted(new, key=lambda x: x['p'])[:15]:
            unit = ' сая ₮/сар' if l['m'] == 'r' else ' сая ₮'
            lines.append(f"- **{l['p']}{unit}** · {l['a']} м² · {l['r'] or '?'} өрөө · {l['d']}, {l['nb']}\n  {l['t']}\n  {l['u']}")
        if len(new) > 15:
            lines.append(f"_...болон өөр {len(new) - 15} зар (эхний 15-ыг үнээр эрэмбэлж харуулав)_")
        seen[rid] = sorted(seen_urls | {l['u'] for l in new})

    json.dump(seen, open(os.path.join(BASE, 'seen.json'), 'w'), ensure_ascii=False)

    if total:
        body = f"\n## {today} — {total} шинэ тохирол\n" + "\n".join(lines) + "\n"
        with open(os.path.join(BASE, 'matches_report.md'), 'a') as f:
            f.write(body)
        print(f"MATCHES: {total} шинэ тохирол олдлоо!")
        print(body)
    else:
        n_active = sum(1 for r in reqs if r.get('active'))
        print(f"MATCHES: шинэ тохирол алга (идэвхтэй захиалга: {n_active}).")


if __name__ == '__main__':
    main()
