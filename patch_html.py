#!/usr/bin/env python3
"""
Patch index.html with:
1. New PRODUCTS array from products_new.js
2. Updated chips HTML for new goals
3. Updated chipLabels
4. New parseGoalsFromText()
5. Updated getWhy() with new goal cases
6. Updated getRecommendations() with primaryBonus scoring
7. Updated deduplication
8. Updated parseConditions()
"""

with open('/home/user/healthneeds-recommender/index.html', 'r') as f:
    html = f.read()

with open('/home/user/healthneeds-recommender/products_new.js', 'r') as f:
    new_products = f.read().strip()

# ─────────────────────────────────────────────────────────────
# 1. REPLACE PRODUCTS ARRAY
# ─────────────────────────────────────────────────────────────
# Find start and end of PRODUCTS block
prod_start = html.index('const PRODUCTS = [')
prod_end = html.index('];', prod_start) + 2  # include the '];'
html = html[:prod_start] + new_products + html[prod_end:]

# ─────────────────────────────────────────────────────────────
# 2. REPLACE CHIPS HTML — add new goal chips
# ─────────────────────────────────────────────────────────────
old_chips = '''    <div class="chips-grid">
      <div class="chip" data-val="sleep">😴 Sleep</div>
      <div class="chip" data-val="energy">⚡ Energy</div>
      <div class="chip" data-val="stress">🧘 Stress</div>
      <div class="chip" data-val="immune">🛡️ Immunity</div>
      <div class="chip" data-val="gut">🫁 Gut</div>
      <div class="chip" data-val="skin">✨ Skin</div>
      <div class="chip" data-val="hair">💅 Hair & nails</div>
      <div class="chip" data-val="weight">⚖️ Weight</div>
      <div class="chip" data-val="joint">💪 Joints</div>
      <div class="chip" data-val="heart">❤️ Heart</div>
      <div class="chip" data-val="kids">🧒 Kids</div>
      <div class="chip" data-val="pregnancy">🤰 Pregnancy</div>
    </div>'''

new_chips = '''    <div class="chips-grid">
      <div class="chip" data-val="sleep">😴 Sleep</div>
      <div class="chip" data-val="energy">⚡ Energy</div>
      <div class="chip" data-val="stress">🧘 Stress</div>
      <div class="chip" data-val="immune">🛡️ Immunity</div>
      <div class="chip" data-val="gut">🫁 Gut</div>
      <div class="chip" data-val="skin">✨ Skin</div>
      <div class="chip" data-val="hair">💅 Hair & nails</div>
      <div class="chip" data-val="weight">⚖️ Weight</div>
      <div class="chip" data-val="joint">💪 Joints</div>
      <div class="chip" data-val="heart">❤️ Heart</div>
      <div class="chip" data-val="focus">🧠 Brain/Focus</div>
      <div class="chip" data-val="menopause">🌡️ Menopause</div>
      <div class="chip" data-val="uti">💧 Urinary</div>
      <div class="chip" data-val="cold">🤧 Cold & Flu</div>
      <div class="chip" data-val="mens">👨 Men\'s Health</div>
      <div class="chip" data-val="womens">👩 Women\'s Health</div>
      <div class="chip" data-val="blood_sugar">🩸 Blood Sugar</div>
      <div class="chip" data-val="liver">🫀 Liver</div>
      <div class="chip" data-val="kids">🧒 Kids</div>
      <div class="chip" data-val="pregnancy">🤰 Pregnancy</div>
    </div>'''

html = html.replace(old_chips, new_chips)

# ─────────────────────────────────────────────────────────────
# 3. REPLACE chipLabels in JS
# ─────────────────────────────────────────────────────────────
old_chip_labels = """const chipLabels = {
  sleep: 'sleep issues', energy: 'low energy', stress: 'stress',
  immune: 'immune support', gut: 'gut health', skin: 'skin',
  hair: 'hair and nails', weight: 'weight management',
  joint: 'joint and muscle pain', heart: 'heart health',
  kids: 'kids health', pregnancy: 'pregnancy'
};"""

