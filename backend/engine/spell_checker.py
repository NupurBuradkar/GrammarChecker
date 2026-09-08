"""
Spelling Checker Module
Combines SymSpell frequency lookup, curated misspelling dictionaries,
contraction restorers, case preservation, and user custom dictionary.
"""

import os
from typing import List, Optional
import symspellpy
from symspellpy import SymSpell, Verbosity
from .preprocessor import ProcessedDocument, Token
from .user_dictionary import user_dict


COMMON_MISSPELLINGS = {
    "recieve": "receive",
    "recieved": "received",
    "recieving": "receiving",
    "freind": "friend",
    "freinds": "friends",
    "frined": "friend",
    "definately": "definitely",
    "definatly": "definitely",
    "seperate": "separate",
    "seperated": "separated",
    "seperation": "separation",
    "occurrance": "occurrence",
    "occured": "occurred",
    "occuring": "occurring",
    "accomodate": "accommodate",
    "accomodation": "accommodation",
    "embarass": "embarrass",
    "embarassing": "embarrassing",
    "goverment": "government",
    "enviroment": "environment",
    "beautifull": "beautiful",
    "allways": "always",
    "begining": "beginning",
    "tommorow": "tomorrow",
    "tommorrow": "tomorrow",
    "untill": "until",
    "alot": "a lot",
    "wierd": "weird",
    "thier": "their",
    "adress": "address",
    "becuase": "because",
    "calender": "calendar",
    "sucess": "success",
    "sucessful": "successful",
    "responsibile": "responsible",
    "langauge": "language",
    "programing": "programming",
    "grammer": "grammar",
    "assigment": "assignment",
    "tierd": "tired",
    "neccessary": "necessary",
    "independant": "independent",
    "persue": "pursue",
    "arguement": "argument",
    "knowlege": "knowledge",
    "acheive": "achieve",
    "publically": "publicly",
    "truely": "truly",
    "succesfully": "successfully",
    "noticable": "noticeable",
    "mispell": "misspell",
    "mispelled": "misspelled",
    "reccomend": "recommend",
    "recomended": "recommended",
    "maintainance": "maintenance",
    "colleague": "colleague",
    "collegue": "colleague",
    "beleive": "believe",
    "beleived": "believed",
    "writting": "writing",
    "existance": "existence",
    "possession": "possession",
    "posession": "possession",
    "fourty": "forty",
    "nineth": "ninth",
    "untill": "until"
}

CONTRACTIONS = {
    "dont": "don't",
    "cant": "can't",
    "wont": "won't",
    "isnt": "isn't",
    "arent": "aren't",
    "wasnt": "wasn't",
    "werent": "weren't",
    "didnt": "didn't",
    "doesnt": "doesn't",
    "havent": "haven't",
    "hasnt": "hasn't",
    "hadnt": "hadn't",
    "couldnt": "couldn't",
    "shouldnt": "shouldn't",
    "wouldnt": "wouldn't",
    "mustnt": "mustn't",
    "theyre": "they're",
    "youre": "you're",
    "ive": "I've",
    "ill": "I'll",
    "youll": "you'll",
    "theyll": "they'll",
    "weve": "we've",
    "whatll": "what'll",
    "thats": "that's",
    "whats": "what's",
    "wheres": "where's",
    "hows": "how's",
    "theres": "there's",
    "heres": "here's"
}

PROTECTED_WORDS = {
    "grammarly", "google", "microsoft", "apple", "amazon", "python", "fastapi",
    "uvicorn", "javascript", "html", "css", "github", "api", "url", "json",
    "nltk", "ai", "nlp", "ui", "ux", "lenovo", "mumbai", "india", "delhi", "london", "paris"
}


def match_casing(original: str, replacement: str) -> str:
    if not replacement or not original:
        return replacement
    if original.isupper() and len(original) > 1:
        return replacement.upper()
    if original[0].isupper():
        return replacement[0].upper() + replacement[1:]
    return replacement


