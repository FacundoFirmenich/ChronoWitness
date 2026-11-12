"""Replay the public FD7 witness and its finite-window counterfactual."""

import argparse
from fractions import Fraction
import json

from tools.render_witness_3d import PAIR, state_path, trace


def evaluate(arm=None, phase=None):
    reference = trace()
    period = len(reference['arms']['A']['word'])
    if arm is None and phase is None:
        edit = None
    elif arm in reference['arms'] and type(phase) is int and 0 <= phase < period:
        original = reference['arms'][arm]['word'][phase]
        edit = {'arm': arm, 'phase': phase, 'from': original, 'to': str(1 - int(original))}
    else:
        raise ValueError('The edit requires an arm and a zero-based phase within the cycle.')

    arms = {}
    for name, record in reference['arms'].items():
        word = record['word']
        if edit and name == arm:
            word = word[:phase] + edit['to'] + word[phase + 1:]
        path = state_path(word, reference['transition'])
        visits = path[:-1].count(3)
        arms[name] = {'word': word, 'path': path, 'visits': visits, 'closed': path[-1] == path[0]}
    contrast = Fraction(arms['A']['visits'] - arms['B']['visits'], period)
    return {
        'schema': 'chronowitness-fd7-demo/1',
        'scope': 'finite_window_from_state_zero' if edit else 'certified_periodic_pair',
        'certificate_applicable': edit is None,
        'edit': edit,
        'period': period,
        'transition': reference['transition'],
        'arms': arms,
        'contrast': str(contrast),
        'sources': {'input_pair': PAIR, 'witness_certificate': reference['source']},
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Replay the FD7 case / Reproducir el caso FD7')
    parser.add_argument('--arm', choices=('A', 'B'), help='Arm to edit / Brazo que se edita')
    parser.add_argument('--phase', type=int, help='Zero-based phase / Fase desde cero')
    args = parser.parse_args()
    try:
        result = evaluate(args.arm, args.phase)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2, ensure_ascii=False))
