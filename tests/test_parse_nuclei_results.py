import unittest
from unittest.mock import mock_open, patch
from core.nuclei import parse_nuclei_results

class TestParseNucleiResults(unittest.TestCase):
    def test_parse_nuclei_results(self):
        file_content = """
        [tag1] [tag2] example.com 
        [tag3] https://test.org
        [tag4] invalid-entry [tag5] [tag6]
        [tag7] [tag8] [tag9] https://another-example.net [tag10]
        """

        expected_result = [
            ("example.com", "[tag1][tag2]"),
            ("test.org", "[tag3]"),
            ("another-example.net", "[tag7][tag8][tag9][tag10]")
        ]

        with patch("builtins.open", mock_open(read_data=file_content)):
            result = parse_nuclei_results("dummy_filename.txt")
            self.assertEqual(result, expected_result)

if __name__ == "__main__":
    unittest.main()
