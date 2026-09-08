"""
Text Preprocessor Module
Handles tokenization with exact character offsets, sentence segmentation,
and Part-of-Speech (POS) tagging.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional
import nltk
from nltk import pos_tag


@dataclass
class Token:
    text: str
    start: int
    end: int
    pos: str = ""
    lemma: str = ""
    is_word: bool = True
    sentence_idx: int = 0
    token_idx: int = 0

    @property
    def lower(self) -> str:
        return self.text.lower()


@dataclass
class Sentence:
    text: str
    start: int
    end: int
    index: int
    tokens: List[Token] = field(default_factory=list)


@dataclass
class ProcessedDocument:
    raw_text: str
    sentences: List[Sentence] = field(default_factory=list)
    tokens: List[Token] = field(default_factory=list)


class Preprocessor:
    def __init__(self):
        # Ensure NLTK models are accessible
        try:
            nltk.data.find("taggers/averaged_perceptron_tagger_eng")
        except LookupError:
            try:
                nltk.download("averaged_perceptron_tagger_eng", quiet=True)
                nltk.download("averaged_perceptron_tagger", quiet=True)
            except Exception:
                pass

    def process(self, text: str) -> ProcessedDocument:
        doc = ProcessedDocument(raw_text=text)
        if not text:
            return doc

        # Sentence segmentation with character offsets
        # Match sentences ending with ., !, ? or newline sequences
        sent_spans = []
        pattern = re.compile(r'[^.!?\n]+(?:[.!?]+|\n+|$)', re.DOTALL)
        for m in pattern.finditer(text):
            s_text = m.group(0)
            if s_text.strip():
                # Trim boundary whitespace but maintain precise start/end
                l_strip = len(s_text) - len(s_text.lstrip())
                r_strip = len(s_text) - len(s_text.rstrip())
                s_start = m.start() + l_strip
                s_end = m.end() - r_strip
                if s_start < s_end:
                    sent_spans.append((s_start, s_end, text[s_start:s_end]))

        if not sent_spans and text.strip():
            sent_spans = [(0, len(text), text)]

        all_tokens: List[Token] = []
        sentences: List[Sentence] = []

        for s_idx, (s_start, s_end, s_raw) in enumerate(sent_spans):
            sentence = Sentence(text=s_raw, start=s_start, end=s_end, index=s_idx)

            # Tokenize words, contractions, and punctuation with offsets
            # Regex captures words with internal apostrophes/hyphens, numbers, or standalone punctuation
            token_pattern = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)?|\d+(?:\.\d+)?|[^\s\w]", re.UNICODE)
            sent_tokens: List[Token] = []
            
            raw_words = []
            word_tokens_meta = []

            for t_idx, match in enumerate(token_pattern.finditer(s_raw)):
                t_str = match.group(0)
                abs_start = s_start + match.start()
                abs_end = s_start + match.end()
                is_w = bool(re.match(r"^[A-Za-z]+(?:['’][A-Za-z]+)?$", t_str))

                tok = Token(
                    text=t_str,
                    start=abs_start,
                    end=abs_end,
                    is_word=is_w,
                    sentence_idx=s_idx,
                    token_idx=len(sent_tokens)
                )
                sent_tokens.append(tok)
                if is_w:
                    raw_words.append(t_str)
                    word_tokens_meta.append(tok)

            # Perform POS tagging on sentence word tokens
            if raw_words:
                try:
                    tagged = pos_tag(raw_words)
                    for tok_meta, (_, tag) in zip(word_tokens_meta, tagged):
                        tok_meta.pos = tag
                except Exception:
                    # Fallback basic POS tagging
                    for tok_meta in word_tokens_meta:
                        tok_meta.pos = self._fallback_pos(tok_meta.text)

            sentence.tokens = sent_tokens
            sentences.append(sentence)
            all_tokens.extend(sent_tokens)

        doc.sentences = sentences
        doc.tokens = all_tokens
        return doc

    def _fallback_pos(self, word: str) -> str:
        w = word.lower()
        if w in {"the", "a", "an"}:
            return "DT"
        if w in {"is", "am", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "go", "goes", "went"}:
            return "VB"
        if w in {"he", "she", "it", "they", "we", "i", "you", "this", "that", "these", "those"}:
            return "PRP"
        if w in {"in", "on", "at", "to", "for", "with", "by", "about", "from"}:
            return "IN"
        if w in {"and", "but", "or", "because", "although", "since"}:
            return "CC"
        return "NN"


preprocessor = Preprocessor()
