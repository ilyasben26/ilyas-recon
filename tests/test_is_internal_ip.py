import unittest
from core.dns import is_internal_ip

class TestIsInternalIp(unittest.TestCase):
    def test_internal_ips(self):
        self.assertTrue(is_internal_ip("192.168.1.1"))
        self.assertTrue(is_internal_ip("10.0.0.1"))
        self.assertTrue(is_internal_ip("172.16.0.1"))
        self.assertTrue(is_internal_ip("172.31.255.255"))

    def test_external_ips(self):
        self.assertFalse(is_internal_ip("8.8.8.8"))
        self.assertFalse(is_internal_ip("1.1.1.1"))

    def test_invalid_ips(self):
        self.assertFalse(is_internal_ip("999.999.999.999"))
        self.assertFalse(is_internal_ip("invalid_ip"))

if __name__ == "__main__":
    unittest.main()
