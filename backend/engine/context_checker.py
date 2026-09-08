"""
Context-Aware Checker Module
Identifies homophones and confusable words in context:
- two / to / too ("I went two the market" -> "I went to the market")
- their / there / they're
- your / you're
- its / it's
- loose / lose
- accept / except
- affect / effect
- than / then
- weather / whether
- peace / piece
- principal / principle
"""

import re
from typing import List
from .preprocessor import ProcessedDocument, Token


CONTEXTUAL_RULES = [
    # two / to / too
    (r"\b(went|go|going|gone|walked|ran|drove|traveled|travelled|flew|heading|sent|welcome|listen|listening|looking|talk|talking)\s+(two)\s+(the|a|an|my|your|his|her|our|their|school|work|home|college|market|store|bed|sleep|hospital)\b",
     2, "to", 'In this context, the preposition "to" indicates direction, not the number "two".', "CONTEXT_TWO_TO"),

    (r"\b(two)\s+(much|many|late|early|hot|cold|fast|slow|hard|soft|expensive|cheap|far|close|tired|busy|small|big|large|heavy|easy|difficult|good|bad)\b",
     1, "too", 'Use the adverb "too" (meaning excessively or also) instead of the numeral "two".', "CONTEXT_TWO_TOO"),

    (r"\b(me|you|us|them|him|her)\s+(to)\s*(?:[.,!?]|$)",
     2, "too", 'Use "too" to mean "also" or "as well".', "CONTEXT_ME_TO_TOO"),

    # their / there / they're
    (r"\b(their)\s+(going|coming|leaving|arriving|doing|making|working|running|trying|waiting|ready|right|wrong|here|there|not|also|always|often|very|excited|happy|sad|tired|busy)\b",
     1, "they're", 'Use "they\'re" (contraction of "they are") before verbs or adjectives.', "CONTEXT_THEIR_THEYRE"),

    (r"\b(their)\s+(is|are|was|were|will|has|have|had|seems|seemed)\b",
     1, "there", 'Use the expletive/adverb "there" with forms of the verb "to be".', "CONTEXT_THEIR_THERE"),

    (r"\b(there|they're)\s+(house|car|car|dog|cat|books|room|friends|family|father|mother|parents|boss|teacher|job|office|children|money|idea|opinions|effort|efforts|work|project|team)\b",
     1, "their", 'Use the possessive pronoun "their" before nouns showing ownership.', "CONTEXT_THERE_THEIR"),

    (r"\b(over|out|in|up|down|back|stay|staying|live|living|went|stood|standing)\s+(their)\b",
     2, "there", 'Use "there" to indicate a place or direction.', "CONTEXT_OVER_THEIR_THERE"),

    # your / you're
    (r"\b(your)\s+(welcome|right|wrong|going|coming|looking|invited|ready|doing|making|smart|beautiful|handsome|kind|amazing|awesome|late|early)\b",
     1, "you're", 'Use "you\'re" (contraction for "you are") in this context.', "CONTEXT_YOUR_YOURE"),

    (r"\b(you're|youre)\s+(car|house|dog|cat|phone|laptop|book|mother|father|parents|friend|friends|job|account|password|email|name|feedback|opinion|time|turn)\b",
     1, "your", 'Use the possessive adjective "your" before nouns.', "CONTEXT_YOURE_YOUR"),

    # its / it's
    (r"\b(its)\s+(a|an|the|very|really|not|going|been|important|possible|clear|obvious|difficult|easy|true|false|great|good|bad|nice)\b",
     1, "it's", 'Use "it\'s" (short for "it is" or "it has") in this context.', "CONTEXT_ITS_ITS"),

    (r"\b(wagged|wagging|shook|spread|opened|closed|lost|found|cleaned|changed)\s+(it's)\s+(tail|wings|doors|mouth|head|leaves|color|shape|name|value)\b",
     2, "its", 'Use the possessive pronoun "its" (without an apostrophe) to show possession.', "CONTEXT_ITS_POSSESSIVE"),

    # loose / lose
    (r"\b(don't|dont|didn't|didnt|wont|won't|cannot|cant|can't|to|will|might|may|could|would|should)\s+(loose)\b",
     2, "lose", 'Use "lose" (meaning to misplace or be defeated) instead of "loose" (not tight).', "CONTEXT_LOOSE_LOSE"),

    (r"\b(loose)\s+(the|a|an|my|your|his|her|our|their|weight|control|mind|temper|focus|interest|money|game|match|job|hope)\b",
     1, "lose", 'Use "lose" as a verb instead of the adjective "loose".', "CONTEXT_LOOSE_LOSE_VERB"),

    # than / then
    (r"\b(more|less|better|worse|greater|smaller|faster|slower|taller|shorter|higher|lower|older|younger|earlier|later|rather|other)\s+(then)\b",
     2, "than", 'Use the comparative conjunction "than" after comparative adjectives/adverbs.', "CONTEXT_THEN_THAN"),

    (r"\b(and|back|just|since|until|even)\s+(than)\b",
     2, "then", 'Use the adverb "then" to refer to time or consequence.', "CONTEXT_THAN_THEN"),

    # accept / except
    (r"\b(everyone|everybody|all|nobody|no\s+one|nothing|everything)\s+(accept)\b",
     2, "except", 'Use "except" to mean excluding or apart from.', "CONTEXT_ACCEPT_EXCEPT"),

    (r"\b(cannot|can't|cant|will\s+not|wont|won't|refuse\s+to|pleased\s+to|happy\s+to|glad\s+to)\s+(except)\b",
     2, "accept", 'Use the verb "accept" (to receive willingly) instead of "except".', "CONTEXT_EXCEPT_ACCEPT"),

    # affect / effect
    (r"\b(will|would|can|could|might|may|should|shall|to)\s+(effect)\b",
     2, "affect", 'Use "affect" as a verb meaning to influence.', "CONTEXT_EFFECT_AFFECT"),

    (r"\b(a|an|the|significant|positive|negative|major|minor|profound|side|lasting)\s+(affect)\b",
     2, "effect", 'Use "effect" as a noun meaning a result or outcome.', "CONTEXT_AFFECT_EFFECT"),

    # weather / whether
    (r"\b(weather)\s+or\s+not\b",
     1, "whether", 'Use the conjunction "whether" for alternatives; "weather" refers to the climate.', "CONTEXT_WEATHER_WHETHER"),

    (r"\b(know|decide|sure|wonder|wondering|asking|asked|ask|doubt|tell)\s+(weather)\b",
     2, "whether", 'Use the conjunction "whether" after verbs of doubt or decision.', "CONTEXT_WEATHER_WHETHER_VERB"),

    # peace / piece
    (r"\b(a|an|one)\s+(peace)\s+of\b",
     2, "piece", 'Use "piece" for a portion or slice of something.', "CONTEXT_PEACE_PIECE"),

    # principal / principle
    (r"\b(school|high\s+school|elementary|middle\s+school|college)\s+(principle)\b",
     2, "principal", 'The head of a school is a "principal".', "CONTEXT_PRINCIPLE_PRINCIPAL"),

    (r"\b(fundamental|core|guiding|moral|ethical|scientific|basic)\s+(principals)\b",
     2, "principles", 'Use "principles" when referring to fundamental truths or rules.', "CONTEXT_PRINCIPALS_PRINCIPLES"),
]


class ContextChecker:
    def __init__(self):
        pass

    def check(self, doc: ProcessedDocument) -> list:
        issues = []
        raw_text = doc.raw_text

        for pattern, target_group_idx, replacement, explanation, rule_id in CONTEXTUAL_RULES:
            for m in re.finditer(pattern, raw_text, re.IGNORECASE):
                target_str = m.group(target_group_idx)
                # Calculate start and end offset of the target group within m
                start_offset = m.start(target_group_idx)
                end_offset = m.end(target_group_idx)

                # Preserve casing
                rep_cased = replacement.upper() if target_str.isupper() else (replacement.capitalize() if target_str[0].isupper() else replacement)

                issues.append({
                    "start": start_offset,
                    "end": end_offset,
                    "original": target_str,
                    "replacement": rep_cased,
                    "category": "Context",
                    "rule_id": rule_id,
                    "message": f'Contextual word confusion: "{target_str}" should likely be "{rep_cased}".',
                    "explanation": explanation,
                    "severity": "error"
                })

        return issues


context_checker = ContextChecker()
