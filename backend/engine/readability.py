"""
Readability & Statistics Module
Calculates Flesch Reading Ease, Flesch-Kincaid Grade Level, Syllable counts,
Reading/Speaking times, and the overall Sentence Accuracy Score.
"""

import math
import re
from typing import Dict, Any, List
from .preprocessor import ProcessedDocument, Token


def count_syllables(word: str) -> int:
    w = word.lower().strip()
    if not w:
        return 0
    if len(w) <= 3:
        return 1

    # Remove non-alpha
    w = re.sub(r"[^a-z]", "", w)
    if not w:
        return 1

    # Handle standard endings
    w = re.sub(r"(?:[^laeiouy]|ed|es|e)$", "", w)
    w = re.sub(r"^y", "", w)
    syllables = len(re.findall(r"[aeiouy]{1,2}", w))
    return max(1, syllables)


class ReadabilityCalculator:
    def __init__(self):
        pass

    def calculate_stats(self, doc: ProcessedDocument, issues: List[dict]) -> Dict[str, Any]:
        text = doc.raw_text
        if not text.strip():
            return {
                "word_count": 0,
                "character_count": 0,
                "character_count_no_spaces": 0,
                "sentence_count": 0,
                "reading_time_minutes": 0.0,
                "speaking_time_minutes": 0.0,
                "avg_sentence_length": 0.0,
                "avg_word_length": 0.0,
                "flesch_reading_ease": 100.0,
                "flesch_kincaid_grade": 0.0,
                "readability_label": "Very Easy to Read",
                "accuracy_percentage": 100,
                "accuracy_rating": "Excellent"
            }

        words = [t.text for t in doc.tokens if t.is_word]
        total_words = len(words)
        total_chars = len(text)
        total_chars_no_spaces = len(text.replace(" ", "").replace("\n", "").replace("\t", ""))
        total_sentences = max(1, len(doc.sentences))

        if total_words == 0:
            return {
                "word_count": 0,
                "character_count": total_chars,
                "character_count_no_spaces": total_chars_no_spaces,
                "sentence_count": total_sentences,
                "reading_time_minutes": 0.0,
                "speaking_time_minutes": 0.0,
                "avg_sentence_length": 0.0,
                "avg_word_length": 0.0,
                "flesch_reading_ease": 100.0,
                "flesch_kincaid_grade": 0.0,
                "readability_label": "Very Easy to Read",
                "accuracy_percentage": 100,
                "accuracy_rating": "Excellent"
            }

        # Syllables
        total_syllables = sum(count_syllables(w) for w in words)

        # Average metrics
        asl = total_words / total_sentences
        asw = total_syllables / total_words
        avg_word_len = sum(len(w) for w in words) / total_words

        # Flesch Reading Ease
        fre = 206.835 - (1.015 * asl) - (84.6 * asw)
        fre = max(0.0, min(100.0, round(fre, 1)))

        # Flesch-Kincaid Grade Level
        fkgl = (0.39 * asl) + (11.8 * asw) - 15.59
        fkgl = max(0.0, min(18.0, round(fkgl, 1)))

        # Readability label
        if fre >= 90:
            readability_label = "Very Easy (5th Grade)"
        elif fre >= 80:
            readability_label = "Easy (6th Grade)"
        elif fre >= 70:
            readability_label = "Fairly Easy (7th Grade)"
        elif fre >= 60:
            readability_label = "Standard (8th–9th Grade)"
        elif fre >= 50:
            readability_label = "Fairly Difficult (10th–12th Grade)"
        elif fre >= 30:
            readability_label = "Difficult (College)"
        else:
            readability_label = "Very Difficult (Graduate)"

        # Reading & speaking times
        reading_time = round(total_words / 200, 2)  # ~200 wpm
        speaking_time = round(total_words / 130, 2)  # ~130 wpm

        # Accuracy Percentage Calculation
        # Count weighted errors
        error_weight = 0
        for issue in issues:
            cat = issue.get("category", "")
            sev = issue.get("severity", "error")
            if cat in {"Spelling", "Grammar", "Context"} or sev == "error":
                error_weight += 12.0
            else:
                error_weight += 4.0

        if not issues:
            accuracy_percentage = 100
        else:
            # Normalize penalty relative to text length
            # A 5-word sentence with 1 error: penalty = 12 / max(1, 0.5) = 24 -> 76%
            # A 1-word sentence with 1 error: penalty = 12 / 0.2 = 60 -> 40%
            scaling = max(0.5, total_words / 10.0)
            penalty = error_weight / scaling
            accuracy_percentage = max(0, min(99, int(round(100 - penalty))))

        # Rating label
        if accuracy_percentage >= 95:
            accuracy_rating = "Excellent"
        elif accuracy_percentage >= 85:
            accuracy_rating = "Good"
        elif accuracy_percentage >= 70:
            accuracy_rating = "Needs Improvement"
        else:
            accuracy_rating = "Critical Issues"

        return {
            "word_count": total_words,
            "character_count": total_chars,
            "character_count_no_spaces": total_chars_no_spaces,
            "sentence_count": total_sentences,
            "reading_time_minutes": reading_time,
            "speaking_time_minutes": speaking_time,
            "avg_sentence_length": round(asl, 1),
            "avg_word_length": round(avg_word_len, 1),
            "flesch_reading_ease": fre,
            "flesch_kincaid_grade": fkgl,
            "readability_label": readability_label,
            "accuracy_percentage": accuracy_percentage,
            "accuracy_rating": accuracy_rating
        }


readability_calculator = ReadabilityCalculator()
