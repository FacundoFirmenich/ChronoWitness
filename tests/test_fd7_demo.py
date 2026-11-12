from fractions import Fraction
import unittest

from streamlit.testing.v1 import AppTest

from tools.fd7_demo import evaluate


class FD7DemoTests(unittest.TestCase):
    def test_reference_and_documented_edit(self):
        baseline = evaluate()
        edited = evaluate('A', 1)
        self.assertEqual(baseline['contrast'], '1/24')
        self.assertTrue(baseline['certificate_applicable'])
        self.assertEqual(edited['edit'], {'arm': 'A', 'phase': 1, 'from': '0', 'to': '1'})
        self.assertEqual(edited['contrast'], '0')
        self.assertFalse(edited['certificate_applicable'])

    def test_all_edits_keep_only_the_declared_symbol_change(self):
        baseline = evaluate()
        for arm in ('A', 'B'):
            for phase in range(24):
                with self.subTest(arm=arm, phase=phase):
                    result = evaluate(arm, phase)
                    for name in ('A', 'B'):
                        old = baseline['arms'][name]['word']
                        new = result['arms'][name]['word']
                        changes = [i for i, pair in enumerate(zip(old, new, strict=True)) if pair[0] != pair[1]]
                        self.assertEqual(changes, [phase] if name == arm else [])
                    visits = result['arms']['A']['path'][:-1].count(3) - result['arms']['B']['path'][:-1].count(3)
                    self.assertEqual(Fraction(result['contrast']), Fraction(visits, 24))

    def test_bilingual_interface(self):
        app = AppTest.from_file('streamlit_app.py', default_timeout=20).run()
        self.assertFalse(app.exception)
        self.assertEqual([m.value for m in app.metric], ['3/24', '2/24', '1/24'])
        app.radio(key='language').set_value('Castellano').run()
        app.radio(key='mode').set_value('Invertir un símbolo').run()
        self.assertFalse(app.exception)
        self.assertEqual([m.value for m in app.metric], ['2/24', '2/24', '0'])
        self.assertEqual(app.title[0].value, 'FD7 · Un ciclo, dos trayectorias')
