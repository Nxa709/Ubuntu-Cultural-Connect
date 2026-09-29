/* Official website links for seeded hotspots, keyed by the experience title
   exactly as stored in the database. Titles without an official website are
   intentionally omitted (the website section simply won't render for them). */
export const hotspotWebsites = {
  'Ocean Basket Musgrave': 'https://www.oceanbasket.co.za',
  'The Spice Restaurant & Bar': 'https://spicerestaurant.co.za',
  "Tiger's Milk Ballito": 'https://www.tigersmilk.co.za',
  'uShaka Maritime Museum': 'https://www.ushakamarine.com',
  'KwaMuhle Museum': 'https://visitdurban.travel/space/kwamuhle-museum',
  'Durban Natural Science Museum': 'https://visitdurban.travel/space/natural-science-museum-research-centre',
  'Natal Museum': 'https://www.nmsa.org.za',
  'Kenneth Stainbank Nature Reserve': 'https://visitdurban.travel/space/kenneth-stainbank-nature-reserve',
  'Burman Bush Nature Reserve': 'https://visitdurban.travel/space/burman-bush-nature-reserve',
  'Hluhluwe-iMfolozi Park — Hluhluwe Section': 'https://www.kznwildlife.com',
  'Hluhluwe-iMfolozi Park — Memorial Gate': 'https://www.kznwildlife.com',
  'uMkhuze Game Reserve': 'https://isimangaliso.com/places/umkhuze/',
  'iSimangaliso Wetland Park — Southern Section': 'https://isimangaliso.com',
  "Gogo's Tales at Phansi Museum": 'https://visitdurban.travel/space/phansi-museum',
  'African Storytelling Nights at The Bat Centre': 'https://visitdurban.travel/space/the-bat-centre',
  'Victoria Street Market': 'https://www.victoriastreetmarket.co.za',
  'Muthi Traditional Market': 'https://visitdurban.travel/space/durban-muthi-market',
  'Muthi Market & Healing Walk': 'https://visitdurban.travel/space/durban-muthi-market',
  'Emmanuel Cathedral': 'https://emmanuelcathedral.org.za',
  'Juma Masjid Mosque': 'https://visitdurban.travel/space/juma-masjid-mosque',
  'The Playhouse Theatre': 'https://www.theplayhousecompany.com',
  'The Bat Centre': 'https://visitdurban.travel/space/the-bat-centre',
  'Elizabeth Sneddon Theatre': 'https://www.sneddontheatre.co.za',
  'The Heritage Theatre': 'https://heritagetheatre.co.za',
  'Inanda Heritage Route Tour': 'https://visitdurban.travel/tour/inanda-kwamashu-tour',
  'PheZulu Cultural Village & Safari': 'https://phezulusafaripark.co.za',
  'Valley of a Thousand Hills Tour': 'https://visitdurban.travel/tour/valley-of-1000-hills-tour',
}

export function getHotspotWebsite(title) {
  if (!title) return null
  return hotspotWebsites[title] || null
}

export default hotspotWebsites
