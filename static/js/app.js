/**
 * GrammaCheck AI - Interactive Client Application
 * Features:
 * - Interactive NLP Writing Workspace with flagged issue Assessment
 * - Document File Upload with Drag & Drop and Instant Success State (Feature #6)
 * - Graphical Performance Report with Readability, Tone & Category Breakdown (Feature #8)
 * - Past Checks History Log with Search, Filter, Reload & Export (Feature #9)
 * - User Authentication (Login, Sign-Up, Demo User)
 * - Custom Dictionary Management and Theme Toggling
 */

"use strict";

(function() {
    // =========================================================
    // DOM Elements Cache
    // =========================================================
    
    // Navigation Tabs & Views
    const navTabs = document.querySelectorAll(".nav-tab");
    const dashboardViews = document.querySelectorAll(".dashboard-view");
    const navHistoryCount = document.getElementById("nav-history-count");
    
    // Editor & Workspace
    const editor = document.getElementById("editor-input");
    const checkBtn = document.getElementById("btn-check");
    const copyBtn = document.getElementById("btn-copy-orig");
    const clearBtn = document.getElementById("btn-clear");
    const saveToHistoryBtn = document.getElementById("btn-save-to-history");
    const copyCorrectedBtn = document.getElementById("btn-copy-corrected");
    const themeToggleBtn = document.getElementById("btn-theme-toggle");
    const sampleSelect = document.getElementById("sample-select");
    const issuesFeed = document.getElementById("issues-feed");
    const previewContent = document.getElementById("preview-content");
    const filterTabsContainer = document.getElementById("filter-tabs");
    
    // Live Word & Char Counters
    const liveWords = document.getElementById("live-words");
    const liveChars = document.getElementById("live-chars");
    
    // Accuracy Gauge (Workspace)
    const scoreNum = document.getElementById("score-num");
    const scoreCircle = document.getElementById("score-circle-progress");
    const scoreTitle = document.getElementById("score-title");
    const scoreBadge = document.getElementById("score-badge");
    const scoreDesc = document.getElementById("score-desc");
    
    // Analytics Metrics (Workspace Footer)
    const statWords = document.getElementById("stat-words");
    const statSentences = document.getElementById("stat-sentences");
    const statReadingTime = document.getElementById("stat-reading-time");
    const statReadability = document.getElementById("stat-readability");
    const statReadabilityGrade = document.getElementById("stat-readability-grade");

    // Performance Report Elements (Feature #8)
    const perfScoreNum = document.getElementById("perf-score-num");
    const perfCircle = document.getElementById("perf-circle-progress");
    const perfScoreBadge = document.getElementById("perf-score-badge");
    const perfQualityTitle = document.getElementById("perf-quality-title");
    const perfQualityDesc = document.getElementById("perf-quality-desc");
    const perfFleschNum = document.getElementById("perf-flesch-num");
    const perfFleschFill = document.getElementById("perf-flesch-fill");
    const perfReadabilityTag = document.getElementById("perf-readability-tag");
    const perfAudienceLevel = document.getElementById("perf-audience-level");
    const perfAvgSentence = document.getElementById("perf-avg-sentence");
    const perfAvgSyllable = document.getElementById("perf-avg-syllable");
    const perfEstReading = document.getElementById("perf-est-reading");
    const perfTotalIssues = document.getElementById("perf-total-issues");
    const perfToneBadge = document.getElementById("perf-tone-badge");
    const perfToneSummary = document.getElementById("perf-tone-summary");
    const btnRefreshReport = document.getElementById("btn-refresh-report");

    // Category Distribution Bars
    const distSpellVal = document.getElementById("dist-spell-val");
    const distSpellBar = document.getElementById("dist-spell-bar");
    const distGramVal = document.getElementById("dist-gram-val");
    const distGramBar = document.getElementById("dist-gram-bar");
    const distPuncVal = document.getElementById("dist-punc-val");
    const distPuncBar = document.getElementById("dist-punc-bar");
    const distCtxVal = document.getElementById("dist-ctx-val");
    const distCtxBar = document.getElementById("dist-ctx-bar");
    const distStyleVal = document.getElementById("dist-style-val");
    const distStyleBar = document.getElementById("dist-style-bar");

    // Tone Bars (Performance View)
    const perfBarFormal = document.getElementById("perf-bar-formal");
    const perfBarCasual = document.getElementById("perf-bar-casual");
    const perfBarProf = document.getElementById("perf-bar-prof");
    const perfBarAcad = document.getElementById("perf-bar-acad");
    const perfValFormal = document.getElementById("perf-val-formal");
    const perfValCasual = document.getElementById("perf-val-casual");
    const perfValProf = document.getElementById("perf-val-prof");
    const perfValAcad = document.getElementById("perf-val-acad");

    // Document Upload Elements (Feature #6)
    const uploadDropzone = document.getElementById("upload-dropzone");
    const fileUploadInput = document.getElementById("file-upload-input");
    const btnBrowseFile = document.getElementById("btn-browse-file");
    const uploadSuccessCard = document.getElementById("upload-success-card");
    const uploadFilename = document.getElementById("upload-filename");
    const uploadFilesize = document.getElementById("upload-filesize");
    const uploadWordcount = document.getElementById("upload-wordcount");
    const uploadCharcount = document.getElementById("upload-charcount");
    const uploadTimestamp = document.getElementById("upload-timestamp");
    const uploadFileType = document.getElementById("upload-file-type");
    const extractedTextPreview = document.getElementById("extracted-text-preview");
    const btnScanUploaded = document.getElementById("btn-scan-uploaded");
    const btnCopyExtracted = document.getElementById("btn-copy-extracted");
    const btnUploadAnother = document.getElementById("btn-upload-another");

    // History Log Elements (Feature #9)
    const historyListContainer = document.getElementById("history-list-container");
    const historySearchInput = document.getElementById("history-search-input");
    const historyFilterSelect = document.getElementById("history-filter-select");
    const btnClearHistory = document.getElementById("btn-clear-history");

    // Auth & Modal Elements
    const authModal = document.getElementById("auth-modal");
    const btnOpenLogin = document.getElementById("btn-open-login");
    const btnOpenSignup = document.getElementById("btn-open-signup");
    const btnCloseModal = document.getElementById("btn-close-modal");
    const tabModalLogin = document.getElementById("tab-modal-login");
    const tabModalSignup = document.getElementById("tab-modal-signup");
    const formLogin = document.getElementById("form-login");
    const formSignup = document.getElementById("form-signup");
    const loginError = document.getElementById("login-error");
    const signupError = document.getElementById("signup-error");
    const btnQuickDemo = document.getElementById("btn-quick-demo");
    const authGuestControls = document.getElementById("auth-guest-controls");
    const authUserProfile = document.getElementById("auth-user-profile");
    const headerUserAvatar = document.getElementById("header-user-avatar");
    const headerUserName = document.getElementById("header-user-name");
    const headerUserPlan = document.getElementById("header-user-plan");
    const btnLogout = document.getElementById("btn-logout");

    // Toast element
    const toast = document.getElementById("toast-notification");

    // Base URL for API requests (supports HTTP server on 8080/8000 and local file:// access)
    const API_BASE = (window.location.protocol === "file:" || window.location.port === "5500" || window.location.port === "3000") ? "http://127.0.0.1:8080" : "";

    let currentAnalysis = null;
    let activeFilter = "all";
    let debounceTimer = null;
    let currentUser = null;
    let historyItems = [];
    let uploadedFileCache = null;

    // Example Test Sentences
    const SAMPLES = {
        "this_are": "This are a bad sentence.",
        "spelling": "I will recieve the package tommorow morning.",
        "grammar_sva": "She go to college every day and the students is ready for the exam.",
        "punctuation": "However the result was good and everyone was happy",
        "context_homophones": "I went two the market to buy there vegetables, but it was two late.",
        "vocabulary_style": "The results were very bad due to the fact that we had no data.",
        "tone_colloquial": "Hey, what's up with the report? Let me know ASAP.",
        "fragment": "Because he was tired.",
        "full_paragraph": "This are a bad sentence. She go to college and the students is ready. However the results were very bad due to the fact that I went two the market to recieve the package tommorow."
    };

    // =========================================================
    // Theme Handling
    // =========================================================
    function initTheme() {
        const savedTheme = localStorage.getItem("grammacheck_theme");
        if (savedTheme === "dark" || (!savedTheme && window.matchMedia("(prefers-color-scheme: dark)").matches)) {
            document.body.classList.add("dark-mode");
            themeToggleBtn.textContent = "☀️";
        } else {
            document.body.classList.remove("dark-mode");
            themeToggleBtn.textContent = "🌙";
        }
    }

    function toggleTheme() {
        const isDark = document.body.classList.toggle("dark-mode");
        themeToggleBtn.textContent = isDark ? "☀️" : "🌙";
        localStorage.setItem("grammacheck_theme", isDark ? "dark" : "light");
    }

    // =========================================================
    // Navigation / View Switching
    // =========================================================
    function switchView(targetViewId) {
        navTabs.forEach(tab => {
            const isActive = tab.getAttribute("data-tab") === targetViewId;
            tab.classList.toggle("active", isActive);
        });

        dashboardViews.forEach(view => {
            const isTarget = view.id === `view-${targetViewId}`;
            view.classList.toggle("active", isTarget);
        });

        if (targetViewId === "history") {
            renderHistoryList();
        } else if (targetViewId === "performance" && currentAnalysis) {
            renderPerformanceReport(currentAnalysis);
        }
    }

    // =========================================================
    // Toast Notification Helper
    // =========================================================
    function showToast(message, icon = "✓") {
        if (!toast) return;
        toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
        toast.classList.add("show");
        setTimeout(() => {
            toast.classList.remove("show");
        }, 3000);
    }

    // =========================================================
    // Live Word and Character Counters
    // =========================================================
    function updateLiveCounters() {
        const text = editor.value;
        const trimmed = text.trim();
        const words = trimmed ? trimmed.split(/\s+/).length : 0;
        const chars = text.length;
        
        liveWords.textContent = words;
        liveChars.textContent = chars;
    }

    // =========================================================
    // API Interaction: Check Writing
    // =========================================================
    async function checkText(forceImmediate = false, autoSaveToHistory = true) {
        const text = editor.value;
        if (!text.trim()) {
            resetToEmptyState();
            return;
        }

        checkBtn.disabled = true;
        checkBtn.innerHTML = `<span>⏳</span> Checking...`;

        try {
            const response = await fetch(`${API_BASE}/api/check`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: text })
            });

            if (!response.ok) {
                throw new Error(`Server returned status ${response.status}`);
            }

            const data = await response.json();
            currentAnalysis = data;
            renderAnalysis(data);

            if (autoSaveToHistory) {
                recordHistoryItem(data);
            }
        } catch (err) {
            console.error("API check error:", err);
            showToast("NLP server request failed. Please check connection.", "⚠️");
        } finally {
            checkBtn.disabled = false;
            checkBtn.innerHTML = `<span>✓</span> Check Writing`;
        }
    }

    // =========================================================
    // Render Results (Workspace & Assessment)
    // =========================================================
    function renderAnalysis(data) {
        renderScore(data.statistics.accuracy_percentage, data.statistics.accuracy_rating, data.issues.length);
        renderFilterTabs(data.issues, data.issue_counts);
        renderIssuesFeed(data.issues);
        renderCorrectedPreview(data.corrected_text, data.original_text, data.issues);
        renderAnalytics(data.statistics, data.tone_analysis);
        renderPerformanceReport(data);
    }

    function renderScore(percentage, rating, issueCount) {
        scoreNum.textContent = percentage;
        
        // Circular progress calculation: circumference = 2 * PI * 40 = 251.2
        const circumference = 251.2;
        const offset = circumference - (percentage / 100) * circumference;
        scoreCircle.style.strokeDashoffset = offset;

        scoreBadge.className = "score-badge";
        if (percentage >= 90) {
            scoreCircle.style.stroke = "var(--brand-primary)";
            scoreBadge.classList.add("excellent");
            scoreBadge.textContent = "Excellent";
            scoreTitle.textContent = "Very polished writing!";
            scoreDesc.textContent = issueCount === 0 ? "No spelling, grammar, or style issues detected." : "Only minor improvements suggested.";
        } else if (percentage >= 75) {
            scoreCircle.style.stroke = "var(--color-grammar)";
            scoreBadge.classList.add("good");
            scoreBadge.textContent = "Good";
            scoreTitle.textContent = "Good, with a few issues.";
            scoreDesc.textContent = "Review the highlighted suggestions to improve clarity and correctness.";
        } else if (percentage >= 60) {
            scoreCircle.style.stroke = "var(--color-style)";
            scoreBadge.classList.add("needs-improvement");
            scoreBadge.textContent = "Needs Work";
            scoreTitle.textContent = "Needs Improvement";
            scoreDesc.textContent = "Multiple grammar, spelling, or structure errors were identified.";
        } else {
            scoreCircle.style.stroke = "var(--color-spelling)";
            scoreBadge.classList.add("critical");
            scoreBadge.textContent = "Critical";
            scoreTitle.textContent = "Major corrections needed";
            scoreDesc.textContent = "Your text contains critical grammar and spelling errors.";
        }
    }

    function renderFilterTabs(issues, counts) {
        const categories = [
            { id: "all", label: "All Issues", count: issues.length },
            { id: "grammar", label: "Grammar", count: counts.grammar || 0 },
            { id: "spelling", label: "Spelling", count: counts.spelling || 0 },
            { id: "punctuation", label: "Punctuation", count: counts.punctuation || 0 },
            { id: "context", label: "Context", count: counts.context || 0 },
            { id: "vocabulary", label: "Vocabulary", count: counts.vocabulary || 0 },
            { id: "style", label: "Style", count: counts.style || 0 },
            { id: "tone", label: "Tone", count: counts.tone || 0 }
        ];

        filterTabsContainer.innerHTML = categories.map(cat => `
            <button class="filter-tab ${activeFilter === cat.id ? 'active' : ''}" data-filter="${cat.id}">
                ${cat.label} <span class="count">${cat.count}</span>
            </button>
        `).join("");

        filterTabsContainer.querySelectorAll(".filter-tab").forEach(tab => {
            tab.addEventListener("click", () => {
                activeFilter = tab.getAttribute("data-filter");
                filterTabsContainer.querySelectorAll(".filter-tab").forEach(t => t.classList.remove("active"));
                tab.classList.add("active");
                renderIssuesFeed(currentAnalysis.issues);
            });
        });
    }

    // Assessment: Flagged Issues Feed
    function renderIssuesFeed(issues) {
        const filtered = activeFilter === "all"
            ? issues
            : issues.filter(iss => iss.category.toLowerCase() === activeFilter);

        if (filtered.length === 0) {
            issuesFeed.innerHTML = `
                <div class="empty-state">
                    <div class="icon">✨</div>
                    <h4>No ${activeFilter === "all" ? "" : activeFilter} issues found</h4>
                    <p>Your writing looks clean, clear, and well-structured!</p>
                </div>
            `;
            return;
        }

        issuesFeed.innerHTML = filtered.map(issue => {
            const catLower = issue.category.toLowerCase();
            const originalEscaped = escapeHtml(issue.original || "(missing)");
            const replacementEscaped = escapeHtml(issue.replacement || "");
            
            return `
                <div class="issue-card category-${catLower}" id="${issue.id}">
                    <div class="issue-meta-row">
                        <span class="category-tag tag-${catLower}">${issue.category}</span>
                        <span style="font-size:11px;color:var(--text-muted);">${issue.rule_id || ""}</span>
                    </div>
                    
                    <div class="issue-diff-row">
                        <span class="original-err">${originalEscaped}</span>
                        <span class="arrow-icon">➔</span>
                        ${issue.replacement ? `
                            <span class="suggested-fix" data-action="accept" data-issue-id="${issue.id}" title="Click to accept suggestion">
                                ✓ ${replacementEscaped}
                            </span>
                        ` : `
                            <span style="font-size:12px;color:var(--text-muted);font-style:italic;">(Review sentence)</span>
                        `}
                    </div>
                    
                    <div class="issue-explanation">
                        <b>${escapeHtml(issue.message || "")}</b><br>
                        ${escapeHtml(issue.explanation || "")}
                    </div>
                    
                    <div class="issue-actions-row">
                        ${issue.replacement ? `
                            <button class="btn-accept" data-action="accept" data-issue-id="${issue.id}">
                                Accept
                            </button>
                        ` : ""}
                        <button class="btn-dismiss" data-action="dismiss" data-issue-id="${issue.id}">
                            Ignore
                        </button>
                        ${issue.category === "Spelling" ? `
                            <button class="btn-dict" data-action="add-dict" data-word="${escapeHtml(issue.original)}">
                                + Add to Dictionary
                            </button>
                        ` : ""}
                    </div>
                </div>
            `;
        }).join("");

        issuesFeed.querySelectorAll("[data-action]").forEach(btn => {
            btn.addEventListener("click", () => {
                const action = btn.getAttribute("data-action");
                const issueId = btn.getAttribute("data-issue-id");
                const word = btn.getAttribute("data-word");
                handleIssueAction(action, issueId, word);
            });
        });
    }

    function handleIssueAction(action, issueId, word) {
        if (!currentAnalysis) return;

        if (action === "accept") {
            const issue = currentAnalysis.issues.find(iss => iss.id === issueId);
            if (!issue || !issue.replacement) return;

            const text = editor.value;
            const start = issue.start;
            const end = issue.end;

            if (start >= 0 && end <= text.length) {
                editor.value = text.substring(0, start) + issue.replacement + text.substring(end);
                updateLiveCounters();
                showToast(`Applied fix: "${issue.replacement}"`, "✓");
                checkText(true);
            }
        } else if (action === "dismiss") {
            currentAnalysis.issues = currentAnalysis.issues.filter(iss => iss.id !== issueId);
            currentAnalysis.issue_counts.total = currentAnalysis.issues.length;
            renderAnalysis(currentAnalysis);
            showToast("Issue ignored", "✕");
        } else if (action === "add-dict") {
            if (!word) return;
            fetch(`${API_BASE}/api/dictionary/add`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ word: word })
            })
            .then(res => res.json())
            .then(() => {
                showToast(`Added "${word}" to custom dictionary`, "📖");
                checkText(true);
            })
            .catch(err => {
                console.error("Dictionary error:", err);
                showToast("Failed to add word to dictionary", "⚠️");
            });
        }
    }

    function renderCorrectedPreview(correctedText, originalText, issues) {
        if (!correctedText) {
            previewContent.textContent = "Your corrected text will appear here after checking.";
            return;
        }

        if (correctedText === originalText && issues.length === 0) {
            previewContent.innerHTML = `<span style="color:var(--brand-primary);font-weight:600;">✓ Perfect writing!</span> No corrections were needed.<br><br>${escapeHtml(correctedText)}`;
        } else {
            previewContent.textContent = correctedText;
        }
    }

    function renderAnalytics(stats, tone) {
        statWords.textContent = stats.word_count;
        statSentences.textContent = stats.sentence_count;
        statReadingTime.textContent = stats.reading_time_minutes > 0 ? `${stats.reading_time_minutes} min` : "< 1 min";
        statReadability.textContent = `${stats.flesch_reading_ease}/100`;
        statReadabilityGrade.textContent = stats.readability_label;
    }

    // =========================================================
    // FEATURE #8: GRAPHICAL PERFORMANCE REPORT
    // =========================================================
    function renderPerformanceReport(data) {
        if (!data || !data.statistics) return;

        const stats = data.statistics;
        const tone = data.tone_analysis;
        const issues = data.issues || [];
        const counts = data.issue_counts || {};

        // 1. Accuracy Gauge
        const score = stats.accuracy_percentage;
        perfScoreNum.textContent = score;
        
        // Large Gauge: radius 50 => circumference = 2 * PI * 50 = 314.15
        const circumference = 314.15;
        const offset = circumference - (score / 100) * circumference;
        perfCircle.style.strokeDashoffset = offset;

        perfScoreBadge.className = "score-badge";
        if (score >= 90) {
            perfCircle.style.stroke = "var(--brand-primary)";
            perfScoreBadge.classList.add("excellent");
            perfScoreBadge.textContent = "Excellent";
            perfQualityTitle.textContent = "Polished & Accurate Writing";
            perfQualityDesc.textContent = "High grammatical correctness and strong structural flow.";
        } else if (score >= 75) {
            perfCircle.style.stroke = "var(--color-grammar)";
            perfScoreBadge.classList.add("good");
            perfScoreBadge.textContent = "Good";
            perfQualityTitle.textContent = "Good Writing Quality";
            perfQualityDesc.textContent = "Writing is understandable, with a few punctuation or style suggestions.";
        } else if (score >= 60) {
            perfCircle.style.stroke = "var(--color-style)";
            perfScoreBadge.classList.add("needs-improvement");
            perfScoreBadge.textContent = "Needs Work";
            perfQualityTitle.textContent = "Room for Improvement";
            perfQualityDesc.textContent = "Multiple issues identified across grammar, spelling, or structure.";
        } else {
            perfCircle.style.stroke = "var(--color-spelling)";
            perfScoreBadge.classList.add("critical");
            perfScoreBadge.textContent = "Critical";
            perfQualityTitle.textContent = "Significant Corrections Needed";
            perfQualityDesc.textContent = "Major spelling and subject-verb agreement issues require attention.";
        }

        // 2. Readability & Comprehension
        const flesch = stats.flesch_reading_ease;
        perfFleschNum.textContent = `${flesch} / 100`;
        perfFleschFill.style.width = `${Math.min(100, Math.max(5, flesch))}%`;
        perfReadabilityTag.textContent = stats.readability_label;
        perfAudienceLevel.textContent = stats.grade_level_label || "General Audience";
        perfAvgSentence.textContent = `${stats.average_sentence_length} words`;
        perfAvgSyllable.textContent = stats.average_syllables_per_word || "1.4";
        perfEstReading.textContent = stats.reading_time_minutes > 0 ? `${stats.reading_time_minutes} min` : "< 1 min";

        // 3. Issue Category Distribution
        const totalIssues = issues.length;
        perfTotalIssues.textContent = totalIssues;

        const spellCount = counts.spelling || 0;
        const gramCount = counts.grammar || 0;
        const puncCount = counts.punctuation || 0;
        const ctxCount = counts.context || 0;
        const styleCount = (counts.style || 0) + (counts.vocabulary || 0);

        distSpellVal.textContent = spellCount;
        distGramVal.textContent = gramCount;
        distPuncVal.textContent = puncCount;
        distCtxVal.textContent = ctxCount;
        distStyleVal.textContent = styleCount;

        const maxIssues = Math.max(1, totalIssues);
        distSpellBar.style.width = `${(spellCount / maxIssues) * 100}%`;
        distGramBar.style.width = `${(gramCount / maxIssues) * 100}%`;
        distPuncBar.style.width = `${(puncCount / maxIssues) * 100}%`;
        distCtxBar.style.width = `${(ctxCount / maxIssues) * 100}%`;
        distStyleBar.style.width = `${(styleCount / maxIssues) * 100}%`;

        // 4. Tone Breakdown
        if (tone) {
            perfToneBadge.textContent = tone.formality;
            perfToneSummary.textContent = tone.summary;

            perfBarFormal.style.width = `${tone.scores.formal}%`;
            perfBarCasual.style.width = `${tone.scores.casual}%`;
            perfBarProf.style.width = `${tone.scores.professional}%`;
            perfBarAcad.style.width = `${tone.scores.academic}%`;

            perfValFormal.textContent = `${tone.scores.formal}%`;
            perfValCasual.textContent = `${tone.scores.casual}%`;
            perfValProf.textContent = `${tone.scores.professional}%`;
            perfValAcad.textContent = `${tone.scores.academic}%`;
        }
    }

    // =========================================================
    // FEATURE #6: DOCUMENT UPLOAD & SUCCESS STATE
    // =========================================================
    function initDocumentUpload() {
        // Browse button trigger
        btnBrowseFile.addEventListener("click", () => fileUploadInput.click());
        uploadDropzone.addEventListener("click", (e) => {
            if (e.target !== btnBrowseFile) fileUploadInput.click();
        });

        // Drag & Drop
        uploadDropzone.addEventListener("dragover", (e) => {
            e.preventDefault();
            uploadDropzone.classList.add("dragover");
        });

        uploadDropzone.addEventListener("dragleave", () => {
            uploadDropzone.classList.remove("dragover");
        });

        uploadDropzone.addEventListener("drop", (e) => {
            e.preventDefault();
            uploadDropzone.classList.remove("dragover");
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                processDocumentFile(files[0]);
            }
        });

        // File input change
        fileUploadInput.addEventListener("change", (e) => {
            if (e.target.files.length > 0) {
                processDocumentFile(e.target.files[0]);
            }
        });

        // "Analyze Document Now" action
        btnScanUploaded.addEventListener("click", () => {
            if (!uploadedFileCache || !uploadedFileCache.text) {
                showToast("No extracted text to analyze", "⚠️");
                return;
            }
            editor.value = uploadedFileCache.text;
            updateLiveCounters();
            switchView("workspace");
            checkText(true, true);
            showToast(`Loaded "${uploadedFileCache.filename}" into editor & scanned`, "🚀");
        });

        // Copy Extracted Text
        btnCopyExtracted.addEventListener("click", () => {
            if (!extractedTextPreview.value) return;
            navigator.clipboard.writeText(extractedTextPreview.value).then(() => {
                showToast("Extracted document text copied!", "📋");
            });
        });

        // Upload Another File
        btnUploadAnother.addEventListener("click", () => {
            uploadSuccessCard.style.display = "none";
            uploadDropzone.style.display = "block";
            fileUploadInput.value = "";
            uploadedFileCache = null;
        });
    }

    async function processDocumentFile(file) {
        if (!file) return;

        showToast(`Processing "${file.name}"...`, "⏳");

        try {
            const text = await readFileAsText(file);
            const words = text.trim() ? text.trim().split(/\s+/).length : 0;
            const ext = file.name.split(".").pop().toUpperCase() || "TXT";
            const payload = {
                filename: file.name,
                text: text,
                file_size_str: formatBytes(file.size),
                file_size_bytes: file.size,
                file_type: ext
            };

            let resultData = null;
            try {
                const res = await fetch(`${API_BASE}/api/upload`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                if (res.ok) {
                    resultData = await res.json();
                }
            } catch (netErr) {
                console.warn("Backend /api/upload unavailable, using local parsed text", netErr);
            }

            if (!resultData) {
                resultData = {
                    filename: file.name,
                    file_size: formatBytes(file.size),
                    file_type: ext,
                    word_count: words,
                    character_count: text.length,
                    text: text
                };
            }

            uploadedFileCache = resultData;
            displayUploadSuccessState(resultData);
            showToast(`"${file.name}" uploaded successfully!`, "✓");

        } catch (err) {
            console.error("Document upload error:", err);
            showToast("Failed to process document file", "⚠️");
        }
    }

    function readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsText(file);
        });
    }

    function displayUploadSuccessState(info) {
        uploadDropzone.style.display = "none";
        uploadSuccessCard.style.display = "block";

        uploadFilename.textContent = info.filename;
        uploadFilesize.textContent = info.file_size;
        uploadWordcount.textContent = `${info.word_count.toLocaleString()} words`;
        uploadCharcount.textContent = `${info.character_count.toLocaleString()} chars`;
        uploadTimestamp.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        uploadFileType.textContent = info.file_type || "DOC";

        extractedTextPreview.value = info.text;
    }

    function formatBytes(bytes) {
        if (bytes < 1024) return bytes + " B";
        else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
        else return (bytes / 1048576).toFixed(2) + " MB";
    }

    // =========================================================
    // FEATURE #9: HISTORY (PAST CHECKS LOG)
    // =========================================================
    async function loadHistoryFromStorage() {
        try {
            const res = await fetch(`${API_BASE}/api/history`);
            if (res.ok) {
                const data = await res.json();
                historyItems = data.history || [];
            } else {
                throw new Error("API history unavailable");
            }
        } catch (e) {
            const saved = localStorage.getItem("grammacheck_history");
            historyItems = saved ? JSON.parse(saved) : [];
        }

        updateHistoryBadge();
    }

    async function recordHistoryItem(analysis) {
        const text = editor.value.trim();
        if (!text) return;

        const words = analysis.statistics.word_count || (text.split(/\s+/).length);
        const chars = text.length;
        const score = analysis.statistics.accuracy_percentage;
        const issuesCount = analysis.issues.length;
        const tone = analysis.tone_analysis ? analysis.tone_analysis.formality : "Neutral";
        const title = text.slice(0, 60).replace(/\n/g, " ") + (text.length > 60 ? "..." : "");

        const entry = {
            id: `chk_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
            title: title,
            original_text: text,
            corrected_text: analysis.corrected_text || "",
            word_count: words,
            char_count: chars,
            score: score,
            issues_count: issuesCount,
            tone: tone,
            timestamp: new Date().toLocaleDateString("en-US", { month: "short", day: "numeric" }) + " - " + new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
            timestamp_epoch: Date.now()
        };

        // Post to backend
        try {
            await fetch(`${API_BASE}/api/history`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(entry)
            });
        } catch (e) {
            console.warn("Backend history post fallback", e);
        }

        // Local cache
        if (historyItems.length > 0 && historyItems[0].original_text === text) {
            historyItems[0] = entry;
        } else {
            historyItems.unshift(entry);
        }
        historyItems = historyItems.slice(0, 50);
        localStorage.setItem("grammacheck_history", JSON.stringify(historyItems));

        updateHistoryBadge();
    }

    function updateHistoryBadge() {
        if (navHistoryCount) {
            navHistoryCount.textContent = historyItems.length;
        }
    }

    function renderHistoryList() {
        if (!historyListContainer) return;

        const query = (historySearchInput.value || "").toLowerCase().trim();
        const filter = historyFilterSelect.value;

        let filtered = historyItems.filter(item => {
            const matchesQuery = !query || 
                item.title.toLowerCase().includes(query) || 
                item.original_text.toLowerCase().includes(query) ||
                (item.timestamp && item.timestamp.toLowerCase().includes(query));

            if (!matchesQuery) return false;

            if (filter === "high") return item.score >= 85;
            if (filter === "medium") return item.score >= 70 && item.score < 85;
            if (filter === "low") return item.score < 70;
            return true;
        });

        if (filtered.length === 0) {
            historyListContainer.innerHTML = `
                <div class="empty-state">
                    <div class="icon">📜</div>
                    <h4>No history entries found</h4>
                    <p>${query ? "No past checks matched your search query." : "Checks you perform in the editor or uploaded documents will automatically appear here."}</p>
                </div>
            `;
            return;
        }

        historyListContainer.innerHTML = filtered.map(item => {
            const scoreClass = item.score >= 85 ? "high" : (item.score >= 70 ? "medium" : "low");
            const snippet = escapeHtml(item.original_text.slice(0, 160) + (item.original_text.length > 160 ? "..." : ""));

            return `
                <div class="history-card" data-id="${item.id}">
                    <div class="history-card-header">
                        <span class="history-title">${escapeHtml(item.title)}</span>
                        <div class="history-meta-badges">
                            <span class="history-badge-score ${scoreClass}">Score: ${item.score}%</span>
                            <span class="category-tag tag-tone" style="font-size:10px;">${escapeHtml(item.tone || "Neutral")}</span>
                            <span style="font-size:11px;color:var(--text-muted);">${item.timestamp}</span>
                        </div>
                    </div>

                    <div class="history-snippet">${snippet}</div>

                    <div class="history-card-footer">
                        <div class="history-stats-row">
                            <span>Words: <b>${item.word_count}</b></span>
                            <span>Characters: <b>${item.char_count}</b></span>
                            <span>Issues Flagged: <b style="color:${item.issues_count > 0 ? 'var(--color-spelling)' : 'var(--brand-primary)'};">${item.issues_count}</b></span>
                        </div>

                        <div class="history-actions-row">
                            <button class="btn-secondary small" data-action="load-history" data-id="${item.id}" title="Open this text in the editor">
                                👁️ Load in Editor
                            </button>
                            <button class="btn-secondary small" data-action="export-history" data-id="${item.id}" title="Download diagnostic report">
                                📥 Export Report
                            </button>
                            <button class="btn-secondary small" data-action="delete-history" data-id="${item.id}" style="color:var(--color-spelling);" title="Delete check from history">
                                🗑️ Delete
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join("");

        // Attach action handlers
        historyListContainer.querySelectorAll("[data-action]").forEach(btn => {
            btn.addEventListener("click", () => {
                const action = btn.getAttribute("data-action");
                const id = btn.getAttribute("data-id");
                const item = historyItems.find(h => h.id === id);
                if (!item) return;

                if (action === "load-history") {
                    editor.value = item.original_text;
                    updateLiveCounters();
                    switchView("workspace");
                    checkText(true, false);
                    showToast("Loaded check into editor", "📂");
                } else if (action === "export-history") {
                    downloadHistoryReport(item);
                } else if (action === "delete-history") {
                    deleteHistoryItem(id);
                }
            });
        });
    }

    function deleteHistoryItem(id) {
        historyItems = historyItems.filter(h => h.id !== id);
        localStorage.setItem("grammacheck_history", JSON.stringify(historyItems));
        fetch(`${API_BASE}/api/history/${id}`, { method: "DELETE" }).catch(() => {});
        updateHistoryBadge();
        renderHistoryList();
        showToast("History entry deleted", "🗑️");
    }

    function downloadHistoryReport(item) {
        const content = `===============================================================
GRAMMACHECK AI - WRITING DIAGNOSTIC REPORT
===============================================================
Date/Time:       ${item.timestamp}
Accuracy Score:  ${item.score}%
Tone Register:   ${item.tone}
Word Count:      ${item.word_count}
Character Count: ${item.char_count}
Flagged Issues:  ${item.issues_count}

---------------------------------------------------------------
ORIGINAL TEXT:
---------------------------------------------------------------
${item.original_text}

---------------------------------------------------------------
CORRECTED VERSION:
---------------------------------------------------------------
${item.corrected_text || "(No corrections recorded)"}

===============================================================
Generated by GrammaCheck AI - NLP Grammar & Style Checker
===============================================================`;

        const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `GrammaCheck_Report_${item.id}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        showToast("Diagnostic report downloaded", "📥");
    }

    // =========================================================
    // AUTHENTICATION & USER MANAGEMENT
    // =========================================================
    function initAuth() {
        // Check stored user
        const savedUser = localStorage.getItem("grammacheck_user");
        if (savedUser) {
            try {
                currentUser = JSON.parse(savedUser);
                updateAuthUI(currentUser);
            } catch (e) {
                currentUser = null;
            }
        }

        // Open modal
        btnOpenLogin.addEventListener("click", () => openModal("login"));
        btnOpenSignup.addEventListener("click", () => openModal("signup"));
        btnCloseModal.addEventListener("click", closeModal);

        // Modal backdrop click
        authModal.addEventListener("click", (e) => {
            if (e.target === authModal) closeModal();
        });

        // Tab switcher inside modal
        tabModalLogin.addEventListener("click", () => switchModalTab("login"));
        tabModalSignup.addEventListener("click", () => switchModalTab("signup"));

        // 1-Click Demo Login
        btnQuickDemo.addEventListener("click", () => {
            loginUser("demo@grammacheck.ai", "password123");
        });

        // Sign In Form Submit
        formLogin.addEventListener("submit", (e) => {
            e.preventDefault();
            const email = document.getElementById("login-email").value.trim();
            const password = document.getElementById("login-password").value;
            loginUser(email, password);
        });

        // Sign Up Form Submit
        formSignup.addEventListener("submit", (e) => {
            e.preventDefault();
            const name = document.getElementById("signup-name").value.trim();
            const email = document.getElementById("signup-email").value.trim();
            const password = document.getElementById("signup-password").value;
            const plan = document.getElementById("signup-plan").value;
            signupUser(name, email, password, plan);
        });

        // Logout
        btnLogout.addEventListener("click", logoutUser);
    }

    function openModal(tab = "login") {
        authModal.style.display = "flex";
        loginError.style.display = "none";
        signupError.style.display = "none";
        switchModalTab(tab);
    }

    function closeModal() {
        authModal.style.display = "none";
    }

    function switchModalTab(tab) {
        if (tab === "login") {
            tabModalLogin.classList.add("active");
            tabModalSignup.classList.remove("active");
            formLogin.style.display = "flex";
            formSignup.style.display = "none";
        } else {
            tabModalLogin.classList.remove("active");
            tabModalSignup.classList.add("active");
            formLogin.style.display = "none";
            formSignup.style.display = "flex";
        }
    }

    async function loginUser(email, password) {
        loginError.style.display = "none";

        try {
            const res = await fetch(`${API_BASE}/api/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            });

            if (res.ok) {
                const data = await res.json();
                handleAuthSuccess(data.user);
            } else {
                const errData = await res.json().catch(() => ({}));
                // Mock fallback for demo account if backend offline
                if (email === "demo@grammacheck.ai" && password === "password123") {
                    handleAuthSuccess({
                        id: "usr_demo",
                        name: "Alex Morgan",
                        email: email,
                        plan: "Pro",
                        avatar: "AM"
                    });
                } else {
                    loginError.textContent = errData.detail || "Invalid email or password.";
                    loginError.style.display = "block";
                }
            }
        } catch (e) {
            // Offline fallback for demo
            if (email === "demo@grammacheck.ai") {
                handleAuthSuccess({
                    id: "usr_demo",
                    name: "Alex Morgan",
                    email: email,
                    plan: "Pro",
                    avatar: "AM"
                });
            } else {
                loginError.textContent = "Unable to reach authentication server.";
                loginError.style.display = "block";
            }
        }
    }

    async function signupUser(name, email, password, plan) {
        signupError.style.display = "none";

        try {
            const res = await fetch(`${API_BASE}/api/auth/signup`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name, email, password, plan })
            });

            if (res.ok) {
                const data = await res.json();
                handleAuthSuccess(data.user);
            } else {
                const errData = await res.json().catch(() => ({}));
                signupError.textContent = errData.detail || "Could not register account.";
                signupError.style.display = "block";
            }
        } catch (e) {
            // Local fallback
            handleAuthSuccess({
                id: `usr_${Date.now()}`,
                name: name,
                email: email,
                plan: plan,
                avatar: name.split(" ").map(p => p[0].toUpperCase()).join("").slice(0, 2)
            });
        }
    }

    function handleAuthSuccess(user) {
        currentUser = user;
        localStorage.setItem("grammacheck_user", JSON.stringify(user));
        updateAuthUI(user);
        closeModal();
        showToast(`Welcome back, ${user.name}!`, "👋");
    }

    function updateAuthUI(user) {
        if (user) {
            authGuestControls.style.display = "none";
            authUserProfile.style.display = "flex";
            headerUserAvatar.textContent = user.avatar || user.name.slice(0, 2).toUpperCase();
            headerUserName.textContent = user.name;
            headerUserPlan.textContent = `${user.plan || "Pro"} Plan`;
        } else {
            authGuestControls.style.display = "flex";
            authUserProfile.style.display = "none";
        }
    }

    function logoutUser() {
        currentUser = null;
        localStorage.removeItem("grammacheck_user");
        updateAuthUI(null);
        showToast("Signed out successfully", "🔒");
    }

    // =========================================================
    // Reset to Empty State
    // =========================================================
    function resetToEmptyState() {
        currentAnalysis = null;
        updateLiveCounters();
        
        scoreNum.textContent = "100";
        scoreCircle.style.strokeDashoffset = "0";
        scoreCircle.style.stroke = "var(--brand-primary)";
        scoreBadge.className = "score-badge excellent";
        scoreBadge.textContent = "Ready";
        scoreTitle.textContent = "Ready to analyze";
        scoreDesc.textContent = "Type or paste your text to check grammar and spelling.";

        filterTabsContainer.innerHTML = `
            <button class="filter-tab active" data-filter="all">All Issues <span class="count">0</span></button>
        `;

        issuesFeed.innerHTML = `
            <div class="empty-state">
                <div class="icon">✍️</div>
                <h4>Your writing suggestions will appear here</h4>
                <p>Start typing or select an example test case to run instant NLP analysis.</p>
            </div>
        `;

        previewContent.textContent = "Your corrected text will appear here after checking.";

        statWords.textContent = "0";
        statSentences.textContent = "0";
        statReadingTime.textContent = "0 min";
        statReadability.textContent = "100/100";
        statReadabilityGrade.textContent = "Very Easy";

        // Reset Performance Dashboard
        perfScoreNum.textContent = "100";
        perfCircle.style.strokeDashoffset = "0";
        perfScoreBadge.className = "score-badge excellent";
        perfScoreBadge.textContent = "Ready";
        perfFleschNum.textContent = "100 / 100";
        perfFleschFill.style.width = "100%";
        perfReadabilityTag.textContent = "Very Easy";
        perfTotalIssues.textContent = "0";
    }

    function escapeHtml(str) {
        if (!str) return "";
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // =========================================================
    // Event Listeners Setup
    // =========================================================
    function initEvents() {
        // Navigation Tabs click
        navTabs.forEach(tab => {
            tab.addEventListener("click", () => {
                const targetView = tab.getAttribute("data-tab");
                switchView(targetView);
            });
        });

        // Editor input debounced checking
        editor.addEventListener("input", () => {
            updateLiveCounters();
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                if (editor.value.trim().length > 0) {
                    checkText(false, false);
                } else {
                    resetToEmptyState();
                }
            }, 500);
        });

        // Check button click (triggers immediate check and saves to history)
        checkBtn.addEventListener("click", () => {
            checkText(true, true);
        });

        // Save to History button
        saveToHistoryBtn.addEventListener("click", () => {
            if (!currentAnalysis) {
                checkText(true, true);
            } else {
                recordHistoryItem(currentAnalysis);
                showToast("Saved current analysis to history log", "💾");
            }
        });

        // Clear button
        clearBtn.addEventListener("click", () => {
            editor.value = "";
            resetToEmptyState();
            sampleSelect.value = "";
            showToast("Editor cleared", "🧹");
        });

        // Copy original
        copyBtn.addEventListener("click", () => {
            const text = editor.value;
            if (!text) {
                showToast("Nothing to copy", "⚠️");
                return;
            }
            navigator.clipboard.writeText(text).then(() => {
                showToast("Original text copied to clipboard!", "📋");
            });
        });

        // Copy corrected
        copyCorrectedBtn.addEventListener("click", () => {
            const text = currentAnalysis ? currentAnalysis.corrected_text : editor.value;
            if (!text) {
                showToast("Nothing to copy", "⚠️");
                return;
            }
            navigator.clipboard.writeText(text).then(() => {
                showToast("Corrected text copied to clipboard!", "📋");
            });
        });

        // Theme toggle
        themeToggleBtn.addEventListener("click", toggleTheme);

        // Sample selector
        sampleSelect.addEventListener("change", () => {
            const key = sampleSelect.value;
            if (key && SAMPLES[key]) {
                editor.value = SAMPLES[key];
                updateLiveCounters();
                checkText(true, true);
                showToast("Sample loaded & analyzed", "🧪");
            }
        });

        // Keyboard shortcut: Ctrl/Cmd + Enter
        editor.addEventListener("keydown", (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
                e.preventDefault();
                checkText(true, true);
            }
        });

        // History search & filter
        historySearchInput.addEventListener("input", renderHistoryList);
        historyFilterSelect.addEventListener("change", renderHistoryList);

        // Clear All History button
        btnClearHistory.addEventListener("click", () => {
            if (historyItems.length === 0) return;
            if (confirm("Are you sure you want to clear all check history?")) {
                historyItems = [];
                localStorage.removeItem("grammacheck_history");
                fetch(`${API_BASE}/api/history`, { method: "DELETE" }).catch(() => {});
                updateHistoryBadge();
                renderHistoryList();
                showToast("All history cleared", "🧹");
            }
        });

        // Refresh Report button
        if (btnRefreshReport) {
            btnRefreshReport.addEventListener("click", () => {
                if (currentAnalysis) {
                    renderPerformanceReport(currentAnalysis);
                    showToast("Performance report updated", "🔄");
                } else if (editor.value.trim()) {
                    checkText(true, false).then(() => {
                        showToast("Performance report updated", "🔄");
                    });
                } else {
                    showToast("Please enter or scan some text first", "ℹ️");
                }
            });
        }
    }

    // =========================================================
    // Initialization
    // =========================================================
    initTheme();
    initAuth();
    initDocumentUpload();
    initEvents();
    loadHistoryFromStorage();
    resetToEmptyState();

})();
