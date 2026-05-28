#!/usr/bin/env python3
"""
Generate optimized PRODUCTS array for Health Needs recommender.
Reads Excel catalog, applies goal classification, outputs compact JS.
"""

import openpyxl
import re
import json
from collections import defaultdict

wb = openpyxl.load_workbook(
    '/root/.claude/uploads/f9b9c490-d9dd-4198-b244-3808ad6c64d9/0b7a2949-HN_Data.xlsx',
    read_only=True
)
ws = wb.active
rows = list(ws.iter_rows(values_only=True))
# headers: ID, Type, SKU, Name, Published, Description, SalePrice, RegularPrice, Categories, Tags, Brands
published = [r for r in rows[1:] if r[4] == 1]


def n(row): return (row[3] or '').strip()
def nl(row): return n(row).lower()
def cats(row): return (row[8] or '').lower()
def tags(row): return (row[9] or '').lower()
def desc(row): return (row[5] or '').lower()
def brand(row): return (row[10] or '').strip()


def has(row, *kws):
    t = nl(row) + ' ' + tags(row) + ' ' + cats(row)
    return any(kw in t for kw in kws)


def has_name(row, *kws):
    t = nl(row)
    return any(kw in t for kw in kws)


def has_desc(row, *kws):
    t = nl(row) + ' ' + tags(row) + ' ' + cats(row) + ' ' + desc(row)[:500]
    return any(kw in t for kw in kws)


# ─────────────────────────────────────────────────────────────
# CLASSIFY GOALS
# Returns (primary_goal, [all_goals], who, warnings_dict, category_label)
# ─────────────────────────────────────────────────────────────

