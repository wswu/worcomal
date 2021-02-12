from dataclasses import dataclass

# from joblib import delayed, Parallel
from tqdm import tqdm
from dawg import CompletionDAWG
from collections import Counter
import itertools

@dataclass
class Compound:
    lang: str
    word: str
    left: str
    right: str
    method: str
    middle: str

    def glue(self) -> str:
        return "" if self.method == "" else self.method[5:]

    def dropl(self) -> str:
        return "" if self.method == "" else self.method[5:]


def write_compounds(fn: str, compounds: list):
    with open(fn, 'w') as fout:
        for c in compounds:
            print('\t'.join(
                [c.lang, c.word, c.left, c.right, c.method]), file=fout)


def read_compounds(fn: str) -> list:
    compounds = []
    with open(fn) as fin:
        for line in fin:
            arr = line.strip('\n').split('\t')
            compounds.append(Compound(*arr))
    return compounds


# Compound Search

def flatten(arr: list) -> list:
    return [x for xs in arr for x in xs]


def make_tries(wordlist):
    tries = {}
    wordlist = sorted(wordlist, key=lambda x: x.lang)
    for lang, group in itertools.groupby(wordlist, key=lambda x: x.lang):
        words = [word for lang, word in group]
        tries[lang] = CompletionDAWG(words)
    return tries


def find_compounds(f2e: dict, methods: list, wordlist: list=None):
    if wordlist is None:
        wordlist = list(f2e.keys())
    
    wordlist = [w for w in wordlist if w in f2e]
    tries = make_tries(wordlist)

    for (lang, word) in tqdm(wordlist):
        for method in methods:
            for comp in decompose(f2e, lang, word, tries, method):
                yield comp


def decompose(f2e: dict, lang: str, word: str, tries: dict, method: str) -> list:
    if method == 'concat':
        return [Compound(lang, word, left, right, "concat", "")
                for (left, right) in segment2(word)
                if (lang, left) in f2e and (lang, right) in f2e]
    
    elif method == 'glue':
        return [Compound(lang, word, left, right, "glue", glue)
                for (left, glue, right) in segment3(word)
                if (lang, left) in f2e and (lang, right) in f2e]
    
    elif method == 'dropl':
        dropl_compounds = []
        for (partial_left, right) in segment2(word):
            if (lang, right) not in f2e:
                continue
            for left in tries[lang].keys(partial_left):
                if left != partial_left:
                    drop = left[len(partial_left):]
                    if len(drop) <= 3 and drop != right:  # todo: argument to change threshold
                        dropl_compounds.append(Compound(lang, word, left, right, "drop", drop))
        return dropl_compounds

    # todo: add other methods

    return []


def segment2(chars) -> list:
    result = []
    for mid in range(1, len(chars)):
        left = chars[0:mid]
        right = chars[mid:]
        result.append((left, right))
    return result


def segment3(chars) -> list:
    result = []
    for a in range(1, len(chars) - 1):
        for b in range(a + 1, len(chars)):
            left = chars[:a]
            glue = chars[a:b]
            right = chars[b:]
            result.append((left, glue, right))
    return result


# compound filtering

from .stats import *

def filter_compounds(compounds, glue_length=0, glue_frequency=0, dropl_length=0, dropl_frequency=0, method_frequency=0):
    if glue_length > 0:
        compounds = [c for c in compounds if len(c.glue()) <= glue_length]
    
    if dropl_length > 0:
        compounds = [c for c in compounds if len(c.dropl()) <= dropl_length]

    if method_frequency > 0:
        counts = count_methods_per_lang(compounds)
        compounds = [c for c in compounds if counts[c.lang][c.method] >= method_frequency]
    
    if glue_frequency > 0:
        counts = count_glues_per_lang(compounds)
        compounds = [c for c in compounds if counts[c.lang][c.glue()] >= glue_frequency]
    
    if dropl_frequency > 0:
        counts = count_dropl_per_lang(compounds)
        compounds = [c for c in compounds if counts[c.lang][c.dropl()] >= dropl_frequency]
        
    return compounds
    
