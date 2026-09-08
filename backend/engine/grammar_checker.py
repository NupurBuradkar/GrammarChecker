"""
Grammar Checker Module
Handles Subject-Verb Agreement (SVA), Demonstrative agreement ("This are" -> "This is"),
Article usage (a/an), Verb forms, Prepositions, and Uncountable noun agreements.
"""

import re
from typing import List, Dict
from .preprocessor import ProcessedDocument, Sentence, Token


DEMONSTRATIVE_RULES = [
    # (pattern_regex, original_target, replacement, explanation, rule_id)
    (r"\b(this)\s+(are)\b", 2, "is", 'The singular demonstrative "this" requires the singular verb "is".', "SVA_DEMONSTRATIVE_THIS_ARE"),
    (r"\b(that)\s+(are)\b", 2, "is", 'The singular demonstrative "that" requires the singular verb "is".', "SVA_DEMONSTRATIVE_THAT_ARE"),
    (r"\b(these)\s+(is)\b", 2, "are", 'The plural demonstrative "these" requires the plural verb "are".', "SVA_DEMONSTRATIVE_THESE_IS"),
    (r"\b(those)\s+(is)\b", 2, "are", 'The plural demonstrative "those" requires the plural verb "are".', "SVA_DEMONSTRATIVE_THOSE_IS"),
    (r"\b(this)\s+(were)\b", 2, "was", 'The singular demonstrative "this" requires the singular past verb "was".', "SVA_DEMONSTRATIVE_THIS_WERE"),
    (r"\b(that)\s+(were)\b", 2, "was", 'The singular demonstrative "that" requires the singular past verb "was".', "SVA_DEMONSTRATIVE_THAT_WERE"),
    (r"\b(these)\s+(was)\b", 2, "were", 'The plural demonstrative "these" requires the plural past verb "were".', "SVA_DEMONSTRATIVE_THESE_WAS"),
    (r"\b(those)\s+(was)\b", 2, "were", 'The plural demonstrative "those" requires the plural past verb "were".', "SVA_DEMONSTRATIVE_THOSE_WAS"),
    (r"\b(this)\s+(have)\b", 2, "has", 'The singular demonstrative "this" requires "has".', "SVA_DEMONSTRATIVE_THIS_HAVE"),
    (r"\b(that)\s+(have)\b", 2, "has", 'The singular demonstrative "that" requires "has".', "SVA_DEMONSTRATIVE_THAT_HAVE"),
    (r"\b(these)\s+(has)\b", 2, "have", 'The plural demonstrative "these" requires "have".', "SVA_DEMONSTRATIVE_THESE_HAS"),
    (r"\b(those)\s+(has)\b", 2, "have", 'The plural demonstrative "those" requires "have".', "SVA_DEMONSTRATIVE_THOSE_HAS"),
]

BASE_TO_THIRD = {
    "go": "goes", "do": "does", "have": "has", "be": "is", "say": "says",
    "try": "tries", "study": "studies", "carry": "carries", "fly": "flies",
    "watch": "watches", "wash": "washes", "fix": "fixes", "pass": "passes",
    "miss": "misses", "teach": "teaches", "catch": "catches", "push": "pushes",
    "finish": "finishes", "make": "makes", "take": "takes", "come": "comes",
    "run": "runs", "need": "needs", "want": "wants", "like": "likes",
    "love": "loves", "work": "works", "help": "helps", "play": "plays",
    "know": "knows", "think": "thinks", "look": "looks", "seem": "seems",
    "feel": "feels", "leave": "leaves", "call": "calls", "ask": "asks",
    "write": "writes", "read": "reads", "give": "gives", "find": "finds",
    "tell": "tells", "become": "becomes", "show": "shows", "hear": "hears",
    "stand": "stands", "lose": "loses", "pay": "pays", "meet": "meets",
    "include": "includes", "continue": "continues", "set": "sets",
    "learn": "learns", "change": "changes", "lead": "leads", "understand": "understands",
    "follow": "follows", "stop": "stops", "create": "creates", "speak": "speaks",
    "allow": "allows", "add": "adds", "spend": "spends", "grow": "grows",
    "open": "opens", "walk": "walks", "win": "wins", "offer": "offers",
    "remember": "remembers", "consider": "considers", "appear": "appears",
    "buy": "buys", "serve": "serves", "die": "dies", "send": "sends",
    "expect": "expects", "build": "builds", "stay": "stays", "fall": "falls",
    "cut": "cuts", "reach": "reaches", "kill": "kills", "remain": "remains"
}

