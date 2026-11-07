"""Recalculate selected PRC v1.16 archive statistics, not source-level experiments.

This script verifies the *archived JSON results*, not the underlying MMah
font download or the original experimental runs. Usage:
    python tools/verify_prc_archive.py /path/to/extracted/results
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import statistics
from pathlib import Path


def summarize(results: Path, output: Path) -> dict:
    names = ('repo_module_results.json', 'sector_generalisation.json',
             'sector_experiment.json')
    raw = {name: (results / name).read_bytes() for name in names}
    main, sectors, reps = [json.loads(raw[name]) for name in names]
    assert len(main) == 120, 'Expected 120 PRC construction candidates'
    assert len(sectors) == 53, 'Expected 53 generalisation candidates'
    assert len(reps) == 6, 'Expected 6 representatives'
    assert len({(r['a'], r['b']) for r in main}) == len(main)
    assert len({r['char'] for r in sectors}) == len(sectors)
    assert all(r['m1']['score']['ok'] for r in sectors)
    assert all(r['m1']['score']['retention'] >= .90 for r in sectors)
    assert all(r['m1']['score']['growth'] <= 1.30 for r in sectors)
    mean_centre_gain = statistics.mean(r['centre_only'] - r['box'] for r in main)
    median_centre_gain = statistics.median(r['centre_only'] - r['box'] for r in main)
    mean_extremity_gain = statistics.mean(r['with_rules'] - r['centre_only'] for r in main)
    deltas = [r['m1']['score']['sym'] - r['base']['sym'] for r in sectors]
    summary = {
        'scope': 'Archived results verification only; not source rerun or human study',
        'input_sha256': {n: hashlib.sha256(raw[n]).hexdigest() for n in names},
        'construction_n': len(main),
        'centre_gain_mean': mean_centre_gain,
        'centre_gain_median': median_centre_gain,
        'extremity_gain_mean': mean_extremity_gain,
        'sector_n': len(sectors),
        'sector_improved_n': sum(x > 0 for x in deltas),
        'sector_delta_median': statistics.median(deltas),
        'sector_delta_mean': statistics.mean(deltas),
        'sector_baseline_median': statistics.median(r['base']['sym'] for r in sectors),
        'sector_edited_median': statistics.median(r['m1']['score']['sym'] for r in sectors),
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / 'prc-archive-summary.json').write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    with (output / 'prc-centre-extremity-120.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['source', 'target', 'box_sym', 'centre_sym', 'rules_sym',
                         'final_sym', 'retention', 'meanings_not_tested'])
        for r in sorted(main, key=lambda r: (r['a'], r['b'])):
            writer.writerow([r['a'], r['b'], r['box'], r['centre_only'],
                             r['with_rules'], r['final'], r['retention'], True])
    with (output / 'prc-sector-generalisation-53.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['source', 'target', 'base_sym', 'edited_sym', 'gain',
                         'retention', 'growth', 'constraints_pass'])
        for r in sorted(sectors, key=lambda r: r['char']):
            b, e = r['base'], r['m1']['score']
            writer.writerow([r['char'], r['partner'], b['sym'], e['sym'],
                             e['sym'] - b['sym'], e['retention'], e['growth'], e['ok']])
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('results', type=Path)
    parser.add_argument('--out', type=Path, default=Path('data/prc/archive-v1.16'))
    args = parser.parse_args()
    print(json.dumps(summarize(args.results, args.out), indent=2))


if __name__ == '__main__':
    main()