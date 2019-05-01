#!/usr/bin/python3

"""
step3 solver for Trustpilot code challenge.
Solving steps:
    1. filter word dictionary to make it as small as possible for given search phrase
    2. Generate char histogram for each word
    3. Go recursively through word list, combining words until a match is found
    4. Try all permutations of found match
    5. Check if its hash is in searched hashes list

Notes:
    Some methods are in class, some are not. Don't know what's your preference, class-ify everything or not?

"""

import hashlib
import itertools
from collections import Counter


class AnagramStatus:  # enum
    VALID = 'V'           # This is a valid anagram
    INCOMPLETE = 'I'      # Some letters are still unused, continue search by adding a new word or use a next word
    OVERFLOW = 'O'        # Current string contains too much letters from original anagram, or dicitonary was exhausted


class Word:
    """
    word as string plus as histogram
    to avoid recalculating histogram in each iteration
    """
    def __init__(self, word):
        self.word = word
        self.histogram = string_histogram(word)

    def __str__(self):
        return self.word

    def __len__(self):  # For sorting when key=len
        return len(self.word)


def load_file_to_list(filename):
    with open(filename) as file:
        return [line.strip() for line in file]


def filter_with_irrelevant_chars(wordlist, anagram_histogram):
    """
    Filters the wordlist so that only words with letters from the anagram_histogram remain
    """
    retlist = []
    is_bad = False
    for word in wordlist:
        for char in word:
            if char not in anagram_histogram:
                is_bad = True
                break
        if not is_bad:
            retlist.append(word)
        is_bad = False
    return retlist


def filter_with_too_many_same(wordlist, anagram_histogram):
    """
    filters words that are not usable right away due to too many repeating letters
    for example the word "alabama" is not usable in "a lamb" due to too many a's
    """
    retlist = []
    empty_word = Word('')
    for word in wordlist:
        if get_status(Word(word).histogram, empty_word, anagram_histogram) == AnagramStatus.OVERFLOW:
            continue
        retlist.append(word)
    return retlist


def dedeuplicate(wordlist):
    """
    remove duplicates since you have given me a dictionary that contains duplicates.
    Is it even a dictionary if it contains duplicate words?
    """
    return list(dict.fromkeys(wordlist))


def string_histogram(str):
    """
    Create a histogram that contains number of occurrences of chars in str, ignoring whitespace
    iirc histogram is a collection of things and frequencies
    """
    ret = Counter()  # I guess dict with key:char value:freq is also fine
    for c in str:
        if c != ' ':
            ret[c] += 1
    return ret


def list_to_histogram_list(wordlist):
    newlist = []
    for word in wordlist:
        newlist.append(Word(word))
    return newlist


def compare_histograms(phrase_histogram, anagram_histogram):
    any_letter_unused = False
    for c in anagram_histogram:
        diff = anagram_histogram[c] - phrase_histogram[c]
        if diff > 0:
            any_letter_unused = True
        elif diff < 0:
            return AnagramStatus.OVERFLOW

    return AnagramStatus.INCOMPLETE if any_letter_unused else AnagramStatus.VALID


def get_status(current_histogram, new_word, anagram_histogram):
    phrase_histogram = current_histogram + new_word.histogram
    return compare_histograms(phrase_histogram, anagram_histogram)


class AnagramSearcher:
    def __init__(self, list_or_filename, phrase, callback):
        self.anagram_histogram = string_histogram(phrase)

        # Load dictionary and filter unusable words
        # when loaded, wordlist is just a list of strings
        if type(list_or_filename) is str:
            self.wordlist = load_file_to_list(list_or_filename)
            self.wordlist = filter_with_irrelevant_chars(self.wordlist, self.anagram_histogram)
            self.wordlist = dedeuplicate(self.wordlist)
            self.wordlist = filter_with_too_many_same(self.wordlist, self.anagram_histogram)
        else:
            self.wordlist = list_or_filename

        # to avoid short useless words as long as possible
        # a heuristic but turns out it works
        self.wordlist.sort(key=len, reverse=True)
        # convert list of strings into list of Words
        self.wordlist = list_to_histogram_list(self.wordlist)
        # callback when anagram is found
        self.callback = callback

    def search(self, max_words):
        """
        Search for anagrams
        :param max_words: max length of anagram, in words
        :return: nothing, results are processed through callback
        """
        self.do_search(0, max_words, [])

    def do_search(self, start_index, max_words, current_phrase):
        new_phrase = current_phrase

        current_histogram = Counter()
        for word in current_phrase:
            current_histogram += word.histogram

        for i in range(start_index, len(self.wordlist)):
            new_status = get_status(current_histogram, self.wordlist[i], self.anagram_histogram)

            if new_status == AnagramStatus.VALID:
                new_phrase.append(self.wordlist[i])
                self.do_permutations(new_phrase)
                del new_phrase[-1]
                continue
            elif new_status == AnagramStatus.INCOMPLETE:
                if len(current_phrase) + 1 >= max_words:  # limit recursion depth
                    continue
                new_phrase.append(self.wordlist[i])
                self.do_search(i, max_words, new_phrase)
                del new_phrase[-1]

    def do_permutations(self, current_phrase):
        permutations = itertools.permutations(current_phrase)
        for mutation in permutations:
                self.callback(self.wordlist_to_str(mutation))

    @staticmethod
    def wordlist_to_str(phrase_wordlist):
        str = ''.join(word.word + ' ' for word in phrase_wordlist)
        return str.strip()


class AnagramCallback:
    def __init__(self, search_hashes, how_many_enough=-1):
        self.search_hashes = search_hashes
        self.how_many_enough = how_many_enough
        self.found_counter = 0

    def __call__(self, str):
        m = hashlib.md5()
        m.update(str.encode('utf8'))
        if m.hexdigest() in self.search_hashes:
            print(str)
            self.found_counter += 1
            if 0 < self.how_many_enough == self.found_counter:
                exit(0)
            # ^ quit, because after two anagrams are found, there is no point to run


if __name__ == '__main__':

    search_hashes = (
        'e4820b45d2277f3844eac66c903e84be',
        '23170acc097c24edb98fc5488ab033fe',
        '665e5bcb0c20062fe8abaaf4628bb154',
    )

    # Callback assumes two found anagrams is enough, and exit the script
    searcher = AnagramSearcher('wordlist', 'poultry outwits ants', AnagramCallback(search_hashes, 2))
    searcher.search(3)  # could be a loop, starting search with one word but I already know it's 3 words
