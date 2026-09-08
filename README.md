# GrammaCheck AI — NLP-Powered Grammar & Spell Checking System

An intelligent, full-stack Natural Language Processing (NLP) grammar and spell checking platform inspired by Grammarly. Built in Python with **FastAPI**, **NLTK**, and **SymSpell** on the backend and a modern, responsive web application on the frontend.

---

## 🌟 Key Features

1. **Demonstrative Pronoun Agreement & Copula Checking**:
   - Corrects `"This are a bad sentence."` $\rightarrow$ `"This is a bad sentence."`
   - Corrects `"These is"` $\rightarrow$ `"These are"`, `"That are"` $\rightarrow$ `"That is"`.

2. **Spelling Correction**:
   - High-speed SymSpell frequency lookup + curated dictionary for common misspellings (`recieve` $\rightarrow$ `receive`, `definately` $\rightarrow$ `definitely`, `freind` $\rightarrow$ `friend`).
   - Contraction restorer (`dont` $\rightarrow$ `don't`, `cant` $\rightarrow$ `can't`, `wont` $\rightarrow$ `won't`).
   - **Custom User Dictionary**: Add any custom word to your local dictionary so it is never flagged again.

3. **Grammar & Subject-Verb Agreement (SVA)**:
   - 3rd person singular agreement (`She go to college` $\rightarrow$ `She goes to college`).
   - Plural noun agreement (`The students is ready` $\rightarrow$ `The students are ready`).
   - Irregular plural noun agreement (`People is` $\rightarrow$ `People are`).
   - Article usage phonetics (`a apple` $\rightarrow$ `an apple`, `an university` $\rightarrow$ `a university`).
   - Preposition correctness (`interested on` $\rightarrow$ `interested in`, `different than` $\rightarrow$ `different from`).

4. **Punctuation & Formatting**:
   - Introductory adverbial commas (`However the result was good` $\rightarrow$ `However, the result was good.`).
   - Capitalization at sentence beginnings.
   - Missing terminal periods and punctuation spacing.

5. **Context-Aware Homophone Corrections**:
   - `two` vs `to` vs `too` (`I went two the market` $\rightarrow$ `I went to the market`).
   - `their` vs `there` vs `they're`.
   - `your` vs `you're`.
   - `its` vs `it's`.
   - `loose` vs `lose`, `affect` vs `effect`, `accept` vs `except`, `than` vs `then`.

6. **Sentence Structure & Fragment Detection**:
   - Subordinate clause fragments (`Because he was tired.` $\rightarrow$ Fragment alert).
   - Missing main finite verbs.

7. **Vocabulary & Word Choice**:
   - Overused intensifiers to evocative vocabulary (`The results were very bad` $\rightarrow$ `The results were disappointing`).

8. **Style, Clarity & Conciseness**:
   - Eliminates wordiness (`Due to the fact that` $\rightarrow$ `Because`, `In order to` $\rightarrow$ `To`, `At this point in time` $\rightarrow$ `Currently`).

9. **Tone & Readability Analysis**:
   - Evaluates tone (Formal, Casual, Professional, Academic).
   - Professional rewrites (`Hey, what's up with the report?` $\rightarrow$ `Could you please provide an update on the report?`).
   - Flesch Reading Ease score, Flesch-Kincaid Grade Level, and estimated Reading/Speaking times.

10. **Interactive Actions**:
    - **Accept Suggestion**: One-click apply replacement in the editor.
    - **Ignore**: Dismiss issue from current session.
    - **Add to Dictionary**: Persist custom vocabulary.
    - **Copy Text**: Copy original input.
    - **Copy Corrected Text**: Copy the full corrected preview.
    - **Clear Text**: Clean slate.
    - **Light ☀️ / Dark 🌙 Theme Toggle**.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Server
```bash
python run_server.py
```
Open your browser and visit: **`http://127.0.0.1:8000`**

---

## 🧪 Running Automated Tests

Run the full NLP engine test suite:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## 📐 Architecture Overview

```
User Input (Web UI)
    │
    ▼
FastAPI Backend (POST /api/check)
    │
    ├─► Preprocessor (Tokens, Offsets, POS Tagging)
    ├─► Spell Checker (SymSpell + Curated Misspellings + User Dict)
    ├─► Grammar Checker (SVA, Demonstratives, Articles, Prepositions)
    ├─► Punctuation Checker (Intro commas, Capitalization, Spacing)
    ├─► Context Checker (Homophones: two/to/too, their/there/they're)
    ├─► Sentence Structure (Fragments, Run-ons)
    ├─► Vocabulary Enhancer (Weak intensifiers)
    ├─► Style & Tone Analyzer (Conciseness, Professional rewrites)
    ├─► Readability & Accuracy Calculator (Flesch scores, % Accuracy)
    │
    ▼
JSON Response -> Rendered dynamically in Web UI
```
