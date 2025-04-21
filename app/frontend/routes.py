from flask import Blueprint, render_template, request, redirect, url_for, flash
import json
from itertools import permutations as it_permutations

from app.utils.config_manager import load_config, save_config
from app.utils.domain_config_manager import load_domain_config, save_domain_config
from app.services.dns_lookup import lookup
from app import db
from app.models import Check

frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/', methods=['GET', 'POST'])
def parts():
    cfg = load_config()
    if request.method == 'POST':
        must_raw = request.form.get('must_parts', '')
        should_raw = request.form.get('should_parts', '')
        can_raw = request.form.get('can_parts', '')
        cfg['parts']['must'] = [p.strip() for p in must_raw.replace(',', '\n').splitlines() if p.strip()]
        cfg['parts']['should'] = [p.strip() for p in should_raw.replace(',', '\n').splitlines() if p.strip()]
        cfg['parts']['can'] = [p.strip() for p in can_raw.replace(',', '\n').splitlines() if p.strip()]
        save_config(cfg)
        return redirect(url_for('frontend.combinations'))
    return render_template('parts.html', parts=cfg['parts'])

@frontend_bp.route('/combinations', methods=['GET', 'POST'])
def combinations():
    cfg = load_config()
    domain_cfg = load_domain_config()

    must = cfg['parts'].get('must', [])
    if not must:
        flash('Bitte mindestens einen "Muss"-Begriff eingeben, bevor Kombinationen erstellt werden.', 'danger')
        return redirect(url_for('frontend.parts'))

    should = cfg['parts'].get('should', [])
    can = cfg['parts'].get('can', [])

    # 1) Basis: alle Permutationen der Muss-Begriffe mit None, '-', '_'
    perms = list(it_permutations(must))
    base_variants = []
    for perm in perms:
        perm_l = [p.lower() for p in perm]
        pure = ''.join(perm_l)
        base_variants.append(pure)
        base_variants.append('-'.join(perm_l))
        base_variants.append('_'.join(perm_l))
    base_variants = list(dict.fromkeys(base_variants))

    # 2) Sollte-Varianten: nur in Kombination mit Muss
    should_variants = []
    for perm in perms:
        perm_l = [p.lower() for p in perm]
        pure = ''.join(perm_l)
        for term in should:
            term_l = term.lower()
            # Prefix
            should_variants.append(term_l + pure)
            should_variants.append(term_l + '-' + pure)
            should_variants.append(term_l + '_' + pure)
            # Suffix
            should_variants.append(pure + term_l)
            should_variants.append(pure + '-' + term_l)
            should_variants.append(pure + '_' + term_l)
            # Insertion zwischen Muss-Begriffen
            for i in range(1, len(perm_l)):
                part1 = ''.join(perm_l[:i])
                part2 = ''.join(perm_l[i:])
                should_variants.append(part1 + term_l + part2)
                should_variants.append(part1 + '-' + term_l + '-' + part2)
                should_variants.append(part1 + '_' + term_l + '_' + part2)
    should_variants = list(dict.fromkeys(should_variants))

    # 3) Kann-Varianten: ausschließlich als Suffix
    combined_pre_can = base_variants + should_variants
    can_variants = []
    for combo in combined_pre_can:
        for term in can:
            term_l = term.lower()
            can_variants.append(combo + term_l)
            can_variants.append(combo + '-' + term_l)
            can_variants.append(combo + '_' + term_l)
    can_variants = list(dict.fromkeys(can_variants))

    # Gesamtliste aller Kombinationen
    combos_full = list(dict.fromkeys(base_variants + should_variants + can_variants))
    total = len(combos_full)

    # Speichern für Auswahl/Ergebnis
    domain_cfg['combinations'] = combos_full

    if request.method == 'POST':
        max_combinations = int(request.form.get('max_combinations', domain_cfg.get('max_combinations', total)))
        force_all = 'force_all' in request.form
        selected = request.form.getlist('combinations')
        action = request.form.get('action')

        domain_cfg['max_combinations'] = max_combinations
        domain_cfg['force_all'] = force_all
        domain_cfg['selected_combinations'] = selected
        save_domain_config(domain_cfg)

        if action == 'next':
            return redirect(url_for('frontend.tlds_import'))
    else:
        max_combinations = domain_cfg.get('max_combinations', total)
        force_all = domain_cfg.get('force_all', False)
        selected = domain_cfg.get('selected_combinations', [])

    # Auswahl, welche angezeigt werden
    if total > max_combinations and not force_all:
        display_combos = combos_full[:max_combinations]
    else:
        display_combos = combos_full

    # Heatmap-Klasse
    if total <= max_combinations:
        heatmap = 'text-success'
    elif total <= max_combinations * 2:
        heatmap = 'text-warning'
    else:
        heatmap = 'text-danger'

    return render_template(
        'combinations.html',
        combinations=display_combos,
        total=total,
        max_combinations=max_combinations,
        force_all=force_all,
        heatmap=heatmap,
        selected=selected
    )

@frontend_bp.route('/tlds/import', methods=['GET', 'POST'])
def tlds_import():
    cfg = load_config()
    if request.method == 'POST':
        raw = request.form.get('tlds_raw', '')
        try:
            tlds = json.loads(raw)
            if not isinstance(tlds, list):
                raise ValueError
        except:
            tlds = [t.strip().lstrip('.') for t in raw.replace('\n', ',').split(',') if t.strip()]
        cfg['tlds'] = tlds
        save_config(cfg)
        return redirect(url_for('frontend.tlds_select'))
    raw_display = ','.join(cfg.get('tlds', []))
    return render_template('tlds_import.html', tlds_raw=raw_display)

@frontend_bp.route('/tlds/select', methods=['GET', 'POST'])
def tlds_select():
    cfg = load_config()
    available_tlds = cfg.get('tlds', [])
    if request.method == 'POST':
        selected = request.form.getlist('tlds')
        cfg['selected_tlds'] = selected
        save_config(cfg)
        return redirect(url_for('frontend.results'))
    return render_template('tlds_select.html', tlds=available_tlds, selected=cfg.get('selected_tlds', []))

@frontend_bp.route('/results')
def results():
    cfg = load_config()
    domain_cfg = load_domain_config()

    selected_combos = domain_cfg.get('selected_combinations', [])
    selected_tlds = cfg.get('selected_tlds', [])
    results = []

    for base in selected_combos:
        for tld in selected_tlds:
            domain_full = f"{base}.{tld}"
            status, ips = lookup(domain_full)
            ip_str = ', '.join(ips) if ips else None
            record = Check(domain=base, tld=tld, status=status, ip=ip_str)
            db.session.add(record)
            results.append({
                'domain': base,
                'tld': tld,
                'status': status,
                'ip': ip_str
            })

    db.session.commit()
    return render_template('results.html', results=results)