def classify(row):
    nm = nl(row)
    tg = tags(row)
    ct = cats(row)
    ds = desc(row)[:600]
    all_text = nm + ' ' + tg + ' ' + ct + ' ' + ds
    goals = set()
    primary = None
    who = ['adult', 'woman', 'man']
    warnings = {}

    # ── BABY / KIDS ──────────────────────────────────────────
    is_baby = ('baby' in ct or 'child' in ct or 'infant' in ct or
               'kids' in nm or 'children' in nm or 'baby' in nm or
               'mini drops' in nm or 'infant' in nm or 'toddler' in nm or
               'magic beans' in nm or 'chewy vites' in nm or 'haliborange' in nm or
               'actikid' in nm.replace(' ', '') or 'pro-ven kids' in nm or
               'actikid' in tg or 'baby and child' in ct or
               ('gummies' in nm and ('kids' in nm or 'children' in nm or 'child' in ct)))
    is_kids_multi = is_baby or 'kids' in nm or 'children' in nm

    if is_baby:
        who = ['baby']
    elif ('wellwoman' in nm or 'menopace' in nm or 'menovital' in nm or
          'femarelle' in nm or 'biogena nutrifem' in nm or
          'pregnacare' in nm or 'gestarelle' in nm or
          'optibac for women' in nm or 'optibac women' in nm or 'proven women' in nm or
          'fertilovit f' in nm or 'femivital' in nm or 'xtrasim 700 wom' in nm or
          'xtrasim 700 woman' in nm or 'xtraslim 700 woman' in nm or
          'nutrifem' in nm or 'biogena femme' in nm or
          re.search(r'\bwomen\b|\bwoman\b|\bfemale\b', nm) or
          re.search(r'\bwomen\b|\bwoman\b|\bfemale\b', ct) or
          re.search(r'\bwomen\b|\bwoman\b', tg)):
        who = ['adult', 'woman']
    elif ('wellman' in nm or 'prostace' in nm or 'prostate' in nm or 'saw palmetto' in nm or
          'prostanox' in nm or 'fertilovit m' in nm or
          re.search(r'\bmen\b', nm) or
          re.search(r'\bmen\b', ct) or re.search(r'\bmen\b', tg) or
          re.search(r'\bman\b', nm)):
        who = ['adult', 'man']

    # ── PREGNANCY ────────────────────────────────────────────
    is_preg = ('pregnancy' in ct or 'prenatal' in nm or 'pregnacare' in nm or
               'gestarelle' in nm or 'expecting' in nm or
               'folic acid' in nm or 'folic' in nm or
               'pregnancy' in tg or 'maternity' in ct)
    if is_preg:
        goals.add('pregnancy')
        if 'folic' in nm or 'pregnacare' in nm or 'gestarelle' in nm:
            primary = 'pregnancy'
            who = ['adult', 'woman']

    # ── SLEEP ────────────────────────────────────────────────
    is_sleep = ('melatonin' in nm or 'valerian' in nm or 'sleep' in nm or
                'insomnia' in nm or 'slumber' in nm or 'night' in nm and 'sleep' in tg or
                'sleep' in tg or 'sleep support' in ct)
    if is_sleep:
        goals.add('sleep')
        if 'melatonin' in nm or 'valerian' in nm or 'sleep' in nm:
            if primary is None: primary = 'sleep'

    # ── STRESS / ANXIETY ──────────────────────────────────────
    is_stress = ('ashwagandha' in nm or 'rhodiola' in nm or
                 'l-theanine' in nm or 'theanine' in nm or
                 'stress' in nm or 'anxiety' in nm or 'calm' in nm or
                 'relax' in nm or 'stress' in tg)
    if is_stress:
        goals.add('stress')
        if 'ashwagandha' in nm or 'rhodiola' in nm:
            if primary is None: primary = 'stress'

    # ── ENERGY ───────────────────────────────────────────────
    is_energy = ('iron' in nm or 'ferrous' in nm or 'spatone' in nm or 'floradix' in nm or
                 'ferritin' in nm or 'b12' in nm or 'b-12' in nm or
                 'coq10' in nm or 'coenzyme q10' in nm or 'ubiquinol' in nm or
                 'b complex' in nm or 'b-complex' in nm or
                 'energy' in nm or 'fatigue' in nm or 'tiredness' in nm or
                 'vitality' in nm or 'berocca' in nm or
                 'l-carnitine' in nm or 'carnitine' in nm or
                 'siberian ginseng' in nm or 'korean ginseng' in nm or
                 'spirulina' in nm or 'moringa' in nm or
                 'iron' in tg or 'energy' in tg or
                 'b vitamin' in tg.replace('vitamin b', 'b vitamin'))
    if is_energy:
        goals.add('energy')
        if 'iron' in nm or 'ferrous' in nm or 'spatone' in nm:
            if primary is None: primary = 'energy'
            warnings['default'] = '⚠️ Do not take iron supplements without confirmed low iron levels. Check with your doctor if unsure.'
        elif 'coq10' in nm or 'coenzyme q10' in nm or 'ubiquinol' in nm:
            if primary is None: primary = 'energy'

    # ── IMMUNE ───────────────────────────────────────────────
    is_immune = ('echinacea' in nm or 'elderberry' in nm or 'elderflower' in nm or
                 'bee propolis' in nm or 'propolis' in nm or
                 'vitamin c' in nm or 'vit c' in nm or
                 'zinc' in nm or 'zinc' in tg or
                 'immune' in nm or 'immunity' in nm or 'immune' in tg or
                 'black elderberry' in nm)
    if is_immune:
        goals.add('immune')
        if 'echinacea' in nm or 'bee propolis' in nm or 'elderberry' in nm:
            if primary is None: primary = 'immune'

    # ── GUT ──────────────────────────────────────────────────
    is_gut = ('probiotic' in nm or 'lactobacillus' in nm or 'bifidobacterium' in nm or
              'optibac' in nm or 'actigut' in nm or 'biogaia' in nm or
              'digestive' in nm or 'digestion' in nm or 'bloat' in nm or
              'gut' in nm or 'bowel' in nm or 'constipat' in nm or
              'psyllium' in nm or 'fibre' in nm or 'fiber' in nm or
              'enzyme' in nm and 'digest' in all_text or
              'probiotic' in tg or 'probiotics' in ct or
              'ibs' in nm or 'aloe vera' in nm)
    if is_gut:
        goals.add('gut')
        if 'probiotic' in nm or 'optibac' in nm or 'actigut' in nm or 'biogaia' in nm:
            if primary is None: primary = 'gut'

    # ── SKIN ─────────────────────────────────────────────────
    is_skin = ('collagen' in nm or 'hyaluronic' in nm or 'biotin' in nm or
               'skin' in nm and ('supplement' in ct or 'vitamin' in ct or 'capsule' in nm) or
               'beauty' in nm or 'ceramide' in nm or 'retinol' in nm or
               'vitamin e' in nm or
               'evening primrose' in nm or 'starflower' in nm or
               'skin' in tg or 'anti-aging' in tg or 'antiaging' in tg)
    if is_skin:
        goals.add('skin')
        if 'collagen' in nm:
            if primary is None: primary = 'skin'

    # ── SUNBURN ──────────────────────────────────────────────
    is_sun = ('after sun' in nm or 'aftersun' in nm or 'after-sun' in nm or
              'post-uv' in nm or 'posthelios' in nm or 'sun care' in ct or
              'suncare' in ct or 'sunscreen' in ct or 'sunblock' in ct or
              'spf' in nm or 'sun protection' in nm or 'sun screen' in nm or
              'aftersun' in tg or 'after sun' in tg)
    if is_sun:
        goals.add('sunburn')
        goals.add('skin')
        if primary is None: primary = 'sunburn'

    # ── HAIR ─────────────────────────────────────────────────
    is_hair = ('hair' in nm and ('supplement' in ct or 'vitamin' in ct or 'capsule' in nm or 'tablet' in nm) or
               'biotin' in nm or 'pantogar' in nm or 'hairvit' in nm or
               'hair' in tg or 'hair loss' in tg or 'hair growth' in tg or
               'hair and nails' in nm or 'hair and scalp' in nm)
    if is_hair:
        goals.add('hair')
        if 'pantogar' in nm or 'hairvit' in nm:
            if primary is None: primary = 'hair'

    # ── JOINT / BONE ─────────────────────────────────────────
    is_joint = ('glucosamine' in nm or 'chondroitin' in nm or 'msm' in nm or
                'joint' in nm or 'arthritis' in nm or 'cartilage' in nm or
                'calcium' in nm or 'osteocare' in nm or 'bone' in nm or
                'turmeric' in nm or 'curcumin' in nm or
                'collagen' in nm or 'flexijoint' in nm or
                'joint' in tg or 'glucosamine' in tg)
    if is_joint:
        goals.add('joint')
        if 'glucosamine' in nm or 'chondroitin' in nm:
            if primary is None: primary = 'joint'
        elif 'turmeric' in nm or 'curcumin' in nm:
            if primary is None: primary = 'joint'

    # ── HEART ────────────────────────────────────────────────
    is_heart = ('omega' in nm or 'fish oil' in nm or 'cod liver' in nm or
                'marine lipid' in nm or 'krill' in nm or
                'coq10' in nm or 'coenzyme q10' in nm or 'ubiquinol' in nm or
                'plant sterol' in nm or 'stanol' in nm or
                'garlic' in nm or
                'cholesterol' in nm or 'heart' in nm or
                'omega' in tg or 'fish oil' in tg or 'cardiovascular' in tg)
    if is_heart:
        goals.add('heart')
        if 'omega' in nm or 'fish oil' in nm or 'cod liver' in nm:
            if primary is None: primary = 'heart'
        elif 'plant sterol' in nm or 'cholesterol' in nm:
            if primary is None: primary = 'heart'

    # ── WEIGHT ───────────────────────────────────────────────
    is_weight = ('weight loss' in nm or 'slimming' in nm or 'slim' in nm or
                 'fat burn' in nm or 'metabolism' in nm or
                 'nupo' in nm or 'meal replacement' in nm or
                 'green tea' in nm or 'l-carnitine' in nm or 'carnitine' in nm or
                 'apple cider' in nm or 'cla' in nm or
                 'weight loss' in ct or 'weight' in tg and 'loss' in tg)
    if is_weight:
        goals.add('weight')
        if 'nupo' in nm or 'meal replacement' in nm or 'slimming' in nm:
            if primary is None: primary = 'weight'

    # ── EYE ──────────────────────────────────────────────────
    is_eye = ('lutein' in nm or 'zeaxanthin' in nm or 'bilberry' in nm or
              'eyebright' in nm or 'vision' in nm or 'eye q' in nm or
              'eye health' in nm or 'macu' in nm or
              'lutein' in tg or 'eye health' in tg or 'vision' in tg)
    if is_eye:
        goals.add('eye')
        if 'lutein' in nm or 'zeaxanthin' in nm or 'bilberry' in nm:
            if primary is None: primary = 'eye'

    # ── FOCUS / BRAIN ────────────────────────────────────────
    is_focus = ('ginkgo' in nm or 'lion\'s mane' in nm or 'lions mane' in nm or
                'choline' in nm or 'phosphatidylserine' in nm or
                'bacopa' in nm or 'brain' in nm or 'memory' in nm or
                'cognitive' in nm or 'focus' in nm or
                'eye q' in nm or 'equazen' in nm or
                'efamol' in nm or 'efamol active memory' in nm or
                'omega-3' in tg and 'brain' in tg or 'brain health' in tg or
                'lion' in tg and 'mane' in tg)
    if is_focus:
        goals.add('focus')
        if 'ginkgo' in nm or 'lion' in nm and 'mane' in nm or 'choline' in nm or \
           'memory' in nm or 'efamol active memory' in nm:
            if primary is None: primary = 'focus'
        elif 'equazen' in nm or 'eye q' in nm:
            if primary is None: primary = 'focus'

    # ── MENOPAUSE ────────────────────────────────────────────
    is_meno = ('menopause' in nm or 'menopace' in nm or 'menovital' in nm or
               'meno' in nm or 'hot flush' in nm or 'hot flash' in nm or
               'black cohosh' in nm or 'red clover' in nm or 'femarelle' in nm or
               'menopause' in tg or 'peri-menopause' in nm or 'neovadiol' in nm or
               'agnus castus' in nm or 'pms' in tg and 'menopause' in tg)
    if is_meno:
        goals.add('menopause')
        who = ['adult', 'woman']
        if 'menopace' in nm or 'menovital' in nm or 'femarelle' in nm or 'menopause' in nm:
            if primary is None: primary = 'menopause'
        elif 'agnus castus' in nm or 'agnus' in nm:
            if primary is None: primary = 'menopause'

    # ── UTI / URINARY ────────────────────────────────────────
    is_uti = ('cranberry' in nm or 'd-mannose' in nm or 'urinary' in nm or
              'cistit' in nm or 'kistinox' in nm or 'urenal' in nm or
              'cystitis' in nm or 'bladder' in nm or
              'cranbiotix' in nm or 'cran' in nm and 'sachet' in nm or
              'urinary' in tg or 'cranberry' in tg)
    if is_uti:
        goals.add('uti')
        if 'cranberry' in nm or 'd-mannose' in nm or 'cistit' in nm or \
           'urenal' in nm or 'kistinox' in nm:
            if primary is None: primary = 'uti'

    # ── COLD / FLU ───────────────────────────────────────────
    is_cold = ('echinacea' in nm or 'manuka' in nm or 'bee propolis' in nm or
               'cold' in nm and ('flu' in nm or 'immune' in nm or 'relief' in nm) or
               'zinc' in nm and 'vitamin c' in nm or 'actifizz' in nm.replace(' ', '') or
               'cold and flu' in ct or 'coughs' in ct or
               'cold' in tg and 'flu' in tg or 'sore throat' in tg)
    if is_cold:
        goals.add('cold')
        goals.add('immune')
        if 'echinacea' in nm or 'bee propolis' in nm or 'manuka' in nm:
            if primary is None: primary = 'cold'

    # ── MEN'S HEALTH ────────────────────────────────────────
    is_mens = ('saw palmetto' in nm or 'prostace' in nm or 'prostate' in nm or
               'wellman' in nm or 'prostanox' in nm or
               'testosterone' in nm or 'l-arginine' in nm or
               'mens health' in tg or 'prostate' in tg or 'men\'s health' in tg)
    if is_mens:
        goals.add('mens')
        who = ['adult', 'man']
        if 'saw palmetto' in nm or 'prostace' in nm or 'prostate' in nm or 'wellman' in nm:
            if primary is None: primary = 'mens'

    # ── WOMEN'S HEALTH ──────────────────────────────────────
    is_womens = ('wellwoman' in nm or 'agnus castus' in nm or
                 'evening primrose' in nm or 'starflower' in nm or
                 'pms' in nm or 'period' in nm and 'pain' in nm or
                 'hormonal' in nm or 'femivital' in nm or
                 'royal 3' in nm or 'nutrifem' in nm or
                 'pms' in tg or 'hormonal balance' in tg or
                 'optibac for women' in nm or 'optibac women' in nm)
    if is_womens:
        goals.add('womens')
        who = ['adult', 'woman']
        if 'wellwoman' in nm or 'nutrifem' in nm or 'femivital' in nm:
            if primary is None: primary = 'womens'
        elif 'evening primrose' in nm or 'starflower' in nm:
            if primary is None: primary = 'womens'
        elif 'agnus castus' in nm:
            if primary is None: primary = 'womens'

    # ── BLOOD SUGAR ──────────────────────────────────────────
    is_bs = ('chromium' in nm or 'berberine' in nm or 'cinnamon' in nm or
             'alpha lipoic' in nm or 'blood sugar' in nm or
             'glicem' in nm or 'glucose' in nm and 'supplement' in ct or
             'chromium' in tg or 'blood sugar' in tg or 'berberine' in tg)
    if is_bs:
        goals.add('blood_sugar')
        if 'chromium' in nm or 'berberine' in nm or 'blood sugar' in nm or 'glicem' in nm:
            if primary is None: primary = 'blood_sugar'
        warnings['diabetes'] = '⚠️ If you are diabetic or on blood sugar medication, consult your doctor before use as this may affect glucose levels.'

    # ── LIVER ────────────────────────────────────────────────
    is_liver = ('milk thistle' in nm or 'silymarin' in nm or
                'liver' in nm and ('support' in nm or 'health' in nm or 'detox' in nm or 'supplement' in ct) or
                'liverbiotix' in nm or 'dandelion' in nm or
                'liver' in tg and 'support' in tg)
    if is_liver:
        goals.add('liver')
        if 'milk thistle' in nm or 'silymarin' in nm or 'liverbiotix' in nm:
            if primary is None: primary = 'liver'

    # ── KIDS MULTIVITAMIN ────────────────────────────────────
    if is_baby or is_kids_multi:
        goals.add('kids')
        if primary is None and ('vitamin' in nm or 'multi' in nm or 'supplement' in ct):
            primary = 'kids'

    # Multivitamins — add many goals
    if ('multivitamin' in nm or 'multi-vitamin' in nm or 'multi vitamin' in nm or
            'centrum' in nm or 'wellman' in nm or 'wellwoman' in nm or
            'berocca' in nm or 'pregnacare' in nm or 'gestarelle' in nm or
            'forte pharma immuvit' in nm or 'koregin' in nm or 'additiva multivit' in nm):
        goals.update(['energy', 'immune'])
        if 'wellwoman' in nm:
            goals.update(['womens', 'hair', 'skin', 'energy', 'immune'])
            if primary is None: primary = 'womens'
        elif 'wellman' in nm and 'conception' not in nm:
            goals.update(['mens', 'energy', 'immune'])
            if primary is None: primary = 'mens'
        elif 'pregnacare' in nm or 'gestarelle' in nm:
            goals.add('pregnancy')
            if primary is None: primary = 'pregnancy'
        elif 'centrum men' in nm or 'men 50+' in nm or 'men 70+' in nm:
            if primary is None: primary = 'mens'
        elif 'centrum women' in nm or 'women 50+' in nm or 'women 70+' in nm:
            if primary is None: primary = 'womens'
        else:
            if primary is None: primary = 'energy'  # generic multi → energy

    # Fallback primary: pick the "first" goal assigned
    if primary is None and goals:
        # Priority order for primary
        priority = ['sleep', 'stress', 'menopause', 'uti', 'cold', 'mens', 'womens',
                    'blood_sugar', 'liver', 'focus', 'energy', 'immune', 'gut', 'skin',
                    'hair', 'joint', 'heart', 'weight', 'eye', 'pregnancy', 'kids', 'sunburn']
        for p in priority:
            if p in goals:
                primary = p
                break
        if primary is None:
            primary = list(goals)[0]

    # Sun products must have goals
    if not goals and is_sun:
        goals.update(['sunburn', 'skin'])
        primary = 'sunburn'

    # Omega-3 — add heart and eye
    if 'omega' in nm or 'fish oil' in nm or 'cod liver' in nm:
        goals.update(['heart'])
        if 'dha' in all_text or 'eye' in tg or 'brain' in tg:
            goals.add('eye')

    # Children's omega / brain
    if is_baby and ('omega' in nm or 'equazen' in nm or 'efamol' in nm):
        goals.update(['kids', 'focus'])
        if primary is None: primary = 'focus'

    # Pregnancy supplements also add energy/immune
    if 'pregnancy' in goals:
        goals.update(['energy', 'immune'])
        who = ['adult', 'woman']

    # Blood thinners warning for Omega, VitK
    if ('omega' in nm or 'fish oil' in nm or 'vitamin k' in nm or 'vitamin k2' in nm):
        warnings['bloodthinners'] = '⚠️ May interact with blood-thinning medication. Please consult your doctor or pharmacist before use.'

    # Iron warning
    if 'iron' in nm and ('supplement' in ct or 'mineral' in ct or 'tablet' in nm or 'capsule' in nm):
        warnings['default'] = '⚠️ Do not take iron supplements without confirmed low iron levels. Check with your doctor if unsure.'

    # Determine category label
    cat_label = get_category_label(row)

    return primary, sorted(goals), who, warnings, cat_label


