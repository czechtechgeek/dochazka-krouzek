import os
import io
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import date, datetime
from flask import Flask, render_template, request, redirect, url_for, flash, Response, jsonify, send_file
from models import db, Group, Child, Attendance

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLITE_URL', 'sqlite:///dochazka.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Proxy fix for standard headers (X-Forwarded-For, X-Forwarded-Proto)
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

# HA ingress: rewrite absolute paths in HTML to include ingress prefix
import re
INGRESS_BASE = os.environ.get('INGRESS_BASE', '')

@app.after_request
def fix_ingress_paths(response):
    pfx = request.headers.get('X-Ingress-Path') or \
          request.headers.get('X-Forwarded-Prefix') or \
          INGRESS_BASE
    if not pfx:
        return response
    rstrip = pfx.rstrip('/')
    # Fix redirect Location header (302/303)
    loc = response.headers.get('Location', '')
    if loc.startswith('/') and not loc.startswith(f'{rstrip}/'):
        response.headers['Location'] = f'{rstrip}{loc}'
    # Fix HTML content (href/action)
    if response.content_type and 'text/html' in response.content_type:
        html = response.get_data(as_text=True)
        html = html.replace('href="/', f'href="{rstrip}/')
        html = html.replace('action="/', f'action="{rstrip}/')
        response.set_data(html)
    return response

PORT = int(os.environ.get('PORT', 9120))

db.init_app(app)

@app.context_processor
def inject_now():
    return {'now': datetime.now}

with app.app_context():
    db.create_all()
    # Migrate: add subgroup column if missing
    try:
        import sqlalchemy as sa
        insp = sa.inspect(db.engine)
        cols = [c['name'] for c in insp.get_columns('children')]
        if 'subgroup' not in cols:
            with db.engine.connect() as conn:
                conn.execute(sa.text('ALTER TABLE children ADD COLUMN subgroup VARCHAR(100)'))
                conn.commit()
        if 'note' not in cols:
            with db.engine.connect() as conn:
                conn.execute(sa.text('ALTER TABLE children ADD COLUMN note VARCHAR(500)'))
                conn.commit()
    except Exception:
        pass  # table might not exist yet

# ── PWA ──────────────────────────────────────────

@app.route('/manifest.json')
def manifest():
    return {
        "name": "Docházka - kroužek",
        "short_name": "Docházka",
        "description": "Správa docházky v kroužku",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#f8fafc",
        "theme_color": "#2563eb",
        "icons": [{
            "src": "/static/icon-192.png",
            "sizes": "192x192",
            "type": "image/png"
        }, {
            "src": "/static/icon-512.png",
            "sizes": "512x512",
            "type": "image/png"
        }]
    }

@app.route('/service-worker.js')
def sw():
    return app.send_static_file('service-worker.js')

# ── HELPERS ──────────────────────────────────────

def today():
    return date.today()

def parse_date(datestr):
    if not datestr:
        return today()
    try:
        return datetime.strptime(datestr, '%Y-%m-%d').date()
    except ValueError:
        return today()

# ── ROUTES ───────────────────────────────────────

@app.route('/')
def index():
    groups = Group.query.order_by(Group.sort_order).all()
    d = today()
    summary = {}
    for g in groups:
        present = Attendance.query.filter_by(date=d, group_id=g.id, status='present').count()
        total = len(g.children)
        attended = Attendance.query.filter_by(date=d, group_id=g.id).count()
        summary[g.id] = {'present': present, 'total': total, 'attended': attended}
    return render_template('index.html', groups=groups, today=d, summary=summary)

@app.route('/manage', methods=['GET', 'POST'])
def manage():
    if request.method == 'POST':
        # Batch add children
        names_raw = request.form.get('names', '')
        group_id = request.form.get('group_id')
        default_subgroup = request.form.get('subgroup', '')
        if group_id:
            group = Group.query.get(int(group_id))
            if group:
                names = [n.strip() for n in names_raw.split('\n') if n.strip()]
                for entry in names:
                    # Parse "Jméno | Podskupina" format
                    if ' | ' in entry:
                        parts = entry.split(' | ', 1)
                        name = parts[0].strip()
                        subgroup = parts[1].strip()
                    else:
                        name = entry
                        subgroup = default_subgroup or None
                    child = Child(name=name, group_id=group.id, subgroup=subgroup)
                    db.session.add(child)
                db.session.commit()
                flash(f'Přidáno {len(names)} dětí do skupiny "{group.name}"', 'success')
        return redirect(url_for('manage'))
    
    groups = Group.query.order_by(Group.sort_order).all()
    return render_template('manage.html', groups=groups)