new_chip_labels = """const chipLabels = {
  sleep: 'sleep issues', energy: 'low energy', stress: 'stress',
  immune: 'immune support', gut: 'gut health', skin: 'skin',
  hair: 'hair and nails', weight: 'weight management',
  joint: 'joint and muscle pain', heart: 'heart health',
  focus: 'brain fog and focus', menopause: 'menopause',
  uti: 'urinary tract issues', cold: 'cold and flu',
  mens: "men's health", womens: "women's health",
  blood_sugar: 'blood sugar', liver: 'liver health',
  kids: 'kids health', pregnancy: 'pregnancy'
};"""

html = html.replace(old_chip_labels, new_chip_labels)

# ─────────────────────────────────────────────────────────────
# 4. REPLACE parseGoalsFromText()
# ─────────────────────────────────────────────────────────────
old_parse_goals = """function parseGoalsFromText(text) {
  const t = text.toLowerCase();
  const goals = new Set();

  // --- TIER 1: PHRASES (specific, highest priority) ---
  // Sunburn — must come before stress so "burned" goes to skin, not stress
  if (/\\bburn(ed|t)?\\b(?! out| through| down| up| off)|sunburn|after.?sun|sun damage|too much sun|skin is red|red from sun|spf|sunscreen|sun protection|sun lotion|sun cream/.test(t)) goals.add('sunburn');
  // Burned OUT specifically → stress
  if (/burn(ed|t)? out|burning out|burnout/.test(t)) goals.add('stress');

  // Sleep
  if (/can.t sleep|trouble sleeping|hard to sleep|wake up at night|poor sleep|not sleeping|sleep issues|sleep problems|fall asleep|staying asleep/.test(t)) goals.add('sleep');
  // Energy (phrases)
  if (/no energy|low energy|always tired|constantly tired|feel drained|feel exhausted|run down|worn out|always fatigued|chronic fatigue/.test(t)) goals.add('energy');
  // Stress (phrases)
  if (/stressed out|feeling stressed|under stress|too much stress|panic attack|feel anxious|constant worry|overwhelmed|can.t cope|mental fatigue|mental exhaustion/.test(t)) goals.add('stress');
  // Immune (phrases)
  if (/keep getting sick|getting ill|frequent colds|cold and flu|boost.*immune|weak immune|always catching|sick all the time/.test(t)) goals.add('immune');
  // Gut (phrases)
  if (/feel bloated|stomach pain|stomach ache|tummy ache|bad digestion|digestive issues|irregular bowel|loose stools|gut health|leaky gut/.test(t)) goals.add('gut');
  // Skin (phrases)
  if (/dry skin|oily skin|skin breakout|skin problems|dull skin|anti.aging|aging skin|skin glow|glowing skin|clear skin|skin hydration/.test(t)) goals.add('skin');
  // Hair (phrases)
  if (/hair loss|hair falling|losing hair|thinning hair|hair breakage|brittle hair|weak hair|hair growth|hair and nails/.test(t)) goals.add('hair');
  // Joint (phrases)
  if (/joint pain|joints hurt|achy joints|stiff joints|knee pain|back pain|muscle pain|sore muscles|muscle aches/.test(t)) goals.add('joint');
  // Heart (phrases)
  if (/heart health|high cholesterol|blood pressure|lower cholesterol|cardiovascular health/.test(t)) goals.add('heart');
  // Weight (phrases)
  if (/lose weight|weight loss|trying to slim|lose fat|weight management|shed pounds|body fat/.test(t)) goals.add('weight');
  // Kids (phrases)
  if (/for my child|for my kid|for my baby|for my toddler|children.s vitamin|kids vitamin|my son|my daughter|my infant|newborn/.test(t)) goals.add('kids');
  // Pregnancy (phrases)
  if (/trying to conceive|trying for a baby|prenatal vitamin|during pregnancy|early pregnancy/.test(t)) goals.add('pregnancy');
  // Eye (phrases)
  if (/eye health|dry eyes|blurry vision|eye strain|screen time.*eye|macular health/.test(t)) goals.add('eye');

  // --- TIER 2: SINGLE KEYWORDS (fallback — only if goal not yet detected) ---
  if (!goals.has('sleep') && !goals.has('energy') && /\\bsleep\\b|insomnia/.test(t)) goals.add('sleep');
  if (!goals.has('energy') && /\\benergy\\b|\\btired\\b|\\bfatigue\\b|exhaust|sluggish|drained/.test(t)) goals.add('energy');
  if (!goals.has('stress') && /\\bstress\\b|anxiet|nervous|worried/.test(t)) goals.add('stress');
  if (!goals.has('immune') && /\\bimmune\\b|\\bsick\\b|\\bcold\\b|\\bflu\\b|infection/.test(t)) goals.add('immune');
  if (!goals.has('gut') && /\\bgut\\b|digest|bloat|\\bstomach\\b|bowel|\\bibs\\b|constipat|diarr/.test(t)) goals.add('gut');
  if (!goals.has('sunburn') && !goals.has('skin') && /\\bskin\\b|acne|moistur|complexion|rash/.test(t)) goals.add('skin');
  if (!goals.has('hair') && /\\bhair\\b|\\bnail\\b|thinning|breakage|\\bbald/.test(t)) goals.add('hair');
  if (!goals.has('weight') && /\\bweight\\b|\\bslim\\b|\\bdiet\\b|calori/.test(t)) goals.add('weight');
  if (!goals.has('joint') && /\\bjoint\\b|muscle|\\bpain\\b|cramp|stiff|arthritis/.test(t)) goals.add('joint');
  if (!goals.has('heart') && /\\bheart\\b|cholesterol/.test(t)) goals.add('heart');
  if (!goals.has('kids') && /\\bkid\\b|\\bchild\\b|\\bbaby\\b|toddler|infant/.test(t)) goals.add('kids');
  if (!goals.has('pregnancy') && /pregnan|expecting|maternity/.test(t)) goals.add('pregnancy');
  if (!goals.has('eye') && /\\beye\\b|vision|lutein/.test(t)) goals.add('eye');

  // sunburn implies skin too
  if (goals.has('sunburn')) goals.add('skin');

  return [...goals];
}"""