def get_category_label(row):
    nm = nl(row)
    ct = cats(row)
    tg = tags(row)

    if 'after sun' in nm or 'aftersun' in nm or 'after-sun' in nm or 'posthelios' in nm or 'post-uv' in nm:
        return 'After Sun'
    if 'spf' in nm or 'sunscreen' in ct or 'sunblock' in ct or 'sun protection' in nm:
        return 'Sun Protection'
    if 'probiotic' in nm or 'optibac' in nm or 'actigut' in nm or 'biogaia' in nm or 'probiotic' in ct:
        return 'Probiotics'
    if 'melatonin' in nm: return 'Melatonin'
    if 'valerian' in nm: return 'Valerian'
    if 'ashwagandha' in nm: return 'Ashwagandha'
    if 'rhodiola' in nm: return 'Rhodiola'
    if 'milk thistle' in nm: return 'Milk Thistle'
    if 'magnesium' in nm: return 'Magnesium'
    if 'iron' in nm or 'ferrous' in nm or 'spatone' in nm or 'floradix' in nm: return 'Iron'
    if 'folic acid' in nm or 'folate' in nm: return 'Folic Acid'
    if 'vitamin c' in nm: return 'Vitamin C'
    if 'vitamin d' in nm or 'vitamin d3' in nm: return 'Vitamin D'
    if 'vitamin b12' in nm or 'b12' in nm: return 'Vitamin B12'
    if 'vitamin b' in nm or 'b complex' in nm or 'b-complex' in nm: return 'Vitamin B'
    if 'vitamin e' in nm: return 'Vitamin E'
    if 'vitamin a' in nm: return 'Vitamin A'
    if 'zinc' in nm: return 'Zinc'
    if 'calcium' in nm or 'osteocare' in nm: return 'Calcium'
    if 'collagen' in nm: return 'Collagen'
    if 'hyaluronic' in nm: return 'Hyaluronic Acid'
    if 'biotin' in nm: return 'Biotin'
    if 'omega' in nm or 'fish oil' in nm or 'cod liver' in nm or 'krill' in nm: return 'Omega-3'
    if 'glucosamine' in nm or 'chondroitin' in nm: return 'Glucosamine'
    if 'coq10' in nm or 'coenzyme q10' in nm or 'ubiquinol' in nm: return 'CoQ10'
    if 'turmeric' in nm or 'curcumin' in nm: return 'Turmeric'
    if 'l-theanine' in nm or 'theanine' in nm: return 'L-Theanine'
    if 'l-carnitine' in nm or 'carnitine' in nm: return 'L-Carnitine'
    if 'spirulina' in nm or 'moringa' in nm: return 'Spirulina'
    if 'garlic' in nm: return 'Garlic'
    if 'green tea' in nm: return 'Green Tea'
    if 'echinacea' in nm: return 'Echinacea'
    if 'elderberry' in nm or 'elderflower' in nm: return 'Elderberry'
    if 'bee propolis' in nm or 'propolis' in nm: return 'Bee Propolis'
    if 'manuka' in nm: return 'Manuka Honey'
    if 'cranberry' in nm or 'cranbiotix' in nm or 'cran' in nm: return 'Cranberry'
    if 'd-mannose' in nm: return 'D-Mannose'
    if 'cistit' in nm or 'urenal' in nm or 'kistinox' in nm: return 'Urinary Support'
    if 'agnus castus' in nm: return 'Agnus Castus'
    if 'evening primrose' in nm or 'starflower' in nm: return 'Evening Primrose Oil'
    if 'menopace' in nm or 'menovital' in nm or 'femarelle' in nm or 'menopause' in nm: return 'Menopause Support'
    if 'saw palmetto' in nm: return 'Saw Palmetto'
    if 'chromium' in nm: return 'Chromium'
    if 'cinnamon' in nm: return 'Cinnamon'
    if 'berberine' in nm: return 'Berberine'
    if 'alpha lipoic' in nm: return 'Alpha Lipoic Acid'
    if 'ginkgo' in nm: return 'Ginkgo Biloba'
    if 'lion' in nm and 'mane' in nm: return "Lion's Mane"
    if 'choline' in nm: return 'Choline'
    if 'equazen' in nm or 'eye q' in nm or 'efamol' in nm: return 'Brain Omega-3'
    if 'lutein' in nm or 'zeaxanthin' in nm: return 'Eye Health'
    if 'bilberry' in nm or 'eyebright' in nm: return 'Eye Support'
    if 'ginseng' in nm: return 'Ginseng'
    if 'aloe vera' in nm: return 'Aloe Vera'
    if 'pantogar' in nm: return 'Hair Supplement'
    if 'nupo' in nm or 'meal replacement' in nm: return 'Meal Replacement'
    if 'pregnancy' in ct or 'maternity' in ct or 'pregna' in nm: return 'Pregnancy'
    # Wellman/Wellwoman get their own categories (BEFORE generic multivitamin check)
    if 'wellwoman' in nm: return "Women's Multivitamin"
    if 'wellman' in nm: return "Men's Multivitamin"
    if 'centrum' in nm: return 'Multivitamin'
    if 'multivitamin' in nm or 'multi vitamin' in nm or 'multivitamin' in ct:
        return 'Multivitamin'
    if 'berocca' in nm: return 'Vitamin B Complex'
    if 'pantogar' in nm: return 'Hair Supplement'
    if 'baby' in ct or 'child' in ct or 'infant' in ct or 'kids' in nm: return 'Children\'s Health'
    if 'liverbiotix' in nm or 'liver' in nm: return 'Liver Support'
    if 'weight' in ct or 'slimming' in nm: return 'Weight Management'
    if 'supplement' in ct: return 'Supplement'
    if 'vitamin' in ct: return 'Vitamin'
    if 'mineral' in ct: return 'Mineral'
    return 'Health Supplement'