class SpellChecker:
    def __init__(self):
        self.sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
        # Load default English frequency dictionary from symspellpy package
        dict_path = symspellpy.__file__
        dict_dir = os.path.dirname(dict_path)
        frequency_dict_path = os.path.join(dict_dir, "frequency_dictionary_en_82_765.txt")

        if os.path.exists(frequency_dict_path):
            self.sym_spell.load_dictionary(frequency_dict_path, term_index=0, count_index=1)
        else:
            print("SymSpell frequency dictionary not found in expected path.")

    def check(self, doc: ProcessedDocument) -> list:
        issues = []
        for tok in doc.tokens:
            if not tok.is_word:
                continue

            word = tok.text
            word_lower = tok.lower

            # Skip single letters except 'a' and 'i'
            if len(word) == 1:
                if word_lower not in {"a", "i"}:
                    continue
                if word == "i":
                    issues.append({
                        "start": tok.start,
                        "end": tok.end,
                        "original": word,
                        "replacement": "I",
                        "category": "Spelling",
                        "rule_id": "STANDALONE_I",
                        "message": f'The pronoun "i" should always be capitalized.',
                        "explanation": 'The standalone first-person pronoun "I" must always be written in uppercase.',
                        "severity": "error"
                    })
                continue

            # Skip user dictionary and protected words
            if user_dict.contains(word_lower) or word_lower in PROTECTED_WORDS:
                continue

            # Check contractions
            if word_lower in CONTRACTIONS:
                rep = match_casing(word, CONTRACTIONS[word_lower])
                issues.append({
                    "start": tok.start,
                    "end": tok.end,
                    "original": word,
                    "replacement": rep,
                    "category": "Spelling",
                    "rule_id": "MISSING_APOSTROPHE",
                    "message": f'Missing apostrophe in contraction "{word}".',
                    "explanation": f'"{word}" is missing an apostrophe. Did you mean "{rep}"?',
                    "severity": "error"
                })
                continue

            # Check common misspellings
            if word_lower in COMMON_MISSPELLINGS:
                rep = match_casing(word, COMMON_MISSPELLINGS[word_lower])
                issues.append({
                    "start": tok.start,
                    "end": tok.end,
                    "original": word,
                    "replacement": rep,
                    "category": "Spelling",
                    "rule_id": "COMMON_MISSPELLING",
                    "message": f'Possible spelling mistake: "{word}".',
                    "explanation": f'The word "{word}" is commonly misspelled. Recommended correction is "{rep}".',
                    "severity": "error"
                })
                continue

            # Check with SymSpell if the word does not exist in dictionary
            suggestions = self.sym_spell.lookup(word_lower, Verbosity.CLOSEST, max_edit_distance=2)
            
            # If word is in dictionary, suggestions[0].distance == 0
            if suggestions:
                best = suggestions[0]
                if best.distance > 0:
                    # Misspelled word
                    rep = match_casing(word, best.term)
                    issues.append({
                        "start": tok.start,
                        "end": tok.end,
                        "original": word,
                        "replacement": rep,
                        "category": "Spelling",
                        "rule_id": "SPELL_SUGGESTION",
                        "message": f'Possible spelling mistake: "{word}".',
                        "explanation": f'"{word}" appears to be misspelled. Suggestion: "{rep}".',
                        "severity": "error"
                    })
            else:
                # No close match found in dictionary, only flag if it looks like an English word
                if len(word) >= 3 and not word.isupper() and not any(c.isdigit() for c in word):
                    issues.append({
                        "start": tok.start,
                        "end": tok.end,
                        "original": word,
                        "replacement": "",
                        "category": "Spelling",
                        "rule_id": "UNKNOWN_WORD",
                        "message": f'Unrecognized word: "{word}".',
                        "explanation": f'"{word}" was not found in the dictionary. Check spelling or add it to your custom dictionary.',
                        "severity": "warning"
                    })

        return issues


spell_checker = SpellChecker()
