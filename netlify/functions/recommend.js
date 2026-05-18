exports.handler = async (event) => {
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
      },
      body: '',
    };
  }

  const { goals, who, extra } = JSON.parse(event.body);

  const HEALTHNEEDS_CATALOG = `
HEALTHNEEDS.COM.MT – PRODUCT CATALOG OVERVIEW

CATEGORIES:
- Vitamins, Minerals & Supplements (vitamins, minerals, supplements, collagen, omega/fish oils, probiotics, magnesium, iron, ashwagandha)
- Skin, Hair & Eye Care (skincare: cleansers, moisturisers, serums, creams, suncare, toner; hair & scalp; eye care; children's skincare)
- Mother & Baby (baby & child health, baby feed & care, pregnancy & maternity)
- Health & Lifestyle (bloating, coughs/colds/flu, ear care, first aid, hangover aid)
- Medical Devices & Home Testing (blood pressure monitors, diabetes management, pregnancy & ovulation tests, covid tests)
- Toiletries (dental care, feminine care, personal care, fragrances)

BRANDS AVAILABLE: Avene, Bioderma, CeraVe, La Roche-Posay, SVR, Uriage, Vichy, Centrum, Health Aid, Nature's Aid, Quest, Seven Seas, Vega, Vitabiotics, ActiKid, Babylino, Chewy Vites, Cow & Gate, Happynose, Nan, Novalac, Aboca, Erba Vita, Gehwol, Medicare, Oppo, Puressentiel, Abena, Always, Colgate, Dove, Durex, Eva Intima, Nivea, Aerochamber, Beurer, Bionime, Clearblue, Omron, Medik8, ISDIN, Lee Stafford, Nupo, Optibac, BioGaia, Igennus, Vital Proteins

BESTSELLERS:
- Magnetrex Magnesium Bisglycinate X30 Tablets (€18.00) – sleep, muscle, stress
- Pantogar Hair & Nails X90 Capsules (€30.40) – hair, nails
- CeraVe Moisturising Cream (€11.30–€20.53) – dry skin
- Optibac Everyday Extra Strength X90 (€70.25) – gut/probiotics
- Vitabiotics Osteocare Original 90 Tablets (€11.87) – bone/joint
- Chewy Vites Kids Multi Vitamin + Probiotic X60 (€9.93) – kids
- Via Lattea X20 Tablets (€8.50) – digestion
- Quest Forte D 4000 X120 Tablets (€29.09) – vitamin D, immune, energy
- BioGaia Baby Drops 5ml (€9.41) – baby gut
- ORS Hydration Soluble Tablets (€5.93–€9.26) – hydration

RECENT ADDITIONS:
- Vital Proteins Collagen Peptides 567g (€42.66) – skin, joints, hair
- Igennus Triple Magnesium Complex X60 (€19.57) – sleep, muscle, nerves
- Melatonin + Forte 5 + Valerian X60 Tablets (€9.41) – sleep
- BetterYou Vitamin D3 + K2 12ml (€13.21) – immune, bone, energy
- Active Iron For Women X60 Capsules (€20.89) – iron, women
- Nupo One Meal + Prime range – weight management
- Marigraine X40 Tablets (€37.05) – migraine
- German Zinc Effervescent X20 Tablets (€4.28) – immune, skin

HEALTH GOALS ON SITE:
Digestive Health, Children's Immune Support, Sleep Support, Energy Booster, Immune System Support, Joint Care, Cardiovascular Health, Baby Skincare

SKIN GOALS ON SITE:
Acne Care, Aging Skin Care, Cleansing, Dry Skin Care, Make-Up Removal

DELIVERY: Free over €25. Same-day delivery (orders before 1PM, over €50). Based in Malta.
WEBSITE: healthneeds.com.mt
`;

  const userPrompt = `
The user is shopping at healthneeds.com.mt, a Maltese health & wellness webshop.

USER PROFILE:
- Who: ${who}
- Goals: ${goals.join(', ')}
- Extra context: ${extra || 'none'}

CATALOG CONTEXT:
${HEALTHNEEDS_CATALOG}

Your task: Recommend exactly 3 products from the Health Needs catalog that best match this user's needs. Be specific — use real product names from the catalog. For each product explain WHY it fits their specific situation in 2–3 sentences. Be warm, clear, and human. Don't be generic.

Respond ONLY in this exact JSON format (no markdown, no backticks, no preamble):
{
  "recommendations": [
    { "rank": "Best match", "name": "Product Name", "category": "Category name", "why": "Explanation of why this fits..." },
    { "rank": "Also great", "name": "Product Name", "category": "Category name", "why": "Explanation..." },
    { "rank": "Worth adding", "name": "Product Name", "category": "Category name", "why": "Explanation..." }
  ]
}
`;

  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': process.env.ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1000,
      messages: [{ role: 'user', content: userPrompt }],
    }),
  });

  const data = await response.json();
  const text = data.content?.map(i => i.text || '').join('') || '';
  const clean = text.replace(/```json|```/g, '').trim();

  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
    },
    body: clean,
  };
};