# ─────────────────────────────────────────────────────────────
# KNOWN GOOD BRANDS (priority)
# ─────────────────────────────────────────────────────────────
PRIORITY_BRANDS = {
    'Vitabiotics', 'Quest', 'Healthaid', 'Health Aid', 'Nature\'s Aid', 'Natures Aid',
    'Optibac', 'BetterYou', 'Igennus', 'Centrum', 'Berocca', 'Manuka Health',
    'Avène', 'La Roche-Posay', 'Bioderma', 'Eucerin', 'Seven Seas',
    'Equazen', 'Efamol', 'Biogaia', 'Laborest', 'Erba Vita',
    'Nupo', 'Weightworld', 'Walmark', 'Puressentiel', 'Pantogar',
    'Mushrooms For Life', 'Femarelle', 'Biogena', 'Proven',
    'ActiFizz', 'ActiKid', 'ActiGut', 'Advancis', 'Forte Pharma',
    'Isdin', 'Maxivita', 'Ryvax', 'Medicare', 'Vichy',
    'Haliborange', 'Chewy Vites', 'Pro-Ven'
}


def is_priority_brand(row):
    b = brand(row)
    return b in PRIORITY_BRANDS


# ─────────────────────────────────────────────────────────────
# PRODUCT SELECTION STRATEGY
# ─────────────────────────────────────────────────────────────