@app.route('/manage/child/delete/<int:child_id>', methods=['POST'])
def delete_child(child_id):
    child = Child.query.get_or_404(child_id)
    Attendance.query.filter_by(child_id=child_id).delete()
    db.session.delete(child)
    db.session.commit()
    flash(f'Dítě odstraněno', 'success')
    return redirect(url_for('manage'))

@app.route('/manage/child/note/<int:child_id>', methods=['POST'])
def child_note(child_id):
    child = Child.query.get_or_404(child_id)
    note = request.form.get('note', '').strip()
    child.note = note if note else None
    db.session.commit()
    return redirect(url_for('manage'))

@app.route('/group/add', methods=['POST'])
def add_group():
    name = request.form.get('name')
    start_time = request.form.get('start_time', '00:00')
    if name:
        max_order = db.session.query(db.func.max(Group.sort_order)).scalar() or 0
        g = Group(name=name, start_time=start_time, sort_order=max_order + 1)
        db.session.add(g)
        db.session.commit()
        flash(f'Skupina "{name}" vytvořena', 'success')
    return redirect(url_for('manage'))

@app.route('/group/delete/<int:group_id>', methods=['POST'])
def delete_group(group_id):
    group = Group.query.get_or_404(group_id)
    Attendance.query.filter_by(group_id=group_id).delete()
    Child.query.filter_by(group_id=group_id).delete()
    db.session.delete(group)
    db.session.commit()
    flash(f'Skupina smazána', 'success')
    return redirect(url_for('manage'))

@app.route('/attendance/<int:group_id>', methods=['GET', 'POST'])
def attendance(group_id):
    group = Group.query.get_or_404(group_id)
    datestr = request.args.get('date', '')
    d = parse_date(datestr)

    if request.method == 'POST':
        changes = 0
        for child in group.children:
            status = request.form.get(f'child_{child.id}')
            if status in ('present', 'absent', 'excused'):
                existing = Attendance.query.filter_by(child_id=child.id, date=d).first()
                if existing:
                    if existing.status != status:
                        existing.status = status
                        changes += 1
                else:
                    att = Attendance(child_id=child.id, date=d, status=status, group_id=group_id)
                    db.session.add(att)
                    changes += 1
        db.session.commit()
        if changes:
            flash(f'Uloženo {changes} změn', 'success')
        return redirect(url_for('attendance', group_id=group_id, date=datestr if datestr else ''))

    children = group.children
    records = {}
    for att in Attendance.query.filter_by(date=d, group_id=group_id).all():
        records[att.child_id] = att.status

    return render_template('attendance.html', group=group, children=children,
                           records=records, selected_date=d, datestr=datestr)

@app.route('/attendance/<int:group_id>/bulk', methods=['POST'])
def attendance_bulk(group_id):
    group = Group.query.get_or_404(group_id)
    datestr = request.args.get('date', '')
    d = parse_date(datestr)
    status = request.form.get('status', 'excused')

    changes = 0
    for child in group.children:
        existing = Attendance.query.filter_by(child_id=child.id, date=d).first()
        if existing:
            if existing.status != status:
                existing.status = status
                changes += 1
        else:
            att = Attendance(child_id=child.id, date=d, status=status, group_id=group_id)
            db.session.add(att)
            changes += 1
    db.session.commit()

    labels = {'present': 'Přítomen', 'excused': 'Omluven', 'absent': 'Nepřítomen'}
    if changes:
        flash(f'Hromadně označeno {changes} dětí jako {labels.get(status, status)}', 'success')
    return redirect(url_for('attendance', group_id=group_id, date=datestr if datestr else ''))

@app.route('/export/<int:group_id>')
def export(group_id):
    group = Group.query.get_or_404(group_id)
    datestr = request.args.get('date', '')
    d = parse_date(datestr)
    fmt = request.args.get('format', 'html')

    children = group.children
    records = {}
    for att in Attendance.query.filter_by(date=d, group_id=group_id).all():
        records[att.child_id] = att.status

    if fmt == 'xml':
        return export_xml(group, children, records, d)
    else:
        return render_template('export.html', group=group, children=children,
                               records=records, date=d)