THIRD_TO_BASE = {v: k for k, v in BASE_TO_THIRD.items()}

IRREGULAR_PAST = {
    "go": "went", "buy": "bought", "come": "came", "see": "saw", "eat": "ate",
    "drink": "drank", "run": "ran", "sit": "sat", "stand": "stood", "write": "wrote",
    "read": "read", "take": "took", "make": "made", "say": "said", "tell": "told",
    "get": "got", "give": "gave", "find": "found", "think": "thought", "bring": "brought",
    "teach": "taught", "catch": "caught", "sleep": "slept", "leave": "left",
    "feel": "felt", "keep": "kept", "speak": "spoke", "drive": "drove", "choose": "chose",
    "begin": "began", "break": "broke", "forget": "forgot", "know": "knew",
    "have": "had", "do": "did", "be": "was", "are": "were", "is": "was"
}

UNCOUNTABLE_NOUNS = {
    "evidences": "evidence",
    "informations": "information",
    "advices": "advice",
    "equipments": "equipment",
    "researches": "research",
    "furnitures": "furniture",
    "luggages": "luggage",
    "softwares": "software",
    "homeworks": "homework",
    "feedbacks": "feedback",
    "knowledges": "knowledge",
    "traffics": "traffic"
}

COMMON_PREPOSITION_FIXES = [
    (r"\binterested\s+on\b", "interested in", 'Use "interested in" rather than "interested on".', "PREP_INTERESTED_IN"),
    (r"\bdepend\s+of\b", "depend on", 'Use "depend on" rather than "depend of".', "PREP_DEPEND_ON"),
    (r"\bdepends\s+of\b", "depends on", 'Use "depends on" rather than "depends of".', "PREP_DEPENDS_ON"),
    (r"\bdepended\s+of\b", "depended on", 'Use "depended on" rather than "depended of".', "PREP_DEPENDED_ON"),
    (r"\bdifferent\s+than\b", "different from", 'In standard English, use "different from".', "PREP_DIFFERENT_FROM"),
    (r"\bgood\s+in\s+(math|mathematics|english|science|sports|art|music|chess)\b", r"good at \1", 'Use "good at" when referring to skills or subjects.', "PREP_GOOD_AT"),
    (r"\bcongratulate\s+(?:him|her|them|me|us|you)\s+for\b", "congratulate on", 'Use "congratulate [someone] on [something]".', "PREP_CONGRATULATE_ON"),
    (r"\binsist\s+to\b", "insist on", 'Use "insist on" instead of "insist to".', "PREP_INSIST_ON"),
    (r"\blook\s+forward\s+to\s+meet\b", "look forward to meeting", 'Use the gerund "meeting" after the phrasal verb "look forward to".', "VERB_LOOK_FORWARD_TO_GERUND"),
    (r"\blooking\s+forward\s+to\s+meet\b", "looking forward to meeting", 'Use the gerund "meeting" after "looking forward to".', "VERB_LOOK_FORWARD_TO_GERUND"),
    (r"\bcapable\s+to\b", "capable of", 'Use "capable of" instead of "capable to".', "PREP_CAPABLE_OF"),
    (r"\bprefer\s+([^,\s]+)\s+than\s+([^,\s]+)\b", r"prefer \1 to \2", 'Use "prefer [X] to [Y]" rather than "than".', "PREP_PREFER_TO"),
    (r"\bmarried\s+with\b", "married to", 'Use "married to" rather than "married with".', "PREP_MARRIED_TO"),
    (r"\bdiscuss\s+about\b", "discuss", '"Discuss" already means "talk about"; omit "about".', "PREP_DISCUSS_ABOUT"),
    (r"\bdiscusses\s+about\b", "discusses", 'Omit "about" after "discusses".', "PREP_DISCUSSES_ABOUT"),
    (r"\bdiscussed\s+about\b", "discussed", 'Omit "about" after "discussed".', "PREP_DISCUSSED_ABOUT"),
]


