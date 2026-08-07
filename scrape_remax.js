// RE/MAX Mongolia-ийн зарыг API-гаар татах — Browser pane-д www.remax.mn нээгдсэн байх ёстой
// (жишээ нь preview_start {url: "https://www.remax.mn"}). Same-origin fetch ашигладаг.
// Үр дүнг parse_result.py-ийн ижил аргаар raw_remax.json болгоно (бүтэц: {sale: [...], rent: [...]}).
// Мөр: [City, LocalZone, price, currency, area, rooms, [lng,lat], MLSID, yearBuilt, granularityUID]
(async () => {
  const cutoff = Math.floor(Date.now() / 1000) - 90 * 86400; // сүүлийн 90 хоног
  const out = { sale: [], rent: [] };
  for (const [key, tuid] of [['sale', 261], ['rent', 260]]) {
    let skip = 0;
    while (skip < 5000) {
      const res = await fetch('https://www.remax.mn/search/listing-search/docs/search', {
        method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          count: true, top: 1000, skip,
          filter: `content/ListingCountryCode eq 'MN' and content/ListingClass eq 2 and content/TransactionTypeUID eq ${tuid} and content/IsViewable eq true and content/MacroPropertyTypeUID eq 19377 and content/OrigListingDate ge ${cutoff}`,
          select: "content/ListingPrice,content/ListingCurrency,content/TotalArea,content/TotalNumOfRooms,content/City,content/LocalZone,content/Location,content/MLSID,content/YearBuilt,content/RentalPriceGranularityUID"
        })
      });
      const j = await res.json();
      if (!j.value || !j.value.length) break;
      j.value.forEach(v => {
        const c = v.content;
        out[key].push([c.City, c.LocalZone, c.ListingPrice, c.ListingCurrency, c.TotalArea, c.TotalNumOfRooms,
          c.Location ? c.Location.coordinates : null, c.MLSID, c.YearBuilt, c.RentalPriceGranularityUID]);
      });
      skip += 1000;
      if (j.value.length < 1000) break;
      await new Promise(r => setTimeout(r, 300));
    }
  }
  return JSON.stringify(out);
})()