new_parse_goals = """function parseGoalsFromText(text) {
  const t = text.toLowerCase();
  const goals = new Set();

  // --- TIER 1: PHRASES (specific, highest priority) ---

  // Sunburn — must come before stress so "burned" goes to skin, not stress
  if (/\\bburn(ed|t)?\\b(?! out| through| down| up| off)|sunburn|after.?sun|sun damage|too much sun|skin is red|red from sun|spf|sunscreen|sun protection|sun lotion|sun cream/.test(t)) goals.add('sunburn');
  if (/burn(ed|t)? out|burning out|burnout/.test(t)) goals.add('stress');

  // Focus / Brain
  if (/brain fog|can.t concentrate|trouble concentrating|lack of focus|poor memory|memory problems|memory loss|cognitive decline|can.t think clearly/.test(t)) goals.add('focus');
  // Menopause
  if (/menopause|hot flush(es)?|hot flash(es)?|perimenopause|peri.menopause|night sweat/.test(t)) goals.add('menopause');
  // UTI / Urinary
  if (/uti|urinary tract|bladder infection|cystitis|burning when urinating|burning when i pee|frequent urination|keep needing to pee/.test(t)) goals.add('uti');
  // Cold / Flu
  if (/i have a cold|fighting a cold|sore throat|runny nose|sneezing|blocked nose|stuffy nose|cold and flu|got the flu|feel a cold coming/.test(t)) goals.add('cold');
  // Men's health
  if (/prostate|men.s health|low testosterone|testosterone support|enlarged prostate/.test(t)) goals.add('mens');
  // Women's health
  if (/pms|period pain|painful periods|irregular periods|hormonal balance|premenstrual|women.s health/.test(t)) goals.add('womens');
  // Blood sugar
  if (/blood sugar|sugar cravings|type 2 diabetes|manage diabetes|glucose levels|insulin resistance|high blood sugar/.test(t)) goals.add('blood_sugar');
  // Liver
  if (/liver health|liver support|liver detox|detox my liver|liver cleanse/.test(t)) goals.add('liver');

  // Sleep
  if (/can.t sleep|trouble sleeping|hard to sleep|wake up at night|poor sleep|not sleeping|sleep issues|sleep problems|fall asleep|staying asleep/.test(t)) goals.add('sleep');
  // Energy (phrases)
  if (/no energy|low energy|always tired|constantly tired|feel drained|feel exhausted|run down|worn out|always fatigued|chronic fatigue/.test(t)) goals.add('energy');
  // Stress (phrases)
  if (/stressed out|feeling stressed|under stress|too much stress|panic attack|feel anxious|constant worry|overwhelmed|can.t cope|mental fatigue|mental exhaustion/.test(t)) goals.add('stress');
  // Immune (phrases)
  if (/keep getting sick|getting ill|frequent colds|cold and flu|boost.*immune|weak immune|always catching|sick all the time/.test(t)) goals.add('immune');
  // Gut (phrases)
  if (/feel bloated|stomach pain|stomach ache|tummy ache|bad digestion|digestive issues|irregular bowel|loose stools|gut health|leaky gut/.test(t)) goals.add('gut');
  // Skin (phrases)
  if (/dry skin|oily skin|skin breakout|skin problems|dull skin|anti.aging|aging skin|skin glow|glowing skin|clear skin|skin hydration/.test(t)) goals.add('skin');
  // Hair (phrases)
  if (/hair loss|hair falling|losing hair|thinning hair|hair breakage|brittle hair|weak hair|hair growth|hair and nails/.test(t)) goals.add('hair');
  // Joint (phrases)
  if (/joint pain|joints hurt|achy joints|stiff joints|knee pain|back pain|muscle pain|sore muscles|muscle aches/.test(t)) goals.add('joint');
  // Heart (phrases)
  if (/heart health|high cholesterol|blood pressure|lower cholesterol|cardiovascular health/.test(t)) goals.add('heart');
  // Weight (phrases)
  if (/lose weight|weight loss|trying to slim|lose fat|weight management|shed pounds|body fat/.test(t)) goals.add('weight');
  // Kids (phrases)
  if (/for my child|for my kid|for my baby|for my toddler|children.s vitamin|kids vitamin|my son|my daughter|my infant|newborn/.test(t)) goals.add('kids');
  // Pregnancy (phrases)
  if (/trying to conceive|trying for a baby|prenatal vitamin|during pregnancy|early pregnancy/.test(t)) goals.add('pregnancy');
  // Eye (phrases)
  if (/eye health|dry eyes|blurry vision|eye strain|screen time.*eye|macular health/.test(t)) goals.add('eye');

  // --- TIER 2: SINGLE KEYWORDS (fallback — only if goal not yet detected) ---
  if (!goals.has('sleep') && !goals.has('energy') && /\\bsleep\\b|insomnia/.test(t)) goals.add('sleep');
  if (!goals.has('energy') && /\\benergy\\b|\\btired\\b|\\bfatigue\\b|exhaust|sluggish|drained/.test(t)) goals.add('energy');
  if (!goals.has('stress') && /\\bstress\\b|anxiet|nervous|worried/.test(t)) goals.add('stress');
  if (!goals.has('immune') && /\\bimmune\\b|\\bsick\\b|\\bflu\\b|infection/.test(t)) goals.add('immune');
  if (!goals.has('gut') && /\\bgut\\b|digest|bloat|\\bstomach\\b|bowel|\\bibs\\b|constipat|diarr/.test(t)) goals.add('gut');
  if (!goals.has('sunburn') && !goals.has('skin') && /\\bskin\\b|acne|moistur|complexion|rash/.test(t)) goals.add('skin');
  if (!goals.has('hair') && /\\bhair\\b|\\bnail\\b|thinning|breakage|\\bbald/.test(t)) goals.add('hair');
  if (!goals.has('weight') && /\\bweight\\b|\\bslim\\b|\\bdiet\\b|calori/.test(t)) goals.add('weight');
  if (!goals.has('joint') && /\\bjoint\\b|muscle|\\bpain\\b|cramp|stiff|arthritis/.test(t)) goals.add('joint');
  if (!goals.has('heart') && /\\bheart\\b|cholesterol/.test(t)) goals.add('heart');
  if (!goals.has('kids') && /\\bkid\\b|\\bchild\\b|\\bbaby\\b|toddler|infant/.test(t)) goals.add('kids');
  if (!goals.has('pregnancy') && /pregnan|expecting|maternity/.test(t)) goals.add('pregnancy');
  if (!goals.has('eye') && /\\beye\\b|vision|lutein/.test(t)) goals.add('eye');
  if (!goals.has('focus') && /\\bfocus\\b|\\bmemory\\b|\\bcognitive\\b|concentration|\\bginkgo\\b/.test(t)) goals.add('focus');
  if (!goals.has('menopause') && /\\bmenopause\\b|\\bmenopace\\b|hot flush|hot flash/.test(t)) goals.add('menopause');
  if (!goals.has('uti') && /\\buti\\b|urinary|cystitis|cranberry/.test(t)) goals.add('uti');
  if (!goals.has('cold') && /\\bcold\\b|\\bflu\\b|echinacea|sore throat/.test(t)) goals.add('cold');
  if (!goals.has('mens') && /\\bprostate\\b|saw palmetto|wellman/.test(t)) goals.add('mens');
  if (!goals.has('womens') && /\\bpms\\b|wellwoman|agnus castus/.test(t)) goals.add('womens');
  if (!goals.has('blood_sugar') && /\\bdiabet\\b|chromium|berberine|\\bglucose\\b/.test(t)) goals.add('blood_sugar');
  if (!goals.has('liver') && /\\bliver\\b|milk thistle|detox/.test(t)) goals.add('liver');

  // sunburn implies skin too
  if (goals.has('sunburn')) goals.add('skin');
  // cold implies immune
  if (goals.has('cold')) goals.add('immune');

  return [...goals];
}"""

