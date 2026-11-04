import unittest
from analyze import parse_line, analyze, render_html


def line(ip='192.0.2.1', request='GET / HTTP/1.1', status='200', date='04/Nov/2026:08:00:00 +0100'):
    return f'{ip} - - [{date}] "{request}" {status} 120'


class LogTests(unittest.TestCase):
    def test_common_and_combined(self):
        self.assertEqual(parse_line(line())['status'], 200)
        self.assertEqual(parse_line(line() + ' "-" "DemoBrowser"')['bytes'], 120)

    def test_errors_and_ignored_lines(self):
        report = analyze([line(), line(status='404'), line(status='503'), 'bad', ''])
        self.assertEqual(report['requests'], 3)
        self.assertEqual(report['http_errors'], 2)
        self.assertEqual(report['invalid_lines'], 1)
        self.assertEqual(report['error_rate'], 66.67)

    def test_utc_and_address_aggregation(self):
        event = parse_line(line(ip='2001:db8:abcd::1', date='04/Nov/2026:00:30:00 +0100'))
        self.assertEqual(event['hour'], '2026-11-03 23:00 UTC')
        self.assertEqual(event['network'], '2001:db8:abcd::/48')
        self.assertEqual(parse_line(line())['network'], '192.0.2.0/24')

    def test_remove_url_query(self):
        self.assertEqual(parse_line(line(request='GET /search?token=demo HTTP/1.1'))['path'], '/search')

    def test_invalid_ip_date_and_request(self):
        for value in [line(ip='bad'), line(date='31/Feb/2026:00:00:00 +0100'), line(request='invalid'), line(date='04/Nov/2026:00:00:00 +0260')]:
            with self.assertRaises(ValueError):
                parse_line(value)

    def test_html_escape(self):
        result = render_html(analyze([line(request='GET /<script> HTTP/1.1')]))
        self.assertNotIn('<script>', result)
        self.assertIn('&lt;script&gt;', result)

    def test_empty_and_invalid_cap(self):
        self.assertEqual(analyze([])['error_rate'], 0)
        report = analyze(['bad'] * 20)
        self.assertEqual(report['invalid_lines'], 20)
        self.assertEqual(len(report['invalid_examples']), 10)
