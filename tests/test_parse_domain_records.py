import unittest
from core.dns import parse_domain_records

class TestParseDomainRecords(unittest.TestCase):
    def test_parse_valid_records(self):
        domain_records = [
            "example.com. A 192.168.1.1",
            "example.com. A 8.8.8.8",
            "example.com. AAAA 2001:4860:4860::8888",
            "test.org. A 10.0.0.1",
            "test.org. A 9.9.9.9"
        ]
        
        expected_result = {
            "example.com": ["A 8.8.8.8", "AAAA 2001:4860:4860::8888"],
            "test.org": ["A 9.9.9.9"]
        }

        result = parse_domain_records(domain_records)
        self.assertEqual(result, expected_result)

    def test_parse_empty_records(self):
        domain_records = []
        expected_result = {}
        result = parse_domain_records(domain_records)
        self.assertEqual(result, expected_result)

    def test_parse_no_internal_ip_records(self):
        domain_records = [
            "example.com. A 8.8.8.8",
            "example.com. AAAA 2001:4860:4860::8888"
        ]
        
        expected_result = {
            "example.com": ["A 8.8.8.8", "AAAA 2001:4860:4860::8888"]
        }

        result = parse_domain_records(domain_records)
        self.assertEqual(result, expected_result)
    
    def test_parse_with_cname_records(self):
        domain_records = [
            "example.com. CNAME alias.example.com.",
            "example.com. A 8.8.8.8",
            "test.org. CNAME alias.test.org.",
            "test.org. A 9.9.9.9"
        ]
        
        expected_result = {
            "example.com": ["CNAME alias.example.com.", "A 8.8.8.8"],
            "test.org": ["CNAME alias.test.org.", "A 9.9.9.9"]
        }

        result = parse_domain_records(domain_records)
        self.assertEqual(result, expected_result)

    def test_parse_with_internal_ip_cname_records(self):
        domain_records = [
            "example.com. A 192.168.1.1",
            "example.com. CNAME alias.example.com.",
            "example.com. A 8.8.8.8",
            "test.org. CNAME alias.test.org.",
            "test.org. A 10.0.0.1"
        ]
        
        expected_result = {
            "example.com": ["CNAME alias.example.com.", "A 8.8.8.8"],
            "test.org": ["CNAME alias.test.org."]
        }

        result = parse_domain_records(domain_records)
        self.assertEqual(result, expected_result)

if __name__ == "__main__":
    unittest.main()