html = html.replace(old_parse_goals, new_parse_goals)

# ─────────────────────────────────────────────────────────────
# 5. REPLACE parseConditions()
# ─────────────────────────────────────────────────────────────
old_parse_conditions = """// Detect conditions from text for warnings
function parseConditions(text) {
  const t = text.toLowerCase();
  const conditions = [];
  if (/pregnan|expecting|trimester|zwanger/.test(t)) conditions.push('pregnant');
  if (/blood thinn|warfarin|anticoagul|aspirin daily|bloedverdunner/.test(t)) conditions.push('bloodthinners');
  if (/kidney|renal|nier/.test(t)) conditions.push('kidney');
  if (/diabet|insulin|blood sugar|bloedsuiker/.test(t)) conditions.push('diabetes');
  if (/thyroid|schildklier/.test(t)) conditions.push('thyroid');
  if (/breastfeed|nursing|lactating|borstvoeding/.test(t)) conditions.push('breastfeeding');
  if (/allerg|intoleran|celiac|gluten/.test(t)) conditions.push('allergy');
  return conditions;
}"""

new_parse_conditions = """// Detect conditions from text for warnings
function parseConditions(text) {
  const t = text.toLowerCase();
  const conditions = [];
  if (/pregnan|expecting|trimester/.test(t)) conditions.push('pregnant');
  if (/blood thinn|warfarin|anticoagul|aspirin daily/.test(t)) conditions.push('bloodthinners');
  if (/kidney|renal/.test(t)) conditions.push('kidney');
  if (/\\bdiabet\\b|insulin|blood sugar|glucose medication|on metformin/.test(t)) conditions.push('diabetes');
  if (/thyroid/.test(t)) conditions.push('thyroid');
  if (/breastfeed|nursing|lactating/.test(t)) conditions.push('breastfeeding');
  if (/allerg|intoleran|celiac|gluten/.test(t)) conditions.push('allergy');
  if (/menopause|hot flush|hot flash|perimenopause/.test(t)) conditions.push('menopause');
  return conditions;
}"""

