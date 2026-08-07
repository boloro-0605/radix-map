# УБ орон сууцны үнийн зураглал — өдөр тутмын шинэчлэлт

Artifact: https://claude.ai/code/artifact/1fceb6ad-8b4e-4fa5-96fc-8f6e231c0a3e
Эх сурвалж: unegui.mn (худалдах + түрээс, УБ-ын 6 дүүрэг, тус бүр эхний 2 хуудас ≈ 120 зар)

## Шинэчлэх дараалал (Claude session-д зориулсан заавар)

1. **Browser tab нээх**: unegui.mn-ийг Browser pane-д нээнэ (жишээ нь
   `preview_start {url: "https://www.unegui.mn/l-hdlh/"}`). curl ажиллахгүй (403,
   Cloudflare) тул заавал browser доторх same-origin fetch ашиглана.

2. **Худалдах зар татах**: `scrape.js`-ийн агуулгыг javascript_tool-д ажиллуулна
   (KIND='sale' хэвээр). Үр дүн том тул tool-result файлд хадгалагдана — тэр файлын
   замыг ашиглан:
   `python3 parse_result.py <tool-result-file> raw_sale.json`

   ⚠️ **javascript_tool 30 секундэд timeout болдог**, scrape.js-ийг бүтнээр нь (12 хуудас)
   нэг дуудалтад ажиллуулбал амжихгүй. Тиймээс: эхний дуудалтад `window.__CATS` толь ба
   `window.__grab(kind, [дүүргүүд])` функцийг тодорхойлж, дараа нь **2 дүүрэг тутамд нэг
   дуудалт** (3 дуудалт/төрөл) хийж `window.__S[kind]`-д хуримтлуулна. Эцэст нь
   `JSON.stringify(window.__S.sale)` гэж буцаавал tool-result файлд хадгалагдана.
   Фон дээр ажиллуулаад poll хийх арга бүтэхгүй — pane хаагдвал window state алга болно.

3. **Түрээсийн зар татах**: scrape.js-ийн эхний мөрийг `const KIND = 'rent';` болгоод
   дахин ажиллуулна, дараа нь:
   `python3 parse_result.py <tool-result-file> raw_rent.json`

3б. **RE/MAX зар татах**: Browser tab-ыг https://www.remax.mn руу шилжүүлээд
   `scrape_remax.js`-ийн агуулгыг javascript_tool-д ажиллуулна (нэг дор sale+rent татна), дараа нь:
   `python3 parse_result.py <tool-result-file> raw_remax.json`
   RE/MAX амжилтгүй бол (API өөрчлөгдсөн г.м.) хуучин raw_remax.json-г дарж бичилгүй үлдээж
   болно — build.py байгаа файлаараа үргэлжилнэ.

4. **HTML угсрах**: `python3 build.py` → `ub-realestate-map.html` үүсгэнэ
   (дата embed + огноо автоматаар шинэчлэгдэнэ). Мөн тухайн өдрийн медиан үзүүлэлтүүдийг
   `history.json`-д хуримтлуулж, трэнд график руу embed хийнэ — history.json-г хэзээ ч
   устгаж болохгүй, энэ бол хуримтлагдсан түүх. Гаралтын тоонууд үнэмшилтэй эсэхийг
   шалгана: төрөл тус бүр 400+ зар, медианууд өмнөхтэй ойролцоо байх ёстой.

5. **Artifact шинэчлэх**: Artifact tool-оор нийтэлнэ —
   `file_path: <энэ хавтас>/ub-realestate-map.html`,
   `url: "https://claude.ai/code/artifact/1fceb6ad-8b4e-4fa5-96fc-8f6e231c0a3e"`,
   `favicon: "🏙️"` (өөрчлөхгүй). URL-ийг заавал дамжуулна — эс бөгөөс шинэ хаяг үүснэ!

5б. **Захиалгын тохируулга**: `python3 match.py` — `requests.json`-ийн идэвхтэй (active: true)
   захиалгуудад тохирох шинэ зар шалгана. Нэг зарыг нэг захиалгад нэг л удаа мэдэгдэнэ
   (seen.json). Тохирлууд matches_report.md-д огноогоор хуримтлагдана. Захиалгын бүтэц,
   талбаруудын тайлбар match.py-ийн эхэнд бий.

**Шинэ захиалга нэмэх**: хэрэглэгч Claude-д "шинэ захиалга: [шаардлага]" гэж хэлэхэд
requests.json-д шинэ бичлэг (id дараалсан, active: true) нэмнэ. Захиалга хаагдвал
active: false болгоно — устгахгүй.

## Анхаарах

- Сайтын бүтэц өөрчлөгдвөл (`.advert.js-item-listing` сонгогч олдохгүй бол) scrape.js-ийг
  засах хэрэгтэй; 0 мөр буцаавал сайтын HTML-ийг шалгах.
- Аль нэг татаж авалт бүхэлдээ амжилтгүй бол хуучин raw_*.json-оо дарж бичихгүй байх —
  parse_result.py 100-аас цөөн мөрөнд алдаа өгдөг.
- Координатын толь (build.py доторх COORDS) шинэ хороолол нэмэгдвэл баяжуулж болно;
  олдоогүй нэрс дүүргийн төв орчимд деterministic jitter-ээр байрлана.
