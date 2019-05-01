#!/usr/bin/python3
"""
Some test provided. 
"""

import unittest
from unittest.mock import patch, Mock
from io import StringIO
from step3 import *


class TestSum(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestSum, self).__init__(*args, **kwargs)
        self.phrase = []
        self.phrase.append(Word("Hello"))
        self.phrase.append(Word("World"))

    def test_wordlist_to_str(self):
        result = AnagramSearcher.wordlist_to_str(self.phrase)
        self.assertEqual(result, "Hello World")

    def test_anagram_callback_anagram(self):
        search_hashes = (
            'e4820b45d2277f3844eac66c903e84be',
            '23170acc097c24edb98fc5488ab033fe',
            '665e5bcb0c20062fe8abaaf4628bb154',
            "00278abe9e7c3c7a38570b833bae3e7f",  # <- "fairy tales"
        )

        phrase = "fairy tales"
        callback = AnagramCallback(search_hashes)
        with patch('sys.stdout', new=StringIO()) as fakeOutput:
            callback(phrase)
            self.assertEqual(fakeOutput.getvalue().strip(), phrase, "Should print \'%s\'" % phrase)

    def test_deduplicate(self):
        initial = [
            "aaa", "aaa",
            "one",
            "bbb", "bbb", "bbb",
            "two",
            "ccc", "ccc"
        ]
        expected = ["aaa", "one", "bbb", "two", "ccc"]
        ret = dedeuplicate(initial)
        self.assertEqual(expected, ret)

    def test_anagram_find(self):
        dictionary = [
            'safe',
            'fairy',
            'fear',
            'ty',
            'tales',
        ]
        phrase = "rail safety"

        callback = Mock()
        searcher = AnagramSearcher(dictionary, phrase, callback)
        searcher.search(3)
        self.assertEqual(callback.call_count, 2, "callback should be called twice, which is one two word anagram, two permutations")


if __name__ == '__main__':
    unittest.main()