html = html.replace(old_parse_conditions, new_parse_conditions)

# ─────────────────────────────────────────────────────────────
# 6. REPLACE getWhy() — add new goal cases before default
# ─────────────────────────────────────────────────────────────
old_why_sunburn = """    case 'sunburn':
      if (is('after sun|aftersun|post-uv|posthelios|after-sun')) return 'Specifically formulated to soothe and repair sun-exposed skin — cools redness, restores lost moisture, and helps skin recover after sun exposure.';
      if (is('spf|sunscreen|sun protection|sun cream|sun lotion')) return 'Broad-spectrum sun protection that shields skin from UVA and UVB damage — essential daily protection, especially in Malta\\'s intense sun.';
      return pName + ' soothes and repairs sunburned or sun-stressed skin.';
    default:
      return pName + ' is a quality health supplement from our Health Needs range.';
  }
}"""

new_why_sunburn = """    case 'sunburn':
      if (is('after sun|aftersun|post-uv|posthelios|after-sun')) return 'Specifically formulated to soothe and repair sun-exposed skin — cools redness, restores lost moisture, and helps skin recover after sun exposure.';
      if (is('spf|sunscreen|sun protection|sun cream|sun lotion')) return 'Broad-spectrum sun protection that shields skin from UVA and UVB damage — essential daily protection, especially in Malta\\'s intense sun.';
      return pName + ' soothes and repairs sunburned or sun-stressed skin.';
    case 'focus':
      if (is('lion\\'s mane|lions mane')) return 'Lion\\'s Mane mushroom is one of the most exciting nootropics in research — it supports nerve growth factor and may help with memory, concentration, and mental clarity.';
      if (is('ginkgo')) return 'Ginkgo Biloba improves cerebral blood flow and is one of the most widely used supplements for memory and cognitive performance.';
      if (is('choline|inositol')) return 'Choline is essential for neurotransmitter production, supporting memory, learning, and overall cognitive function.';
      if (is('equazen|eye q|efamol')) return 'This omega-3 formula is specifically designed for brain health — DHA is a key structural fat in the brain, supporting memory, concentration, and cognitive clarity.';
      if (isOmega) return 'Omega-3 DHA is one of the most important nutrients for brain function — regular supplementation supports memory, focus, and mental performance.';
      return pName + ' supports cognitive performance, focus, and mental clarity.';
    case 'menopause':
      if (is('menopace|vitabiotics menop')) return 'Menopace is a clinically formulated supplement designed specifically for menopause — providing targeted nutrients to ease symptoms and support women through this transition.';
      if (is('menovital|femarelle')) return 'A specialist menopause formula that helps reduce hot flushes, support hormonal balance, and maintain wellbeing during and after menopause.';
      if (is('agnus castus')) return 'Agnus Castus is one of the most studied herbal remedies for hormonal balance — it helps regulate the menstrual cycle and ease PMS and menopausal symptoms.';
      if (is('evening primrose|starflower')) return 'Evening Primrose Oil provides gamma-linolenic acid (GLA) which supports hormonal balance and is widely used to ease menopausal symptoms and PMS.';
      if (is('black cohosh')) return 'Black Cohosh is a clinically studied herbal remedy specifically for hot flushes and other menopausal symptoms.';
      if (is('neovadiol')) return 'Neovadiol is dermatologist-formulated for peri-menopausal skin, addressing the hormonal changes that affect skin density and hydration during this transition.';
      return pName + ' is formulated to support hormonal balance and ease menopausal symptoms.';
    case 'uti':
      if (is('cranberry')) return 'Cranberry is one of the most evidence-backed natural supplements for urinary tract health — it helps prevent bacteria from attaching to the bladder wall, reducing the frequency of UTIs.';
      if (is('d-mannose')) return 'D-Mannose is a natural sugar that prevents E. coli (the most common UTI cause) from adhering to the urinary tract lining — highly effective for frequent UTI sufferers.';
      if (is('cistit|urenal|kistinox')) return 'A targeted urinary tract support formula that helps soothe the bladder and urinary tract while reducing the discomfort of infection.';
      if (is('cranbiotix')) return 'Combines cranberry with beneficial probiotics to support both urinary tract and gut health simultaneously — ideal for women who get recurrent UTIs.';
      return pName + ' supports a healthy urinary tract and helps reduce the risk of recurrent infections.';
    case 'cold':
      if (is('echinacea')) return 'Echinacea is one of the most clinically researched herbs for fighting colds — it activates immune cells and can reduce the duration and severity of cold symptoms.';
      if (is('manuka')) return 'Manuka Honey has powerful antimicrobial properties and is highly effective for soothing sore throats and supporting immune defence during illness.';
      if (is('bee propolis|propolis')) return 'Bee Propolis has natural antibacterial and antiviral properties — an effective natural remedy for sore throats and immune support during cold and flu season.';
      if (isZinc && isVitC) return 'This zinc and vitamin C combination is one of the most effective formulas for fighting colds — both nutrients are essential for immune defence and can shorten illness duration.';
      if (isVitC) return 'High-dose vitamin C is one of the most effective immune boosters — it supports white blood cell function and can reduce the duration of cold symptoms.';
      if (isZinc) return 'Zinc is one of the most important minerals for fighting infection — it activates immune cells and is particularly effective taken at the first sign of a cold.';
      return pName + ' supports your immune system to fight cold and flu symptoms faster.';
    case 'mens':
      if (is('saw palmetto|prostace|prostate')) return 'Saw Palmetto supports healthy prostate function and is one of the most widely used supplements for men\\'s urinary and prostate health.';
      if (is('wellman')) return 'Wellman is a comprehensive men\\'s multivitamin formulated specifically for male health — covering energy, immunity, heart health, and more in one daily tablet.';
      if (is('l-arginine|arginine')) return 'L-Arginine is an amino acid that supports nitric oxide production, improving blood flow — widely used for cardiovascular health and male vitality.';
      if (is('testosterone|zinc')) return 'Zinc is essential for healthy testosterone production in men. Supplementing zinc can support hormonal health, energy, and male vitality.';
      return pName + ' is formulated to support men\\'s specific health needs and vitality.';
    case 'womens':
      if (is('wellwoman')) return 'Wellwoman is a comprehensive women\\'s multivitamin specifically formulated to support female health needs — covering energy, hormones, hair, skin, and immunity.';
      if (is('agnus castus')) return 'Agnus Castus helps regulate the menstrual cycle and ease PMS symptoms — one of the most trusted herbal remedies for women\\'s hormonal balance.';
      if (is('evening primrose|starflower')) return 'Evening Primrose Oil provides essential GLA fatty acids that support hormonal balance, ease PMS symptoms, and nourish skin from within.';
      if (is('nutrifem|femivital|biogena')) return 'A specialist women\\'s formula providing targeted nutrients for hormonal balance, energy, and female-specific nutritional needs.';
      if (isEPO) return 'Evening primrose oil is rich in GLA essential fatty acids — highly effective for easing PMS symptoms, hormonal balance, and skin hydration.';
      return pName + ' supports women\\'s hormonal health, energy, and overall female wellbeing.';
    case 'blood_sugar':
      if (is('chromium')) return 'Chromium picolinate is a well-researched mineral that improves insulin sensitivity and helps regulate blood sugar levels — reducing cravings and supporting healthy glucose metabolism.';
      if (is('berberine')) return 'Berberine is one of the most studied natural compounds for blood sugar control — it activates AMPK, improving insulin sensitivity comparable to some medications.';
      if (is('cinnamon')) return 'Cinnamon has been shown in multiple studies to improve insulin sensitivity and lower fasting blood sugar levels, making it a useful daily supplement for glucose management.';
      if (is('alpha lipoic|lipoic acid')) return 'Alpha Lipoic Acid is a powerful antioxidant that improves insulin sensitivity and helps protect against oxidative damage associated with high blood sugar.';
      if (is('glicem')) return 'A comprehensive blood sugar support formula combining multiple evidence-backed ingredients to help maintain healthy glucose levels throughout the day.';
      return pName + ' supports healthy blood sugar levels and glucose metabolism.';
    case 'liver':
      if (is('milk thistle')) return 'Milk Thistle (silymarin) is the most clinically studied herb for liver health — it protects liver cells from damage, supports regeneration, and helps with detoxification.';
      if (is('liverbiotix')) return 'A comprehensive liver support formula combining multiple liver-protective ingredients including probiotics to support both gut and liver health simultaneously.';
      if (is('dandelion')) return 'Dandelion root has natural liver-supportive properties and helps stimulate bile production, aiding fat digestion and gentle liver detoxification.';
      return pName + ' supports healthy liver function and natural detoxification.';
    default:
      return pName + ' is a quality health supplement from our Health Needs range.';
  }
}"""

