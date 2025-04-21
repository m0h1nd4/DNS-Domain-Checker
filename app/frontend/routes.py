from flask import Blueprint, render_template, request, redirect, url_for
import json
from itertools import chain, combinations as it_combinations

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
    should = cfg['parts'].get('should', [])
    can = cfg['parts'].get('can', [])

    # Erzeuge alle Teilmengen von should+can
    items = should + can
    all_subsets = chain.from_iterable(it_combinations(items, n) for n in range(len(items)+1))

    combos_full = []
    for subset in all_subsets:
        parts = must + list(subset)
        if not parts:
            continue
        # Varianten ohne und mit Separatoren
        combos_full.append(''.join(parts))
        combos_full.append('-'.join(parts))
        combos_full.append('_'.join(parts))
    # Duplikate entfernen und Reihenfolge bewahren
    combos_full = list(dict.fromkeys(combos_full))
    total = len(combos_full)

    # Vollständige Liste zwischenspeichern
    domain_cfg['combinations'] = combos_full

    if request.method == 'POST':
        max_combinations = int(request.form.get('max_combinations', domain_cfg.get('max_combinations', 20)))
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
        max_combinations = domain_cfg.get('max_combinations', 20)
        force_all = domain_cfg.get('force_all', False)
        selected = domain_cfg.get('selected_combinations', [])

    # Bestimmen, welche Kombinationen angezeigt werden
    if total > max_combinations and not force_all:
        display_combos = combos_full[:max_combinations]
    else:
        display_combos = combos_full

    # Heatmap-Klasse bestimmen
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
