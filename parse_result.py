#!/usr/bin/env python3
"""javascript_tool-ийн tool-result файлаас raw JSON-ийг салгаж авна.

Хэрэглээ: python3 parse_result.py <tool-result-file> <raw_sale.json|raw_rent.json>
Tool result нь [{type,text}] бүтэцтэй; text дотор JSON string + "(captured..." тэмдэглэл байдаг.
"""
import json, sys, os

src, dst = sys.argv[1], sys.argv[2]
outer = json.load(open(src))
text = outer[0]['text']
idx = text.find('(captured')
if idx > 0:
    text = text[:idx]
text = text.strip()
data = json.loads(json.loads(text) if text.startswith('"') else text)
assert isinstance(data, list) and len(data) > 100, f'хэт цөөн мөр: {len(data)}'
json.dump(data, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), dst), 'w'), ensure_ascii=False)
print(f'{dst}: {len(data)} мөр')
