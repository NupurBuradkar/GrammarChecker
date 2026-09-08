"""
Punctuation Checker Module
Handles introductory adverbial commas ("However the result was good" -> "However,"),
sentence start capitalization, missing terminal periods, spacing around punctuation,
and duplicate punctuation marks.
"""

import re
from typing import List
from .preprocessor import ProcessedDocument, Sentence


INTRODUCTORY_WORDS = [
    "however", "therefore", "furthermore", "moreover", "in addition",
    "for example", "for instance", "on the other hand", "in contrast",
    "consequently", "as a result", "meanwhile", "first of all",
    "finally", "initially", "ultimately", "obviously", "interestingly",
    "fortunately", "unfortunately", "in fact", "surprisingly"
]


class PunctuationChecker:
    def __init__(self):
        pass

    def check(self, doc: ProcessedDocument) -> list:
        issues = []
        raw_text = doc.raw_text

        # 1. Capitalization of first word of each sentence
        self._check_sentence_capitalization(doc, issues)

        # 2. Introductory words missing comma ("However the result was good" -> "However,")
        self._check_introductory_commas(doc, issues)

        # 3. Missing terminal punctuation at the end of complete sentences
        self._check_terminal_punctuation(doc, issues)

        # 4. Spacing around punctuation (e.g. "hello ,world" or "hello,world")
        self._check_punctuation_spacing(raw_text, issues)

        # 5. Repeated punctuation marks (e.g. "??" or ",,")
        self._check_repeated_punctuation(raw_text, issues)

        return issues

    def _check_sentence_capitalization(self, doc: ProcessedDocument, issues: list):
        for sent in doc.sentences:
            words = [t for t in sent.tokens if t.is_word]
            if words:
                first_word_tok = words[0]
                # If first token starts with lowercase letter
                if first_word_tok.text and first_word_tok.text[0].islower():
                    rep = first_word_tok.text[0].upper() + first_word_tok.text[1:]
                    issues.append({
                        "start": first_word_tok.start,
                        "end": first_word_tok.end,
                        "original": first_word_tok.text,
                        "replacement": rep,
                        "category": "Punctuation",
                        "rule_id": "SENTENCE_START_CAPITALIZATION",
                        "message": f'Sentences should start with a capital letter: "{rep}".',
                        "explanation": 'The first word of a sentence must be capitalized in standard English.',
                        "severity": "error"
                    })

    def _check_introductory_commas(self, doc: ProcessedDocument, issues: list):
        for sent in doc.sentences:
            s_text = sent.text.strip()
            for intro in INTRODUCTORY_WORDS:
                # Pattern: starts with intro phrase, followed by space, but NOT comma
                pattern = rf"^(?P<intro>{re.escape(intro)})\s+(?=[A-Za-z])"
                m = re.match(pattern, s_text, re.IGNORECASE)
                if m:
                    intro_matched = m.group("intro")
                    # Locate exact character position in original doc
                    abs_start = sent.start + s_text.lower().find(intro_matched.lower())
                    abs_end = abs_start + len(intro_matched)
                    rep = intro_matched + ","
                    issues.append({
                        "start": abs_start,
                        "end": abs_end,
                        "original": intro_matched,
                        "replacement": rep,
                        "category": "Punctuation",
                        "rule_id": "INTRODUCTORY_COMMA",
                        "message": f'Add a comma after introductory transition "{intro_matched}".',
                        "explanation": f'Introductory phrases like "{intro_matched}" should typically be followed by a comma.',
                        "severity": "suggestion"
                    })

    def _check_terminal_punctuation(self, doc: ProcessedDocument, issues: list):
        # If document ends without a terminal mark (., !, ?)
        if not doc.raw_text.strip():
            return
        trimmed = doc.raw_text.rstrip()
        if len(trimmed) > 0 and trimmed[-1] not in {".", "!", "?", "\"", "'", "”", ";", ":"}:
            # Check if text looks like a complete sentence (more than 2 words)
            total_words = len([t for t in doc.tokens if t.is_word])
            if total_words >= 3:
                issues.append({
                    "start": len(trimmed),
                    "end": len(trimmed),
                    "original": "",
                    "replacement": ".",
                    "category": "Punctuation",
                    "rule_id": "MISSING_TERMINAL_PERIOD",
                    "message": 'Missing ending punctuation mark (period).',
                    "explanation": 'Sentences should normally end with a period, question mark, or exclamation mark.',
                    "severity": "suggestion"
                })

    def _check_punctuation_spacing(self, text: str, issues: list):
        # Space before comma/period/semicolon/colon (e.g. "word , next")
        for m in re.finditer(r"(\w+)\s+([,.;:!?])", text):
            word = m.group(1)
            punct = m.group(2)
            issues.append({
                "start": m.start(),
                "end": m.end(),
                "original": m.group(0),
                "replacement": f"{word}{punct}",
                "category": "Punctuation",
                "rule_id": "SPACE_BEFORE_PUNCTUATION",
                "message": f'Unexpected space before "{punct}".',
                "explanation": 'Punctuation marks should immediately follow the preceding word without a space.',
                "severity": "error"
            })

        # Missing space after comma/semicolon/colon (e.g. "apple,banana" -> "apple, banana")
        for m in re.finditer(r"([,;:])([A-Za-z0-9])", text):
            punct = m.group(1)
            next_char = m.group(2)
            issues.append({
                "start": m.start(),
                "end": m.end(),
                "original": m.group(0),
                "replacement": f"{punct} {next_char}",
                "category": "Punctuation",
                "rule_id": "MISSING_SPACE_AFTER_PUNCTUATION",
                "message": f'Missing space after "{punct}".',
                "explanation": 'Put a space after a comma, semicolon, or colon before starting the next word.',
                "severity": "error"
            })

    def _check_repeated_punctuation(self, text: str, issues: list):
        # Consecutive commas or semicolons (,, -> ,)
        for m in re.finditer(r"([,;]){2,}", text):
            issues.append({
                "start": m.start(),
                "end": m.end(),
                "original": m.group(0),
                "replacement": m.group(1),
                "category": "Punctuation",
                "rule_id": "REPEATED_PUNCTUATION",
                "message": f'Repeated punctuation marks "{m.group(0)}".',
                "explanation": 'Replace repeated punctuation marks with a single punctuation mark.',
                "severity": "suggestion"
            })


punctuation_checker = PunctuationChecker()