# Filter to supplement/health relevant products only (exclude pure toiletries/skincare)
def is_supplement_or_health(row):
    ct = row[8] or ''  # raw, may contain \\,
    nm = nl(row)
    tg = tags(row)
    # Include vitamins/supplements/minerals (note: backslash-comma in raw data)
    incl_cats = ['Vitamins', 'Minerals', 'Supplements', 'Mother & Baby',
                 'Suncare', 'Sunscreen', 'After Sun', 'Coughs', 'Throat Care',
                 'Sleep support', 'Weight Loss', 'Probiotics', 'Omega',
                 'Fish oils', 'Glucosamine', 'Essential Oils', 'Collagen',
                 'Iron', 'Calcium', 'Magnesium', 'Zinc']
    if any(x in ct for x in incl_cats):
        return True
    if 'after sun' in nm or 'aftersun' in nm or 'spf' in nm:
        return True
    # Exclude pure toiletries/dental/grooming/baby-formula/nappies
    excl = ['Dental Care', 'Fragrances', 'Shower Gel', 'Shampoo', 'Deodorant',
            'Nappies', 'Wipes', 'Dummies', 'Baby Feed & Care > Food', 'Bath time',
            'Bottles and Teats', 'Grooming', 'Shaving', 'Feminine Care',
            'First Aid', 'Foot Care', 'Insoles', 'Braces', 'Medical Devices']
    if any(x in ct for x in excl):
        return False
    return False


