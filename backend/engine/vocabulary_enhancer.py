"""
Vocabulary Enhancer Module
Detects overused intensifiers and weak adjectives (e.g. "very bad" -> "disappointing")
and suggests richer, more evocative vocabulary choices.
"""

import re
from typing import List
from .preprocessor import ProcessedDocument, Token


VOCABULARY_SUGGESTIONS = [
    (r"\bvery\s+bad\b", ["disappointing", "substandard", "poor", "unfavorable"], "Consider using a more precise adjective instead of \"very bad\".", "VOCAB_VERY_BAD"),
    (r"\breally\s+bad\b", ["terrible", "dismal", "unsatisfactory"], "Replace \"really bad\" with a more impactful adjective.", "VOCAB_REALLY_BAD"),
    (r"\bvery\s+good\b", ["excellent", "superb", "outstanding", "exceptional"], "Use a more descriptive word instead of \"very good\".", "VOCAB_VERY_GOOD"),
    (r"\breally\s+good\b", ["impressive", "remarkable", "terrific"], "Enhance your writing by replacing \"really good\".", "VOCAB_REALLY_GOOD"),
    (r"\bvery\s+big\b", ["huge", "immense", "massive", "substantial"], "Replace \"very big\" with a more evocative adjective.", "VOCAB_VERY_BIG"),
    (r"\bvery\s+large\b", ["extensive", "immense", "colossal"], "Replace \"very large\" with a stronger word.", "VOCAB_VERY_LARGE"),
    (r"\bvery\s+small\b", ["tiny", "compact", "microscopic", "minute"], "Consider using \"tiny\" or \"compact\" instead of \"very small\".", "VOCAB_VERY_SMALL"),
    (r"\bvery\s+happy\b", ["delighted", "thrilled", "ecstatic", "overjoyed"], "Use a more expressive adjective than \"very happy\".", "VOCAB_VERY_HAPPY"),
    (r"\bvery\s+sad\b", ["devastated", "heartbroken", "sorrowful", "dejected"], "Consider using \"devastated\" or \"sorrowful\".", "VOCAB_VERY_SAD"),
    (r"\bvery\s+tired\b", ["exhausted", "fatigued", "drained"], "Replace \"very tired\" with \"exhausted\" or \"fatigued\".", "VOCAB_VERY_TIRED"),
    (r"\bvery\s+angry\b", ["furious", "irate", "enraged", "indignant"], "Consider \"furious\" or \"irate\" instead of \"very angry\".", "VOCAB_VERY_ANGRY"),
    (r"\bvery\s+important\b", ["crucial", "essential", "vital", "paramount"], "Use \"crucial\", \"vital\", or \"essential\" for greater impact.", "VOCAB_VERY_IMPORTANT"),
    (r"\bvery\s+beautiful\b", ["stunning", "gorgeous", "exquisite", "magnificent"], "Consider \"stunning\" or \"exquisite\".", "VOCAB_VERY_BEAUTIFUL"),
    (r"\bvery\s+fast\b", ["rapid", "swift", "brisk", "speedy"], "Consider \"rapid\" or \"swift\".", "VOCAB_VERY_FAST"),
    (r"\bvery\s+slow\b", ["sluggish", "leisurely", "gradual"], "Consider \"sluggish\" or \"gradual\".", "VOCAB_VERY_SLOW"),
    (r"\bvery\s+smart\b", ["brilliant", "ingenious", "astute", "sharp"], "Consider \"brilliant\" or \"astute\".", "VOCAB_VERY_SMART"),
    (r"\bvery\s+rich\b", ["wealthy", "affluent", "prosperous"], "Consider \"wealthy\" or \"affluent\".", "VOCAB_VERY_RICH"),
    (r"\bvery\s+poor\b", ["impoverished", "destitute", "underprivileged"], "Consider \"impoverished\" or \"destitute\".", "VOCAB_VERY_POOR"),
    (r"\bvery\s+hot\b", ["scorching", "sweltering", "boiling", "scalding"], "Consider \"scorching\" or \"sweltering\".", "VOCAB_VERY_HOT"),
    (r"\bvery\s+cold\b", ["freezing", "frigid", "bitterly cold"], "Consider \"freezing\" or \"frigid\".", "VOCAB_VERY_COLD"),
    (r"\bvery\s+simple\b", ["straightforward", "effortless", "elementary"], "Consider \"straightforward\" or \"effortless\".", "VOCAB_VERY_SIMPLE"),
    (r"\bvery\s+clean\b", ["spotless", "immaculate", "pristine"], "Consider \"spotless\" or \"pristine\".", "VOCAB_VERY_CLEAN"),
    (r"\bvery\s+interesting\b", ["fascinating", "captivating", "compelling"], "Consider \"fascinating\" or \"compelling\".", "VOCAB_VERY_INTERESTING"),
    (r"\ba\s+lot\s+of\b", ["numerous", "many", "substantial", "abundant"], "In formal writing, replace \"a lot of\" with \"numerous\" or \"many\".", "VOCAB_A_LOT_OF"),
]


class VocabularyEnhancer:
    def __init__(self):
        pass

    def check(self, doc: ProcessedDocument) -> list:
        issues = []
        raw_text = doc.raw_text

        for pattern, suggestions, explanation, rule_id in VOCABULARY_SUGGESTIONS:
            for m in re.finditer(pattern, raw_text, re.IGNORECASE):
                orig = m.group(0)
                best_replacement = suggestions[0]
                
                # Match casing
                if orig.isupper():
                    rep = best_replacement.upper()
                elif orig[0].isupper():
                    rep = best_replacement.capitalize()
                else:
                    rep = best_replacement

                issues.append({
                    "start": m.start(),
                    "end": m.end(),
                    "original": orig,
                    "replacement": rep,
                    "all_suggestions": suggestions,
                    "category": "Vocabulary",
                    "rule_id": rule_id,
                    "message": f'Enhance word choice: Replace "{orig}" with "{rep}".',
                    "explanation": f'{explanation} Alternative options: {", ".join(suggestions)}.',
                    "severity": "suggestion"
                })

        return issues


vocabulary_enhancer = VocabularyEnhancer()