class GrammarChecker:
    def __init__(self):
        pass

    def check(self, doc: ProcessedDocument) -> list:
        issues = []
        raw_text = doc.raw_text

        # 1. Demonstrative Pronoun + Verb Agreement ("This are" -> "This is")
        self._check_demonstratives(raw_text, issues)

        # 2. Subject-Verb Agreement (SVA) & 3rd Person Singular
        self._check_subject_verb_agreement(doc, issues)

        # 3. Articles (a vs an)
        self._check_articles(doc, issues)

        # 4. Uncountable Nouns
        self._check_uncountable_nouns(doc, issues)

        # 5. Prepositions & Phrasal Idioms
        self._check_prepositions(raw_text, issues)

        # 6. Past Tense Temporal Indicators + Present Verbs
        self._check_past_tense_consistency(doc, issues)

        return issues

    def _check_demonstratives(self, text: str, issues: list):
        for pattern, verb_group, rep, explanation, rule_id in DEMONSTRATIVE_RULES:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                # Target the verb specifically or the pair
                full_match = m.group(0)
                verb_str = m.group(verb_group)
                # Offset of verb within full match
                verb_offset = m.start() + full_match.lower().rfind(verb_str.lower())
                
                # Casing
                rep_cased = rep.upper() if verb_str.isupper() else (rep.capitalize() if verb_str[0].isupper() else rep)
                
                issues.append({
                    "start": verb_offset,
                    "end": verb_offset + len(verb_str),
                    "original": verb_str,
                    "replacement": rep_cased,
                    "category": "Grammar",
                    "rule_id": rule_id,
                    "message": f'Subject-verb agreement error: "{m.group(1)} {verb_str}".',
                    "explanation": explanation,
                    "severity": "error"
                })

    def _check_subject_verb_agreement(self, doc: ProcessedDocument, issues: list):
        for sent in doc.sentences:
            words = [t for t in sent.tokens if t.is_word]
            n = len(words)
            if n < 2:
                continue

            for i in range(n - 1):
                t1 = words[i]
                t2 = words[i + 1]
                w1 = t1.lower
                w2 = t2.lower

                # 3rd Person Singular Pronoun + Base Verb (e.g. "She go to college" -> "She goes")
                if w1 in {"he", "she", "it", "someone", "everyone", "anybody", "nobody", "everybody"}:
                    if w2 in BASE_TO_THIRD and w2 not in {"can", "could", "will", "would", "shall", "should", "may", "might", "must"}:
                        # Skip if preceded by modal (e.g. "can he go")
                        prev_w = words[i - 1].lower if i > 0 else ""
                        if prev_w in {"can", "could", "will", "would", "shall", "should", "may", "might", "must", "did", "does", "do"}:
                            continue
                        
                        target_verb = BASE_TO_THIRD[w2]
                        rep = target_verb.upper() if t2.text.isupper() else (target_verb.capitalize() if t2.text[0].isupper() else target_verb)
                        issues.append({
                            "start": t2.start,
                            "end": t2.end,
                            "original": t2.text,
                            "replacement": rep,
                            "category": "Grammar",
                            "rule_id": "SVA_SINGULAR_PRONOUN_VERB",
                            "message": f'Third-person singular subject "{t1.text}" requires verb "{rep}".',
                            "explanation": f'The singular subject "{t1.text}" requires the third-person singular verb form "{rep}" rather than "{t2.text}".',
                            "severity": "error"
                        })

                # Plural Pronoun + 3rd Person Singular Verb (e.g. "They goes" -> "They go", "We has" -> "We have")
                elif w1 in {"they", "we", "you", "i"}:
                    if w2 in THIRD_TO_BASE and w1 != "he" and w1 != "she" and w1 != "it":
                        target_verb = THIRD_TO_BASE[w2]
                        rep = target_verb.upper() if t2.text.isupper() else (target_verb.capitalize() if t2.text[0].isupper() else target_verb)
                        issues.append({
                            "start": t2.start,
                            "end": t2.end,
                            "original": t2.text,
                            "replacement": rep,
                            "category": "Grammar",
                            "rule_id": "SVA_PLURAL_PRONOUN_VERB",
                            "message": f'Pronoun "{t1.text}" requires base verb "{rep}".',
                            "explanation": f'The subject "{t1.text}" takes the base verb form "{rep}" instead of "{t2.text}".',
                            "severity": "error"
                        })

                # Plural Subject Noun + Singular Copula/Verb (e.g. "The students is ready" -> "The students are ready")
                if w1.endswith("s") and len(w1) > 3 and not w1.endswith("ss") and not w1.endswith("us") and not w1.endswith("is"):
                    # w1 is likely plural noun (students, teachers, cars, reports, children, people)
                    if w2 in {"is", "was", "has", "does"}:
                        mapping = {"is": "are", "was": "were", "has": "have", "does": "do"}
                        rep = mapping[w2]
                        rep_cased = rep.upper() if t2.text.isupper() else (rep.capitalize() if t2.text[0].isupper() else rep)
                        issues.append({
                            "start": t2.start,
                            "end": t2.end,
                            "original": t2.text,
                            "replacement": rep_cased,
                            "category": "Grammar",
                            "rule_id": "SVA_PLURAL_NOUN_SINGULAR_VERB",
                            "message": f'Plural subject "{t1.text}" requires plural verb "{rep_cased}".',
                            "explanation": f'The noun "{t1.text}" is plural, so the verb must agree in plural form ("{rep_cased}").',
                            "severity": "error"
                        })

                # Special plural irregular nouns (people, children, men, women, criteria, phenomena)
                if w1 in {"people", "children", "men", "women", "criteria", "phenomena"}:
                    if w2 in {"is", "was", "has", "does"}:
                        mapping = {"is": "are", "was": "were", "has": "have", "does": "do"}
                        rep = mapping[w2]
                        rep_cased = rep.upper() if t2.text.isupper() else (rep.capitalize() if t2.text[0].isupper() else rep)
                        issues.append({
                            "start": t2.start,
                            "end": t2.end,
                            "original": t2.text,
                            "replacement": rep_cased,
                            "category": "Grammar",
                            "rule_id": "SVA_IRREGULAR_PLURAL_NOUN",
                            "message": f'Plural noun "{t1.text}" requires plural verb "{rep_cased}".',
                            "explanation": f'"{t1.text}" is an irregular plural noun and requires the plural verb "{rep_cased}".',
                            "severity": "error"
                        })

                # Singular Noun + Plural Copula (e.g. "The student are ready" -> "The student is ready")
                # When t1 is singular noun (not ending in s, not pronoun, tagged NN or preceded by 'the'/'a'/'this')
                if i > 0 and words[i - 1].lower in {"the", "a", "an", "this", "that", "my", "your", "his", "her", "our"} and not w1.endswith("s"):
                    if w2 in {"are", "were"}:
                        mapping = {"are": "is", "were": "was"}
                        rep = mapping[w2]
                        rep_cased = rep.upper() if t2.text.isupper() else (rep.capitalize() if t2.text[0].isupper() else rep)
                        issues.append({
                            "start": t2.start,
                            "end": t2.end,
                            "original": t2.text,
                            "replacement": rep_cased,
                            "category": "Grammar",
                            "rule_id": "SVA_SINGULAR_NOUN_PLURAL_VERB",
                            "message": f'Singular subject "{t1.text}" requires singular verb "{rep_cased}".',
                            "explanation": f'The subject "{t1.text}" is singular, so use the singular verb form "{rep_cased}".',
                            "severity": "error"
                        })

    def _check_articles(self, doc: ProcessedDocument, issues: list):
        for sent in doc.sentences:
            words = [t for t in sent.tokens if t.is_word]
            for i in range(len(words) - 1):
                art_tok = words[i]
                next_tok = words[i + 1]
                art = art_tok.lower
                next_w = next_tok.lower

                if art not in {"a", "an"}:
                    continue

                # Vowel sound vs Consonant sound phonetic check
                # Exceptions where 'u' / 'e' sounds like consonant 'y' (/juː/)
                consonant_sounding_vowels = re.compile(r"^(uni|user|useful|use|usual|ubiquitous|european|one|euphemism)", re.IGNORECASE)
                # Exceptions where silent 'h' sounds like vowel (/aʊər/, /ɒnɪst/)
                vowel_sounding_h = re.compile(r"^(honest|honour|honor|hour|heir|herb)", re.IGNORECASE)

                starts_with_vowel_letter = bool(re.match(r"^[aeiou]", next_w))
                
                is_vowel_sound = False
                if starts_with_vowel_letter:
                    is_vowel_sound = not bool(consonant_sounding_vowels.match(next_w))
                elif vowel_sounding_h.match(next_w):
                    is_vowel_sound = True

                needed = "an" if is_vowel_sound else "a"
                if art != needed:
                    rep = needed.upper() if art_tok.text.isupper() else (needed.capitalize() if art_tok.text[0].isupper() else needed)
                    issues.append({
                        "start": art_tok.start,
                        "end": art_tok.end,
                        "original": art_tok.text,
                        "replacement": rep,
                        "category": "Grammar",
                        "rule_id": "ARTICLE_A_AN",
                        "message": f'Use article "{rep}" before "{next_tok.text}".',
                        "explanation": f'Use "{rep}" before words starting with a {"vowel" if is_vowel_sound else "consonant"} sound.',
                        "severity": "error"
                    })

    def _check_uncountable_nouns(self, doc: ProcessedDocument, issues: list):
        for tok in doc.tokens:
            if not tok.is_word:
                continue
            w = tok.lower
            if w in UNCOUNTABLE_NOUNS:
                rep = UNCOUNTABLE_NOUNS[w]
                rep_cased = rep.upper() if tok.text.isupper() else (rep.capitalize() if tok.text[0].isupper() else rep)
                issues.append({
                    "start": tok.start,
                    "end": tok.end,
                    "original": tok.text,
                    "replacement": rep_cased,
                    "category": "Grammar",
                    "rule_id": "UNCOUNTABLE_NOUN_PLURAL",
                    "message": f'"{tok.text}" is an uncountable noun.',
                    "explanation": f'"{tok.text}" is normally uncountable in standard English; use "{rep_cased}".',
                    "severity": "error"
                })

    def _check_prepositions(self, text: str, issues: list):
        for pattern, replacement, explanation, rule_id in COMMON_PREPOSITION_FIXES:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                # Expand backreferences if any
                rep = m.expand(replacement)
                issues.append({
                    "start": m.start(),
                    "end": m.end(),
                    "original": m.group(0),
                    "replacement": rep,
                    "category": "Grammar",
                    "rule_id": rule_id,
                    "message": f'Incorrect preposition or phrasing: "{m.group(0)}".',
                    "explanation": explanation,
                    "severity": "error"
                })

    def _check_past_tense_consistency(self, doc: ProcessedDocument, issues: list):
        past_markers = {"yesterday", "last", "ago", "previously", "earlier", "formerly"}
        for sent in doc.sentences:
            words = [t for t in sent.tokens if t.is_word]
            has_past_marker = any(t.lower in past_markers for t in words)
            if not has_past_marker:
                continue

            for t in words:
                w = t.lower
                if w in IRREGULAR_PAST and w not in {"have", "do", "be", "are", "is", "read"}:
                    # If preceded by 'to' (infinitive) or modal, skip
                    idx = words.index(t)
                    prev_w = words[idx - 1].lower if idx > 0 else ""
                    if prev_w in {"to", "did", "didn't", "could", "would", "should", "will", "might", "can"}:
                        continue
                    
                    past_rep = IRREGULAR_PAST[w]
                    rep_cased = past_rep.upper() if t.text.isupper() else (past_rep.capitalize() if t.text[0].isupper() else past_rep)
                    issues.append({
                        "start": t.start,
                        "end": t.end,
                        "original": t.text,
                        "replacement": rep_cased,
                        "category": "Grammar",
                        "rule_id": "PAST_TENSE_TIME_MARKER",
                        "message": f'Past time marker indicates past tense verb "{rep_cased}".',
                        "explanation": f'Because this sentence refers to a past time, use the past tense "{rep_cased}" instead of "{t.text}".',
                        "severity": "error"
                    })


grammar_checker = GrammarChecker()
