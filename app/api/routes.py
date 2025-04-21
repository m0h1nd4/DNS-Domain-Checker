from flask import Blueprint, request, jsonify
from app import db
from app.models import Check
from app.services.dns_lookup import lookup

api_bp = Blueprint('api', __name__)

@api_bp.route('/parts', methods=['POST'])
def set_parts():
    data = request.get_json()
    # expect keys: must, should, can (lists)
    # currently unused, as frontend writes directly to JSON config
    return jsonify({'message': 'Parts received'}), 200

@api_bp.route('/tlds/import', methods=['POST'])
def import_tlds():
    data = request.get_json()
    # expect: list of tlds
    # currently unused, as frontend writes directly to JSON config
    return jsonify({'message': 'TLDs imported'}), 200

@api_bp.route('/check', methods=['POST'])
def run_check():
    data = request.get_json()
    parts = data.get('parts')
    tlds = data.get('tlds')
    results = []
    for p in parts['must'] + parts['should'] + parts['can']:
        for tld in tlds:
            domain_full = f"{p}.{tld}"
            status, ips = lookup(domain_full)
            ip_str = ','.join(ips) if ips else None
            record = Check(domain=p, tld=tld, status=status, ip=ip_str)
            db.session.add(record)
            results.append({
                'domain': p,
                'tld': tld,
                'status': status,
                'ip': ip_str
            })
    db.session.commit()
    return jsonify(results), 200

@api_bp.route('/results', methods=['GET'])
def get_results():
    recs = Check.query.order_by(Check.timestamp.desc()).all()
    return jsonify([{
        'domain': r.domain,
        'tld': r.tld,
        'status': r.status,
        'ip': r.ip,
        'timestamp': r.timestamp.isoformat()
    } for r in recs])
