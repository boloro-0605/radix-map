#!/usr/bin/env python3
"""javascript_tool-ийн tool-result файлаас raw JSON-ийг салгаж авна.

Хэрэглээ: python3 parse_result.py <tool-result-file> [<tool-result-file> ...] <raw_sale.json|raw_rent.json>
Хамгийн сүүлийн аргумент нь гаралтын файл; түүний өмнөх бүгд нь эх файлууд.
Хэд хэдэн эх файл дамжуулбал (scrape.js-ийг PAGES=[1,7] + [8,14] гэж хуваасан үед)
бүгдийг парс хийж, href-ээр давхардал арилгаад нэг файлд нийлүүлнэ.
Tool result нь [{type,text}] бүтэцтэй; text дотор JSON string + "(captured..." тэмдэглэл байдаг.
"""
import json, sys, os

if len(sys.argv) < 3:
    sys.exit(__doc__)

srcs, dst = sys.argv[1:-1], sys.argv[-1]


def load(src):
    outer = json.load(open(src))
    text = outer[0]['text']
    idx = text.find('(captured')
    if idx > 0:
        text = text[:idx]
    text = text.strip()
    return json.loads(json.loads(text) if text.startswith('"') else text)


rows, seen = [], set()
for src in srcs:
    data = load(src)
    assert isinstance(data, list), f'{src}: list биш ({type(data).__name__})'
    if len(srcs) > 1:
        print(f'  {os.path.basename(src)}: {len(data)} мөр')
    for row in data:
        key = row[4] if isinstance(row, list) and len(row) > 4 else json.dumps(row, ensure_ascii=False)
        if key in seen:
            continue
        seen.add(key)
        rows.append(row)

assert len(rows) > 100, f'хэт цөөн мөр: {len(rows)}'
json.dump(rows, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), dst), 'w'), ensure_ascii=False)
print(f'{dst}: {len(rows)} мөр' + (' (давхардал арилсны дараа)' if len(srcs) > 1 else ''))