def export_xml(group, children, records, date_obj):
    root = ET.Element('dochazka')
    ET.SubElement(root, 'datum').text = date_obj.isoformat()
    ET.SubElement(root, 'skupina').text = group.name
    ET.SubElement(root, 'cas').text = group.start_time

    deti = ET.SubElement(root, 'deti')
    present = absent = excused = 0
    for child in children:
        c = ET.SubElement(deti, 'dite')
        ET.SubElement(c, 'jmeno').text = child.name
        status = records.get(child.id, 'nevyplneno')
        ET.SubElement(c, 'stav').text = status
        if status == 'present': present += 1
        elif status == 'absent': absent += 1
        elif status == 'excused': excused += 1

    souhrn = ET.SubElement(root, 'souhrn')
    ET.SubElement(souhrn, 'pritomno').text = str(present)
    ET.SubElement(souhrn, 'omluveno').text = str(excused)
    ET.SubElement(souhrn, 'nepritomno').text = str(absent)
    ET.SubElement(souhrn, 'celkem').text = str(len(children))

    rough = ET.tostring(root, encoding='unicode')
    dom = minidom.parseString(rough)
    xml_str = dom.toprettyxml(indent='  ', encoding='utf-8')
    return Response(xml_str, mimetype='application/xml',
                    headers={'Content-Disposition': f'attachment; filename=dochazka_{date_obj.isoformat()}.xml'})

# ── JSON API (pro rychlé značení z mobilu) ──────

@app.route('/api/toggle/<int:child_id>', methods=['POST'])
def api_toggle(child_id):
    data = request.get_json(force=True, silent=True) or {}
    datestr = data.get('date', '')
    d = parse_date(datestr)
    status = data.get('status', 'present')

    child = Child.query.get_or_404(child_id)
    existing = Attendance.query.filter_by(child_id=child_id, date=d).first()
    if existing:
        if existing.status == status:
            db.session.delete(existing)
            db.session.commit()
            return jsonify({'status': 'deleted', 'child_id': child_id})
        existing.status = status
    else:
        att = Attendance(child_id=child_id, date=d, status=status, group_id=child.group_id)
        db.session.add(att)
    db.session.commit()
    return jsonify({'status': status, 'child_id': child_id})

@app.route('/api/attendance/<int:group_id>')
def api_get_attendance(group_id):
    datestr = request.args.get('date', '')
    d = parse_date(datestr)
    group = Group.query.get_or_404(group_id)
    records = {}
    for att in Attendance.query.filter_by(date=d, group_id=group_id).all():
        records[att.child_id] = att.status
    return jsonify({
        'date': d.isoformat(),
        'group_id': group_id,
        'children': [{'id': c.id, 'name': c.name, 'status': records.get(c.id, 'none')}
                      for c in group.children]
    })

# ── SUMMARY ──────────────────────────────────────

@app.route('/summary')
def summary():
    groups = Group.query.order_by(Group.sort_order).all()
    return render_template('summary.html', groups=groups, today=today())

@app.route('/summary/data')
def summary_data():
    date_from = request.args.get('from', '')
    date_to = request.args.get('to', '')
    group_id = request.args.get('group_id', type=int)

    q = Attendance.query
    if date_from:
        q = q.filter(Attendance.date >= parse_date(date_from))
    if date_to:
        q = q.filter(Attendance.date <= parse_date(date_to))
    if group_id:
        q = q.filter(Attendance.group_id == group_id)

    all_records = q.order_by(Attendance.date).all()

    # Group by date+group
    data = {}
    for r in all_records:
        key = (r.date.isoformat(), r.group_id)
        if key not in data:
            g = Group.query.get(r.group_id)
            data[key] = {
                'date': r.date.isoformat(),
                'group_id': r.group_id,
                'group_name': g.name if g else '?',
                'present': 0, 'absent': 0, 'excused': 0, 'total': 0
            }
        data[key][r.status] += 1
        data[key]['total'] += 1

    return jsonify(sorted(data.values(), key=lambda x: x['date']))

# ── INDIVIDUAL STATS ──────────────────────────────

@app.route('/stats')
def stats_overview():
    groups = Group.query.order_by(Group.sort_order).all()
    return render_template('stats.html', groups=groups, today=today())

@app.route('/stats/<int:child_id>')
def stats_detail(child_id):
    child = Child.query.get_or_404(child_id)
    records = Attendance.query.filter_by(child_id=child_id).order_by(Attendance.date.desc()).all()
    present = sum(1 for r in records if r.status == 'present')
    excused = sum(1 for r in records if r.status == 'excused')
    absent = sum(1 for r in records if r.status == 'absent')
    total = len(records)
    pct = round(present / total * 100) if total else 0
    return render_template('stats_detail.html', child=child, records=records,
                           present=present, excused=excused, absent=absent,
                           total=total, pct=pct)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)