# Run classification on all relevant products
all_rows = [r for r in published if is_supplement_or_health(r)]
print(f"Candidate products: {len(all_rows)}")

classified = []
for row in all_rows:
    primary, goals, who, warnings, cat_label = classify(row)
    if goals:
        classified.append({
            'name': n(row),
            'category': cat_label,
            'primary': primary,
            'goals': goals,
            'who': who,
            'warnings': warnings,
            'brand': brand(row),
            '_priority': is_priority_brand(row)
        })

print(f"Classified with goals: {len(classified)}")


# ─────────────────────────────────────────────────────────────
# DEDUPLICATION — keep best per (primary_goal, category_label)
# ─────────────────────────────────────────────────────────────

# Group by (primary, category) and keep best
# Limits: max 3 per specific ingredient type, max 5 for broader types
BROAD_CATEGORIES = {
    'Multivitamin', 'Vitamin B', 'Vitamin D', 'Vitamin C', 'Omega-3',
    'Iron', 'Magnesium', 'Zinc', 'Probiotics', 'Calcium', 'Sun Protection',
    'After Sun', "Children's Health", 'Glucosamine', 'Vitamin B12',
    'Collagen', 'Biotin', 'Ginseng', 'Vitamin B Complex', 'Evening Primrose Oil',
    'Ashwagandha', 'Melatonin', 'Turmeric', 'CoQ10', 'Eye Health',
    'Cranberry', 'Menopause Support', "Men\'s Multivitamin", "Women\'s Multivitamin",
    'Pregnancy', 'Meal Replacement', 'Weight Management', 'Liver Support',
    'Brain Omega-3', 'Aloe Vera', 'Echinacea', 'Manuka Honey', 'Milk Thistle',
    'Hair Supplement', 'L-Theanine', "Lion's Mane", 'Rhodiola',
}
SPECIFIC_LIMIT = 5  # max 5 per narrow category
BROAD_LIMIT = 14    # max 14 per broad category