html = html.replace(old_why_sunburn, new_why_sunburn)

# ─────────────────────────────────────────────────────────────
# 7. REPLACE scoring in getRecommendations()
# ─────────────────────────────────────────────────────────────
old_scoring = """      // Specificity bonus: product covering fewer total goals = more targeted
      const specificity = 1 / product.goals.length;
      // Match ratio: what % of user goals does this product cover
      const matchRatio = matchedGoals.length / Math.max(allGoals.length, 1);
      // Raw match count still matters but is weighted down for broad products
      const score = (matchedGoals.length * 2) + (specificity * 3) + (matchRatio * 2);"""

new_scoring = """      // Specificity bonus: product covering fewer total goals = more targeted
      const specificity = 1 / product.goals.length;
      // Match ratio: what % of user goals does this product cover
      const matchRatio = matchedGoals.length / Math.max(allGoals.length, 1);
      // Primary goal bonus: strongly reward products whose PRIMARY goal matches what the user needs
      const primaryBonus = (product.primary && allGoals.includes(product.primary)) ? 4 : 0;
      // Raw match count still matters but is weighted down for broad products
      const score = primaryBonus + (matchedGoals.length * 2) + (specificity * 3) + (matchRatio * 2);"""

html = html.replace(old_scoring, new_scoring)

