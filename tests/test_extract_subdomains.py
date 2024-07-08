import unittest
from unittest.mock import mock_open, patch
from core.targets import extract_subdomains

class TestExtractSubdomains(unittest.TestCase):

    def test_extract_subdomains(self):
        file_content = """
        https://subdomain1.example.com
        ftp://subdomain2.example.net
        invalidurl
        subdomain3.test.wow.com
        test.com
        """

        expected_subdomains = ['subdomain1.example.com', 'subdomain2.example.net', 'subdomain3.test.wow.com','test.com']

        # Mocking the file reading
        with patch('builtins.open', mock_open(read_data=file_content)):
            actual_subdomains = extract_subdomains('mocked_filename.txt')

        self.assertEqual(actual_subdomains, expected_subdomains)

if __name__ == '__main__':
    unittest.main()

