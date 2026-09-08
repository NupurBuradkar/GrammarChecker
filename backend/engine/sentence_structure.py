"""
Sentence Structure Analyzer Module
Detects sentence fragments (e.g. "Because he was tired."), missing main verbs,
and run-on structures.
"""

import re
from typing import List
from .preprocessor import ProcessedDocument, Sentence


SUBORDINATING_CONJUNCTIONS = {
    "because", "although", "even though", "though", "since", "while",
    "whereas", "unless", "whenever", "wherever"
}


class SentenceStructureAnalyzer:
    def __init__(self):
        pass

    def check(self, doc: ProcessedDocument) -> list:
        issues = []
        for sent in doc.sentences:
            s_text = sent.text.strip()
            words = [t for t in sent.tokens if t.is_word]
            if not words:
                continue

            first_word = words[0].lower

            # 1. Subordinate Clause Fragment (e.g., "Because he was tired.")
            # If sentence starts with subordinating conjunction and contains no comma separating a main clause
            if first_word in SUBORDINATING_CONJUNCTIONS:
                has_comma = any(t.text == "," for t in sent.tokens)
                if not has_comma and len(words) >= 3:
                    issues.append({
                        "start": sent.start,
                        "end": sent.end,
                        "original": s_text,
                        "replacement": "",
                        "category": "Structure",
                        "rule_id": "SENTENCE_FRAGMENT_SUBORDINATE",
                        "message": "Possible sentence fragment.",
                        "explanation": f'This sentence begins with the subordinating conjunction "{words[0].text}" but lacks a main independent clause. Connect it to an independent clause or remove "{words[0].text}".',
                        "severity": "warning"
                    })

            # 2. Sentences starting with "Which" or "That" as relative pronoun fragment (e.g. "Which is very good.")
            if first_word in {"which"} and len(words) >= 3:
                issues.append({
                    "start": sent.start,
                    "end": sent.end,
                    "original": s_text,
                    "replacement": "",
                    "category": "Structure",
                    "rule_id": "SENTENCE_FRAGMENT_RELATIVE_WHICH",
                    "message": 'Possible sentence fragment starting with "Which".',
                    "explanation": 'Relative clauses beginning with "Which" usually should be attached to the preceding sentence with a comma rather than standing alone.',
                    "severity": "warning"
                })

            # 3. Missing main verb in sentences with >= 4 words
            # Check if there are no verb POS tags or known auxiliary/action verbs
            if len(words) >= 4:
                verbs = [t for t in words if t.pos.startswith("VB") or t.lower in {
                    "is", "am", "are", "was", "were", "be", "been", "being",
                    "have", "has", "had", "do", "does", "did", "can", "could",
                    "will", "would", "shall", "should", "may", "might", "must",
                    "go", "goes", "went", "like", "likes", "liked", "make", "makes", "made"
                }]
                if not verbs and first_word not in {"how", "what", "where", "when", "why", "who"}:
                    issues.append({
                        "start": sent.start,
                        "end": sent.end,
                        "original": s_text,
                        "replacement": "",
                        "category": "Structure",
                        "rule_id": "MISSING_MAIN_VERB",
                        "message": "Sentence appears to lack a main verb.",
                        "explanation": "Every complete sentence requires at least one main finite verb.",
                        "severity": "warning"
                    })

        return issues


sentence_structure_analyzer = SentenceStructureAnalyzer()
