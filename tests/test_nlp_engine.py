"""
Automated Test Suite for NLP Grammar & Spell Checking System
Tests all 9 core requirements and specific user test cases.
"""

import unittest
from backend.engine.pipeline import nlp_pipeline
from backend.engine.user_dictionary import user_dict


class TestGrammarCheckerNLP(unittest.TestCase):

    def test_this_are_a_bad_sentence(self):
        """Test Case: 'This are a bad sentence.' -> 'This is a bad sentence.'"""
        text = "This are a bad sentence."
        res = nlp_pipeline.analyze(text)
        self.assertTrue(len(res["issues"]) > 0, "Should detect issue in 'This are a bad sentence.'")
        
        # Verify issue details
        found_sva = any(iss["original"].lower() == "are" and iss["replacement"].lower() == "is" for iss in res["issues"])
        self.assertTrue(found_sva, "Should suggest replacing 'are' with 'is'")
        
        # Verify corrected text
        self.assertEqual(res["corrected_text"], "This is a bad sentence.")
        self.assertTrue(0 <= res["statistics"]["accuracy_percentage"] < 100)

    def test_spelling_correction(self):
        """Test Case 1: Detect misspelled words like 'recieve' -> 'receive'"""
        text = "I will recieve the package tommorow."
        res = nlp_pipeline.analyze(text)
        issues = res["issues"]
        
        origs = [iss["original"].lower() for iss in issues]
        self.assertIn("recieve", origs)
        self.assertIn("tommorow", origs)
        
        rep_dict = {iss["original"].lower(): iss["replacement"].lower() for iss in issues}
        self.assertEqual(rep_dict.get("recieve"), "receive")
        self.assertEqual(rep_dict.get("tommorow"), "tomorrow")
        self.assertEqual(res["corrected_text"], "I will receive the package tomorrow.")

    def test_grammar_verb_form(self):
        """Test Case 2: 'She go to college' -> 'She goes to college'"""
        text = "She go to college."
        res = nlp_pipeline.analyze(text)
        issues = res["issues"]
        found = any(iss["original"] == "go" and iss["replacement"] == "goes" for iss in issues)
        self.assertTrue(found, "Should correct 'She go' to 'She goes'")
        self.assertEqual(res["corrected_text"], "She goes to college.")

    def test_punctuation_introductory_comma(self):
        """Test Case 3: 'However the result was good' -> 'However, the result was good.'"""
        text = "However the result was good."
        res = nlp_pipeline.analyze(text)
        issues = res["issues"]
        found = any("however" in iss["original"].lower() and "however," in iss["replacement"].lower() for iss in issues)
        self.assertTrue(found, "Should suggest comma after introductory 'However'")
        self.assertIn("However, the result was good.", res["corrected_text"])

    def test_subject_verb_agreement(self):
        """Test Case 4: 'The students is ready' -> 'The students are ready'"""
        text = "The students is ready."
        res = nlp_pipeline.analyze(text)
        issues = res["issues"]
        found = any(iss["original"] == "is" and iss["replacement"] == "are" for iss in issues)
        self.assertTrue(found, "Should correct 'students is' to 'students are'")
        self.assertEqual(res["corrected_text"], "The students are ready.")

    def test_sentence_structure_fragment(self):
        """Test Case 5: 'Because he was tired.' -> Sentence fragment"""
        text = "Because he was tired."
        res = nlp_pipeline.analyze(text)
        issues = res["issues"]
        found = any(iss["category"] == "Structure" for iss in issues)
        self.assertTrue(found, "Should detect sentence fragment starting with 'Because'")

    def test_context_aware_correction(self):
        """Test Case 6: 'I went two the market' -> 'I went to the market'"""
        text = "I went two the market."
        res = nlp_pipeline.analyze(text)
        issues = res["issues"]
        found = any(iss["original"] == "two" and iss["replacement"] == "to" for iss in issues)
        self.assertTrue(found, "Should replace contextual homophone 'two' with 'to'")
        self.assertEqual(res["corrected_text"], "I went to the market.")

    def test_vocabulary_word_choice(self):
        """Test Case 7: 'The results were very bad' -> 'The results were disappointing'"""
        text = "The results were very bad."
        res = nlp_pipeline.analyze(text)
        issues = res["issues"]
        found = any("very bad" in iss["original"].lower() and "disappointing" in iss["replacement"].lower() for iss in issues)
        self.assertTrue(found, "Should suggest replacing 'very bad' with 'disappointing'")

    def test_style_conciseness(self):
        """Test Case 8: 'Due to the fact that' -> 'Because'"""
        text = "Due to the fact that it was raining, we stayed inside."
        res = nlp_pipeline.analyze(text)
        issues = res["issues"]
        found = any("due to the fact that" in iss["original"].lower() and "because" in iss["replacement"].lower() for iss in issues)
        self.assertTrue(found, "Should simplify 'Due to the fact that' to 'Because'")

    def test_readability_and_tone(self):
        """Test Case 9: Readability & Tone analysis"""
        text = "Hey, what's up with the report? Let me know ASAP."
        res = nlp_pipeline.analyze(text)
        self.assertIn("tone_analysis", res)
        self.assertIn("statistics", res)
        self.assertEqual(res["tone_analysis"]["formality"], "Casual / Conversational")
        self.assertTrue(res["statistics"]["word_count"] > 0)

    def test_custom_user_dictionary(self):
        """Test custom dictionary persistence and ignoring"""
        custom_word = "NeuroLinguisticsX"
        user_dict.add_word(custom_word)
        self.assertTrue(user_dict.contains(custom_word))
        
        text = f"We are studying {custom_word} today."
        res = nlp_pipeline.analyze(text)
        # Should not flag the custom word as spelling error
        found = any(iss["original"] == custom_word for iss in res["issues"])
        self.assertFalse(found, "Custom dictionary word should not be flagged as an error")
        
        # Clean up
        user_dict.remove_word(custom_word)


if __name__ == "__main__":
    unittest.main()
