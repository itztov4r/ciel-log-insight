"""Summarize standard Apache Common / Combined access logs locally."""
import argparse
import ipaddress
import json
import re
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path
from report_theme import page, table, bars

LINE = re.compile(r'^(\S+) \S+ \S+ \[([^\]]+)\] "([^"\r\n]*)" ([1-5]\d{2}) (\d+|-)(?: "[^"\r\n]*" "[^"\r\n]*")?$')
MONTHS = {name: i for i, name in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(), 1)}


def parse_line(line):
    match = LINE.fullmatch(line.strip())
    if not match:
        raise ValueError('Format Common/Combined non reconnu')
    address, date, request, status, size = match.groups()
    ip = ipaddress.ip_address(address)
    parts = request.split()
    if len(parts) != 3 or not parts[0].isalpha() or not parts[2].startswith('HTTP/'):
        raise ValueError('Requête HTTP non reconnue')
    stamp = re.fullmatch(r'(\d{2})/(\w{3})/(\d{4}):(\d{2}):(\d{2}):(\d{2}) ([+-])(\d{2})(\d{2})', date)
    if not stamp:
        raise ValueError('Horodatage invalide')
    day, month, year, hour, minute, second, sign, oh, om = stamp.groups()
    if month not in MONTHS or int(oh) > 23 or int(om) > 59:
        raise ValueError('Horodatage invalide')
    offset = timedelta(hours=int(oh), minutes=int(om)) * (1 if sign == '+' else -1)
    dt = datetime(int(year), MONTHS[month], int(day), int(hour), int(minute), int(second), tzinfo=timezone(offset))
    # Remove query strings from the report and aggregate addresses by subnet.
    path = parts[1].split('?', 1)[0].split('#', 1)[0]
    network = str(ipaddress.ip_network(f'{ip}/{24 if ip.version == 4 else 48}', strict=False))
    return {'hour': dt.astimezone(timezone.utc).strftime('%Y-%m-%d %H:00 UTC'), 'path': path,
            'status': int(status), 'bytes': 0 if size == '-' else int(size), 'network': network}


def analyze(lines):
    codes, paths, hours, networks = Counter(), Counter(), Counter(), Counter()
    total = invalid = count = errors = size = 0
    invalid_examples = []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        total += 1
        try:
            event = parse_line(line)
        except ValueError as error:
            invalid += 1
            if len(invalid_examples) < 10:
                invalid_examples.append({'line': number, 'reason': str(error)})
            continue
        count += 1
        errors += event['status'] >= 400
        size += event['bytes']
        codes[str(event['status'])] += 1
        paths[event['path']] += 1
        hours[event['hour']] += 1
        networks[event['network']] += 1
    return {'input_lines': total, 'requests': count, 'invalid_lines': invalid,
            'http_errors': errors, 'error_rate': round(100 * errors / count, 2) if count else 0,
            'bytes': size, 'status_codes': dict(sorted(codes.items())),
            'top_paths': paths.most_common(10), 'activity_utc': dict(sorted(hours.items())),
            'top_networks': networks.most_common(10), 'invalid_examples': invalid_examples}


def render_html(report):
    body = '<div class="grid"><section class="panel"><h2>Réponses HTTP</h2>' + bars(report['status_codes'].items()) + '</section>'
    body += '<section class="panel"><h2>Chemins les plus consultés</h2>' + table(['Chemin sans paramètres', 'Requêtes'], report['top_paths']) + '</section></div>'
    body += '<section class="panel"><h2>Activité par heure · UTC</h2>' + table(['Heure', 'Requêtes'], report['activity_utc'].items()) + '</section>'
    body += '<div class="grid"><section class="panel"><h2>Réseaux sources · agrégés</h2>' + table(['Sous-réseau', 'Requêtes'], report['top_networks']) + '<p class="note">IPv4 agrégées en /24, IPv6 en /48. Les paramètres des URLs sont retirés ; les chemins restent présents.</p></section>'
    body += '<section class="panel"><h2>Qualité des données</h2>' + table(['Ligne', 'Motif'], ((x['line'], x['reason']) for x in report['invalid_examples'])) + f'<p class="note">{report["invalid_lines"]} lignes ignorées ; 10 motifs affichés au maximum. {report["bytes"]} octets déclarés par les lignes reconnues.</p></section></div>'
    body += '<p class="note">Les erreurs HTTP désignent les réponses 4xx et 5xx. Ces statistiques ne prouvent ni panne ni attaque. Les lignes non reconnues sont comptabilisées séparément.</p>'
    return page('Les logs deviennent lisibles.', 'Codes HTTP, chemins consultés et activité horaire. Analyse locale des formats Apache Common et Combined.', [('Requêtes reconnues', report['requests']), ('Erreurs HTTP', report['http_errors']), ('Taux d’erreur', f'{report["error_rate"]}%')], body, 'LOG INSIGHT')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', type=Path)
    parser.add_argument('--output', type=Path, default=Path('report.html'))
    parser.add_argument('--json', type=Path, dest='json_output')
    parser.add_argument('--fail-on-errors', action='store_true')
    args = parser.parse_args()
    try:
        targets = [args.output] + ([args.json_output] if args.json_output else [])
        resolved = [p.resolve() for p in targets]
        if args.log.resolve() in resolved or len(set(resolved)) != len(resolved):
            raise ValueError('Entrée et sorties doivent être distinctes')
        with args.log.open(encoding='utf-8-sig') as stream:
            report = analyze(stream)
        args.output.write_text(render_html(report), encoding='utf-8')
        if args.json_output:
            args.json_output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    except (OSError, ValueError) as error:
        parser.exit(2, f'Erreur : {error}\n')
    print(f"{report['requests']} requêtes, {report['http_errors']} erreurs HTTP, {report['invalid_lines']} lignes ignorées. Rapport : {args.output}")
    return 1 if args.fail_on_errors and (report['http_errors'] or report['invalid_lines']) else 0


if __name__ == '__main__':
    raise SystemExit(main())
