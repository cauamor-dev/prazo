import csv
import io
import tempfile
import unittest
from datetime import date
from pathlib import Path

from app import create_app, expiry_status, validate_item


class PrazoTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.temp.name) / 'test.sqlite')
        self.app = create_app({'TESTING': True, 'DATABASE': self.path, 'SECRET_KEY': 'test-only'})
        self.client = self.app.test_client()
        self.client.get('/')
        with self.client.session_transaction() as session:
            self.token = session['csrf_token']

    def tearDown(self):
        self.temp.cleanup()

    def post(self, url, **data):
        return self.client.post(url, data={'csrf_token': self.token, **data}, follow_redirects=True)

    def add(self, name='Arroz', expiry='2099-01-01'):
        return self.post('/items', name=name, category='Grãos', quantity='2', unit='kg', expiry=expiry)

    def test_expiry_boundaries(self):
        today = date(2026, 10, 4)
        for expiry, expected in [('2026-10-03','expired'),('2026-10-04','soon'),('2026-10-07','soon'),('2026-10-08','fresh')]:
            self.assertEqual(expiry_status(expiry, today)[0], expected)

    def test_invalid_quantities(self):
        for value in ['0', '-1', 'nan', 'inf', '10001', 'abc']:
            with self.assertRaises(ValueError):
                validate_item({'name':'Arroz','category':'Grãos','unit':'kg','quantity':value,'expiry':'2026-10-04'})

    def test_invalid_date_and_category(self):
        for update in [{'expiry':'2026-02-30'},{'category':'x'},{'name':' '},{'unit':'x'}]:
            with self.assertRaises(ValueError):
                validate_item({'name':'Arroz','category':'Grãos','unit':'kg','quantity':'1','expiry':'2026-10-04',**update})

    def test_add_filter_and_persist(self):
        self.add()
        self.add('Leite','2020-01-01')
        response = self.client.get('/?q=Arroz&status=fresh')
        self.assertIn(b'Arroz', response.data)
        self.assertNotIn(b'<strong>Leite</strong>', response.data)
        other = create_app({'TESTING':True,'DATABASE':self.path,'SECRET_KEY':'test-only'}).test_client()
        self.assertIn(b'Arroz', other.get('/').data)

    def test_close_restore_and_conflicts(self):
        self.add()
        self.assertIn(b'Consumido', self.post('/items/1/state', state='consumed').data)
        self.assertEqual(self.post('/items/1/state', state='discarded').status_code,409)
        self.post('/items/1/state', state='active')
        self.assertIn(b'<strong>Arroz</strong>', self.client.get('/').data)
        self.assertEqual(self.post('/items/99/state', state='consumed').status_code,404)
        self.assertEqual(self.post('/items/1/state', state='invalid').status_code,400)

    def test_csrf_rejected(self):
        self.assertEqual(self.client.post('/items', data={}).status_code,400)

    def test_html_is_escaped(self):
        self.add('<script>alert(1)</script>')
        html = self.client.get('/').data
        self.assertNotIn(b'<script>alert(1)</script>',html)
        self.assertIn(b'&lt;script&gt;', html)

    def test_export_neutralizes_formulas(self):
        self.add('=1+1')
        response=self.client.get('/export.csv')
        rows=list(csv.reader(io.StringIO(response.data.decode('utf-8-sig')),delimiter=';'))
        self.assertEqual(rows[1][0],"'=1+1")
        self.assertEqual(response.headers['Content-Disposition'],'attachment; filename=prazo-estoque.csv')

    def test_demo_does_not_duplicate(self):
        self.post('/demo')
        self.post('/demo')
        rows=list(csv.reader(io.StringIO(self.client.get('/export.csv').data.decode('utf-8-sig')),delimiter=';'))
        self.assertEqual(len(rows),7)


if __name__ == '__main__':
    unittest.main()
