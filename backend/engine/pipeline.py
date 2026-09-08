"""
Master NLP Pipeline Module
Orchestrates preprocessing, spell checking, grammar checking, punctuation checking,
contextual analysis, vocabulary enhancement, style & tone evaluation,
issue deduplication, corrected text generation, and accuracy calculation.
"""

import re
from typing import Dict, Any, List
from .preprocessor import preprocessor, ProcessedDocument
from .spell_checker import spell_checker
from .grammar_checker import grammar_checker
from .punctuation_checker import punctuation_checker
from .context_checker import context_checker
from .sentence_structure import sentence_structure_analyzer
from .vocabulary_enhancer import vocabulary_enhancer
from .style_tone_analyzer import style_tone_analyzer
from .readability import readability_calculator


CATEGORY_PRIORITY = {
    "Grammar": 1,
    "Context": 2,
    "Spelling": 3,
    "Punctuation": 4,
    "Structure": 5,
    "Vocabulary": 6,
    "Style": 7,
    "Tone": 8
}


class NLPPipeline:
    def __init__(self):
        pass

    def analyze(self, text: str) -> Dict[str, Any]:
        if not text:
            return {
                "original_text": "",
                "corrected_text": "",
                "issues": [],
                "issue_counts": {
                    "total": 0, "spelling": 0, "grammar": 0,
                    "punctuation": 0, "context": 0, "vocabulary": 0,
                    "style": 0, "tone": 0, "structure": 0
                },
                "statistics": readability_calculator.calculate_stats(ProcessedDocument(raw_text=""), []),
                "tone_analysis": style_tone_analyzer.analyze_tone(ProcessedDocument(raw_text=""))
            }

        # 1. Preprocess text
        doc = preprocessor.process(text)

        # 2. Run all analytical components
        raw_issues: List[dict] = []
        raw_issues.extend(spell_checker.check(doc))
        raw_issues.extend(grammar_checker.check(doc))
        raw_issues.extend(punctuation_checker.check(doc))
        raw_issues.extend(context_checker.check(doc))
        raw_issues.extend(sentence_structure_analyzer.check(doc))
        raw_issues.extend(vocabulary_enhancer.check(doc))
        raw_issues.extend(style_tone_analyzer.check(doc))

        # 3. Deduplicate and resolve overlapping issue spans
        deduped_issues = self._resolve_overlaps(raw_issues, text)

        # 4. Generate corrected text
        corrected_text = self._generate_corrected_text(deduped_issues, text)

        # 5. Calculate statistics and accuracy percentage
        stats = readability_calculator.calculate_stats(doc, deduped_issues)

        # 6. Analyze overall tone
        tone = style_tone_analyzer.analyze_tone(doc)

        # 7. Count issues by category
        counts = {
            "total": len(deduped_issues),
            "spelling": 0,
            "grammar": 0,
            "punctuation": 0,
            "context": 0,
            "vocabulary": 0,
            "style": 0,
            "tone": 0,
            "structure": 0
        }
        for iss in deduped_issues:
            cat = iss.get("category", "").lower()
            if cat in counts:
                counts[cat] += 1

        return {
            "original_text": text,
            "corrected_text": corrected_text,
            "issues": deduped_issues,
            "issue_counts": counts,
            "statistics": stats,
            "tone_analysis": tone
        }

    def _resolve_overlaps(self, issues: List[dict], original_text: str) -> List[dict]:
        # Sort by start offset ascending, then by length descending
        sorted_issues = sorted(
            issues,
            key=lambda x: (
                x.get("start", 0),
                CATEGORY_PRIORITY.get(x.get("category", ""), 99),
                -(x.get("end", 0) - x.get("start", 0))
            )
        )

        resolved: List[dict] = []
        seen_keys = set()

        for candidate in sorted_issues:
            start = candidate.get("start", 0)
            end = candidate.get("end", 0)
            replacement = candidate.get("replacement", "")
            key = f"{start}_{end}_{candidate.get('rule_id')}_{replacement}"
            if key in seen_keys:
                continue

            # Check overlap with already accepted issues
            overlap_idx = -1
            for idx, existing in enumerate(resolved):
                e_start = existing.get("start", 0)
                e_end = existing.get("end", 0)

                # Check if spans intersect
                if max(start, e_start) < min(end, e_end) and (end > start) and (e_end > e_start):
                    overlap_idx = idx
                    break

            if overlap_idx >= 0:
                existing = resolved[overlap_idx]
                e_cat_prio = CATEGORY_PRIORITY.get(existing.get("category", ""), 99)
                c_cat_prio = CATEGORY_PRIORITY.get(candidate.get("category", ""), 99)

                # If candidate has strictly higher priority (lower number), replace existing
                if c_cat_prio < e_cat_prio:
                    resolved[overlap_idx] = candidate
                    seen_keys.add(key)
                elif c_cat_prio == e_cat_prio and not existing.get("replacement") and replacement:
                    resolved[overlap_idx] = candidate
                    seen_keys.add(key)
            else:
                resolved.append(candidate)
                seen_keys.add(key)

        # Re-sort by start offset and assign unique IDs
        resolved.sort(key=lambda x: (x.get("start", 0), x.get("end", 0)))
        for i, issue in enumerate(resolved):
            issue["id"] = f"issue_{i + 1}"
            # Ensure snippet context is provided
            s = max(0, issue["start"] - 15)
            e = min(len(original_text), issue["end"] + 15)
            issue["context_snippet"] = original_text[s:e]

        return resolved

    def _generate_corrected_text(self, issues: List[dict], original_text: str) -> str:
        if not issues:
            return original_text

        # Usable replacements only
        usable = [
            iss for iss in issues
            if iss.get("replacement") is not None and iss.get("replacement") != ""
        ]

        # Apply from end of text to start to keep offsets valid
        usable.sort(key=lambda x: x["start"], reverse=True)

        corrected = original_text
        for iss in usable:
            start = iss["start"]
            end = iss["end"]
            rep = iss["replacement"]
            if 0 <= start <= len(corrected) and 0 <= end <= len(corrected):
                corrected = corrected[:start] + rep + corrected[end:]

        # Minor whitespace & punctuation cleanup
        corrected = re.sub(r"[ \t]{2,}", " ", corrected)
        corrected = re.sub(r" ([,\.\?!;:])", r"\1", corrected)
        return corrected


nlp_pipeline = NLPPipeline()