# ─────────────────────────────────────────────────────────────
# 8. REPLACE deduplication — smarter, also dedupe by primary goal
# ─────────────────────────────────────────────────────────────
old_dedup = """  // Deduplicate categories — don't show 3 magnesium products
  const seen = new Set();
  const deduped = [];
  for (const item of scored) {
    const cat = item.product.category;
    const name = item.product.name.split(' ')[0]; // first word as loose dedup key
    const key = `${cat}-${name}`;
    if (!seen.has(key)) {
      seen.add(key);
      deduped.push(item);
    }
    if (deduped.length === 3) break;
  }"""

new_dedup = """  // Deduplicate — don't show 3 similar products:
  // 1. Don't repeat same category-prefix combo
  // 2. Don't show 2+ products with the same primary goal when user has multiple needs
  const seenKeys = new Set();
  const seenPrimaries = new Set();
  const deduped = [];
  const multiGoalUser = allGoals.length > 1;

  for (const item of scored) {
    const cat = item.product.category;
    const nameFirst = item.product.name.split(' ')[0];
    const catKey = `${cat}-${nameFirst}`;
    const pri = item.product.primary;

    // Skip if exact category-name combo seen
    if (seenKeys.has(catKey)) continue;

    // If user has multiple goals, limit 1 product per primary goal
    // (avoids showing 3 magnesium products when user said sleep+energy+stress)
    if (multiGoalUser && pri && seenPrimaries.has(pri)) continue;

    seenKeys.add(catKey);
    if (pri) seenPrimaries.add(pri);
    deduped.push(item);

    if (deduped.length === 3) break;
  }"""

html = html.replace(old_dedup, new_dedup)

# ─────────────────────────────────────────────────────────────
# 9. Use product.primary as the goal for getWhy
# ─────────────────────────────────────────────────────────────
old_why_call = """    const primaryGoal = allGoals.find(g => p.goals.includes(g));
    const why = getWhy(p, primaryGoal);"""

new_why_call = """    // Use the product's own primary goal for the why message (most accurate)
    const primaryGoal = (p.primary && p.goals.includes(p.primary))
      ? p.primary
      : (allGoals.find(g => p.goals.includes(g)) || p.primary);
    const why = getWhy(p, primaryGoal);"""

html = html.replace(old_why_call, new_why_call)

# ─────────────────────────────────────────────────────────────
# WRITE OUTPUT
# ─────────────────────────────────────────────────────────────
with open('/home/user/healthneeds-recommender/index.html', 'w') as f:
    f.write(html)

print("Done! File size:", len(html), "bytes")
print("File size in KB:", len(html) / 1024)