# Sort: priority brand first, then by number of goals (more is better for coverage), then name length
classified.sort(key=lambda x: (not x['_priority'], -len(x['goals']), len(x['name'])))

from collections import defaultdict
cat_counts = defaultdict(int)
selected = []

for p in classified:
    cat = p['category']
    limit = BROAD_LIMIT if cat in BROAD_CATEGORIES else SPECIFIC_LIMIT
    if cat_counts[cat] < limit:
        cat_counts[cat] += 1
        selected.append(p)

print(f"After dedup by category: {len(selected)}")

# Ensure coverage of all goals — if a goal has <2 products, relax limit
goal_counts = defaultdict(int)
for p in selected:
    for g in p['goals']:
        goal_counts[g] += 1

ALL_GOALS = ['sleep', 'stress', 'energy', 'immune', 'gut', 'skin', 'sunburn',
             'hair', 'joint', 'heart', 'weight', 'kids', 'pregnancy', 'eye',
             'focus', 'menopause', 'uti', 'cold', 'mens', 'womens', 'blood_sugar', 'liver']

for g in ALL_GOALS:
    if goal_counts[g] < 3:
        # Add more products for this goal from non-selected
        already_names = {p['name'] for p in selected}
        for p in classified:
            if p['name'] in already_names:
                continue
            if g in p['goals']:
                selected.append(p)
                already_names.add(p['name'])
                goal_counts[g] += 1
                if goal_counts[g] >= 3:
                    break

