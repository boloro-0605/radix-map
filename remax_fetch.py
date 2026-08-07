#!/usr/bin/env python3
"""RE/MAX Mongolia-ийн зарыг API-гаас шууд татна (браузер шаардахгүй).

scrape_remax.js-ийн Python хувилбар — GitHub Actions зэрэг серверлэсс орчинд ажиллана.
Гаралт: raw_remax.json {sale: [...], rent: [...]}
"""
import json, os, time, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
API = 'https://www.remax.mn/search/listing-search/docs/search'
CUTOFF = int(time.time()) - 90 * 86400  # сүүлийн 90 хоног


def fetch(tuid):
    rows, skip = [], 0
    while skip < 5000:
        body = json.dumps({
            'count': True, 'top': 1000, 'skip': skip,
            'filter': (f"content/ListingCountryCode eq 'MN' and content/ListingClass eq 2 "
                       f"and content/TransactionTypeUID eq {tuid} and content/IsViewable eq true "
                       f"and content/MacroPropertyTypeUID eq 19377 and content/OrigListingDate ge {CUTOFF}"),
            'select': ("content/ListingPrice,content/ListingCurrency,content/TotalArea,"
                       "content/TotalNumOfRooms,content/City,content/LocalZone,content/Location,"
                       "content/MLSID,content/YearBuilt,content/RentalPriceGranularityUID"),
        }).encode()
        req = urllib.request.Request(API, data=body, headers={
            'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            j = json.load(r)
        vals = j.get('value', [])
        if not vals:
            break
        for v in vals:
            c = v['content']
            rows.append([c['City'], c['LocalZone'], c['ListingPrice'], c['ListingCurrency'],
                         c['TotalArea'], c['TotalNumOfRooms'],
                         c['Location']['coordinates'] if c.get('Location') else None,
                         c['MLSID'], c['YearBuilt'], c['RentalPriceGranularityUID']])
        skip += 1000
        if len(vals) < 1000:
            break
        time.sleep(0.4)
    return rows


def main():
    out = {'sale': fetch(261), 'rent': fetch(260)}
    if len(out['sale']) < 500:
        raise SystemExit(f"хэт цөөн sale зар ({len(out['sale'])}) — API өөрчлөгдсөн байж магадгүй, хуучин файлыг хадгална")
    json.dump(out, open(os.path.join(BASE, 'raw_remax.json'), 'w'), ensure_ascii=False)
    print(f"OK: sale {len(out['sale'])}, rent {len(out['rent'])}")


if __name__ == '__main__':
    main()
