import csv
import io
import os
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from pathlib import Path

from flask import Flask, Response, abort, flash, redirect, render_template, request, session, url_for


CATEGORIES = ('Hortifruti', 'Laticínios', 'Proteínas', 'Grãos', 'Outros')
UNITS = ('un', 'kg', 'g', 'L', 'ml')


def expiry_status(expiry, today=None):
    days = (date.fromisoformat(expiry) - (today or date.today())).days
    if days < 0:
        return 'expired', 'Vencido', days
    if days <= 3:
        return 'soon', 'Vence hoje' if days == 0 else f'Em {days} dias', days
    return 'fresh', 'No prazo', days


def validate_item(form):
    name = form.get('name', '').strip()
    category = form.get('category', '')
    unit = form.get('unit', '')
    try:
        quantity = float(form.get('quantity', '').replace(',', '.'))
        expiry = date.fromisoformat(form.get('expiry', ''))
    except (ValueError, TypeError):
        raise ValueError('Confira a quantidade e a data de validade.') from None
    if not 1 <= len(name) <= 80:
        raise ValueError('O nome precisa ter entre 1 e 80 caracteres.')
    if category not in CATEGORIES or unit not in UNITS:
        raise ValueError('Escolha uma categoria e unidade válidas.')
    if not 0 < quantity <= 10000:
        raise ValueError('A quantidade deve ser maior que zero e até 10.000.')
    return name, category, quantity, unit, expiry.isoformat()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(SECRET_KEY=os.environ.get('SECRET_KEY') or secrets.token_hex(32),
                      DATABASE=str(Path(app.instance_path) / 'prazo.sqlite'),
                      MAX_CONTENT_LENGTH=32_768, SESSION_COOKIE_SAMESITE='Lax')
    if test_config:
        app.config.update(test_config)
    Path(app.config['DATABASE']).parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect():
        conn = sqlite3.connect(app.config['DATABASE'])
        conn.row_factory = sqlite3.Row
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    with connect() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY, name TEXT NOT NULL, category TEXT NOT NULL,
            quantity REAL NOT NULL CHECK(quantity > 0), unit TEXT NOT NULL,
            expiry TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'active'
            CHECK(state IN ('active','consumed','discarded')), closed_at TEXT)''')

    @app.before_request
    def protect_forms():
        session.setdefault('csrf_token', secrets.token_hex(32))
        if request.method == 'POST':
            token = request.form.get('csrf_token', '')
            if not secrets.compare_digest(token, session['csrf_token']):
                abort(400, description='Formulário expirado. Atualize a página e tente novamente.')

    @app.after_request
    def security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self'; script-src 'self'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'"
        response.headers['Referrer-Policy'] = 'same-origin'
        return response

    @app.get('/')
    def index():
        q = request.args.get('q', '').strip()[:80]
        selected = request.args.get('status', 'all')
        category = request.args.get('category', '')
        with connect() as db:
            rows = [dict(row) for row in db.execute('SELECT * FROM items ORDER BY expiry, name')]
        active, history = [], []
        for row in rows:
            row['status'], row['label'], row['days'] = expiry_status(row['expiry'])
            row['display_date'] = date.fromisoformat(row['expiry']).strftime('%d/%m/%Y')
            if row['closed_at']:
                row['display_closed'] = datetime.fromisoformat(row['closed_at']).strftime('%d/%m/%Y')
            (active if row['state'] == 'active' else history).append(row)
        history.sort(key=lambda row: row['closed_at'], reverse=True)
        counts = {key: sum(row['status'] == key for row in active) for key in ('soon', 'expired', 'fresh')}
        visible = [row for row in active if (not q or q.casefold() in row['name'].casefold())
                   and (selected == 'all' or row['status'] == selected)
                   and (not category or row['category'] == category)]
        return render_template('index.html', items=visible, history=history[:8],
                               counts=counts, total=len(active), categories=CATEGORIES, units=UNITS,
                               q=q, selected=selected, category=category, today=date.today().isoformat())

    @app.post('/items')
    def add_item():
        try:
            values = validate_item(request.form)
        except ValueError as error:
            flash(str(error), 'error')
            return redirect(url_for('index'), code=303)
        with connect() as db:
            db.execute('INSERT INTO items(name,category,quantity,unit,expiry) VALUES(?,?,?,?,?)', values)
        flash('Alimento adicionado.', 'success')
        return redirect(url_for('index'), code=303)

    @app.post('/items/<int:item_id>/state')
    def change_state(item_id):
        state = request.form.get('state')
        if state not in ('consumed', 'discarded', 'active'):
            abort(400)
        with connect() as db:
            item = db.execute('SELECT state FROM items WHERE id=?', (item_id,)).fetchone()
            if item is None:
                abort(404)
            if (item['state'] == 'active') == (state == 'active'):
                abort(409)
            db.execute('UPDATE items SET state=?, closed_at=? WHERE id=?',
                       (state, None if state == 'active' else datetime.now().astimezone().isoformat(), item_id))
        flash('Registro atualizado. Você pode desfazer pelo histórico.', 'success')
        return redirect(url_for('index'), code=303)

    @app.post('/demo')
    def demo():
        with connect() as db:
            if db.execute('SELECT COUNT(*) FROM items').fetchone()[0]:
                flash('A demonstração só é carregada quando o estoque está vazio.', 'error')
            else:
                examples = [('Iogurte natural','Laticínios',4,'un',1),('Tomate cereja','Hortifruti',0.5,'kg',2),
                            ('Arroz integral','Grãos',1,'kg',90),('Leite','Laticínios',1,'L',-1),
                            ('Ovos','Proteínas',12,'un',10),('Banana','Hortifruti',6,'un',0)]
                db.executemany('INSERT INTO items(name,category,quantity,unit,expiry) VALUES(?,?,?,?,?)',
                               [(n,c,q,u,(date.today()+timedelta(days=d)).isoformat()) for n,c,q,u,d in examples])
                flash('Dados fictícios carregados para explorar a aplicação.', 'success')
        return redirect(url_for('index'), code=303)

    @app.get('/export.csv')
    def export():
        output = io.StringIO(newline='')
        writer = csv.writer(output, delimiter=';')
        writer.writerow(['Nome','Categoria','Quantidade','Unidade','Validade','Estado'])
        with connect() as db:
            for row in db.execute('SELECT name,category,quantity,unit,expiry,state FROM items ORDER BY expiry'):
                writer.writerow(["'"+value if isinstance(value,str) and value.lstrip().startswith(('=','+','-','@')) else value for value in row])
        return Response('\ufeff'+output.getvalue(), mimetype='text/csv',
                        headers={'Content-Disposition':'attachment; filename=prazo-estoque.csv'})

    @app.errorhandler(400)
    @app.errorhandler(404)
    @app.errorhandler(409)
    @app.errorhandler(413)
    def error_page(error):
        return render_template('error.html', error=error), error.code

    return app


if __name__ == '__main__':
    create_app().run(host='127.0.0.1', port=5000)