print(f"After goal coverage boost: {len(selected)}")

# Final size check — cap at 450
if len(selected) > 450:
    # Score by: number of goals covered, priority brand, name length
    selected.sort(key=lambda x: (not x['_priority'], -len(x['goals']), len(x['name'])))
    selected = selected[:450]

print(f"Final product count: {len(selected)}")

# Coverage check
goal_counts2 = defaultdict(int)
for p in selected:
    for g in p['goals']:
        goal_counts2[g] += 1
for g in ALL_GOALS:
    print(f"  {g}: {goal_counts2[g]}")


# ─────────────────────────────────────────────────────────────
# OUTPUT
# ─────────────────────────────────────────────────────────────

def js_str(s):
    s = s or ''
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"

def js_arr(lst):
    return '[' + ','.join(js_str(x) for x in lst) + ']'

def js_obj(d):
    if not d:
        return '{}'
    parts = []
    for k, v in d.items():
        parts.append(k + ':' + js_str(v))
    return '{' + ','.join(parts) + '}'

lines = []
for p in selected:
    line = (
        '{name:' + js_str(p['name']) +
        ',category:' + js_str(p['category']) +
        ',primary:' + js_str(p['primary']) +
        ',goals:' + js_arr(p['goals']) +
        ',who:' + js_arr(p['who']) +
        ',warnings:' + js_obj(p['warnings']) +
        '}'
    )
    lines.append(line)

output = 'const PRODUCTS = [\n  ' + ',\n  '.join(lines) + '\n];'

with open('/home/user/healthneeds-recommender/products_new.js', 'w') as f:
    f.write(output)

print(f"\nWrote {len(lines)} products to products_new.js")
print(f"Output size: {len(output):,} bytes")
