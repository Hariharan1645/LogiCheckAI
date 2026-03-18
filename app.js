document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const urlInput = document.getElementById('video-url');
    const analyzeBtn = document.getElementById('analyze-btn');
    const loadingState = document.getElementById('loading-state');
    const errorState = document.getElementById('error-state');
    const resultsState = document.getElementById('results-state');
    const resultsCount = document.getElementById('claims-count');
    const claimsList = document.getElementById('claims-list');
    const errorMessage = document.getElementById('error-message');
    const retryBtn = document.getElementById('retry-btn');
    const loadingText = document.getElementById('loading-text');
    const themeToggleBtn = document.getElementById('theme-toggle');
    const body = document.body;

    // Check for saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        body.classList.add('dark-mode');
        themeToggleBtn.innerHTML = '<i class="fa-solid fa-sun"></i>';
    }

    // Theme toggle event
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            body.classList.toggle('dark-mode');
            // Update icon based on theme
            if (body.classList.contains('dark-mode')) {
                themeToggleBtn.innerHTML = '<i class="fa-solid fa-sun"></i>';
                localStorage.setItem('theme', 'dark');
            } else {
                themeToggleBtn.innerHTML = '<i class="fa-solid fa-moon"></i>';
                localStorage.setItem('theme', 'light');
            }
        });
    }

    // Loading stages to cycle through
    const loadingStages = [
        "Extracting speech from video...",
        "Converting speech to text via Whisper AI...",
        "Detecting healthcare claims...",
        "Retrieving evidence from medical sources...",
        "Evaluating claims against trusted sources..."
    ];

    let loadingInterval;
    let isAnalyzing = false;

    // Validate URL
    urlInput.addEventListener('input', () => {
        const val = urlInput.value.trim();
        if (val.length > 0) {
            analyzeBtn.disabled = false;
        }
    });

    // Analyze Button Click
    analyzeBtn.addEventListener('click', () => {
        const url = urlInput.value.trim();
        if (!url || isAnalyzing) return;
        startAnalysis(url);
    });

    // Enter Key
    urlInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const url = urlInput.value.trim();
            if (url && !isAnalyzing) startAnalysis(url);
        }
    });

    // Retry Button
    retryBtn.addEventListener('click', () => {
        const url = urlInput.value.trim();
        if (url && !isAnalyzing) startAnalysis(url);
    });

    function cycleLoadingText() {
        let currentIndex = 0;
        loadingText.textContent = loadingStages[0];
        
        loadingInterval = setInterval(() => {
            currentIndex = (currentIndex + 1) % loadingStages.length;
            loadingText.textContent = loadingStages[currentIndex];
        }, 3500); // Change text every 3.5 seconds
    }

    async function startAnalysis(url) {
        if (isAnalyzing) return;
        isAnalyzing = true;
        
        // Reset states
        errorState.classList.add('hidden');
        resultsState.classList.add('hidden');
        loadingState.classList.remove('hidden');
        claimsList.innerHTML = '';
        
        // Start loading animation text
        cycleLoadingText();
        analyzeBtn.disabled = true;

        try {
            // Encode the URL parameter
            const encodedUrl = encodeURIComponent(url);
            const apiUrl = `http://localhost:8085/analyze_youtube?url=${encodedUrl}`;

            const response = await fetch(apiUrl, {
                method: 'GET', // or POST if required by backend, user asked for endpoint: return JSON
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                let errorDetail = `Server Error (${response.status})`;
                try {
                    const errorData = await response.json();
                    if (errorData.detail) errorDetail = errorData.detail;
                } catch (e) {}
                const error = new Error(errorDetail);
                if (response.status === 500) error.isServerError = true;
                throw error;
            }

            const data = await response.json();
            
            clearInterval(loadingInterval);
            renderResults(data);
            
        } catch (error) {
            console.error("Analysis Error:", error);
            clearInterval(loadingInterval);
            if (error.isServerError || error.message.includes("Internal Server Error")) {
                showError(`Analysis failed: ${error.message}`);
            } else {
                showError(error.message || "Failed to connect to the analysis server. Please make sure the backend is running.");
            }
        } finally {
            isAnalyzing = false;
            analyzeBtn.disabled = false;
        }
    }

    function renderResults(data) {
        loadingState.classList.add('hidden');
        
        let claims = [];
        
        // Log response for debugging
        console.log("Response data:", data);
        
        // Handle different possible JSON structures
        if (Array.isArray(data)) {
            claims = data;
        } else if (data.data && Array.isArray(data.data)) {
            claims = data.data;
        } else if (data.claims && Array.isArray(data.claims)) {
            claims = data.claims;
        } else if (data && typeof data === 'object') {
            // Object but not an array - check if it's a valid claim object
            if (data.original_claim || data.claim) {
                claims = [data];
            } else {
                // Unknown structure
                console.warn("Unexpected response structure:", data);
                claims = [];
            }
        } else {
            // Invalid response
            console.warn("Invalid response type:", typeof data);
            claims = [];
        }

        const reasoningContainer = document.getElementById('ai-reasoning-container');
        const reasoningContent = document.getElementById('ai-reasoning-content');

        if (data.reasoning) {
            reasoningContent.innerHTML = formatMarkdown(data.reasoning);
            reasoningContainer.classList.remove('hidden');
        } else {
            reasoningContainer.classList.add('hidden');
        }

        if (claims.length === 0) {
            resultsCount.textContent = "No claims detected";
            claimsList.innerHTML = `
                <div class="claim-card" style="padding: 2rem; text-align: center; color: var(--text-muted);">
                    <i class="fa-solid fa-check-circle" style="font-size: 2rem; color: var(--verdict-green); margin-bottom: 1rem;"></i>
                    <p>No healthcare claims were detected in this video.</p>
                </div>
            `;
        } else {
            resultsCount.textContent = `${claims.length} claims detected`;
            
            claims.forEach((claim) => {
                const claimHtml = createClaimCard(claim);
                claimsList.innerHTML += claimHtml;
            });
        }
        
        resultsState.classList.remove('hidden');
        
        // Ensure the screen jumps down to show analysis results if below fold
        setTimeout(() => {
            resultsState.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 300);
    }

    // Basic Markdown format helper for AI reasoning
    function formatMarkdown(text) {
        if (!text) return "";
        
        // Escape HTML to prevent injection if necessary, but AI is considered safe-ish
        let html = text;
        
        // Convert Headers
        html = html.replace(/^### (.*$)/gim, '<h5 style="margin: 0.75rem 0 0.25rem 0; font-size: 1rem; color: var(--text-main);">$1</h5>');
        html = html.replace(/^## (.*$)/gim, '<h4 style="margin: 1rem 0 0.5rem 0; font-size: 1.125rem; color: var(--text-main);">$1</h4>');
        html = html.replace(/^# (.*$)/gim, '<h3 style="margin: 1rem 0 0.5rem 0; font-size: 1.25rem; color: var(--text-main);">$1</h3>');
        
        // Convert Bold
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert Unordered lists
        html = html.replace(/^\s*[-*]\s+(.*$)/gim, '<div style="display: flex; align-items: flex-start; gap: 8px; margin-bottom: 6px;"><i class="fa-solid fa-circle" style="font-size: 6px; margin-top: 8px; color: var(--primary-blue);"></i><span>$1</span></div>');
        
        // Convert numbered lists
        html = html.replace(/^\s*\d+\.\s+(.*$)/gim, '<div style="display: flex; align-items: flex-start; gap: 8px; margin-bottom: 6px;"><strong>$1.</strong><span>$1</span></div>'); // Just naive, might need index tracking, or simple text is fine.
        
        // Convert paragraph spaces using safe `<br>` tags to avoid breaking DOM structure
        html = html.replace(/\n\n/g, '<br><br>');
        
        return `<div style="font-size: 0.95rem;">${html}</div>`;
        
        // Scroll to results
        setTimeout(() => {
            resultsState.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }

    function createClaimCard(claim) {
        const originalClaim = claim.original_claim || claim.claim || claim.original || "Unknown Claim";
        const rewrittenClaim = claim.rewritten_claim || claim.rewritten || claim.structured_claim || "";
        let verdict = claim.verdict || claim.classification || "Unknown";
        let confidence = typeof claim.confidence_score !== 'undefined' ? claim.confidence_score : (claim.confidence || "N/A");
        let evidence = claim.supporting_evidence || claim.evidence || "No evidence provided.";

        // Handle nested verdict object from backend
        if (typeof verdict === 'object' && verdict !== null) {
            confidence = typeof verdict.confidence !== 'undefined' ? verdict.confidence : confidence;
            verdict = verdict.verdict || "Unknown";
        }

        // Handle array of evidence from backend
        if (Array.isArray(evidence)) {
            if (evidence.length === 0) {
                evidence = "No matching evidence found in corpus.";
            } else {
                evidence = evidence.map(e => `• ${e.evidence} <em style="font-size: 0.85em; opacity: 0.8; display: block; margin-top: 4px;">— Source: ${e.source || 'Unknown'}</em>`).join('<div style="margin-bottom: 8px;"></div>');
            }
        }

        // Determine styling based on verdict
        let verdictClass = 'verdict-yellow';
        let verdictIcon = '<i class="fa-solid fa-triangle-exclamation"></i>';
        
        const vLower = String(verdict).toLowerCase();
        if (vLower.includes('supported') && !vLower.includes('weak') && !vLower.includes('un')) {
            verdictClass = 'verdict-green';
            verdictIcon = '<i class="fa-solid fa-check-circle"></i>';
        } else if (vLower.includes('unsupported') || vLower.includes('false') || vLower.includes('insufficient')) {
            verdictClass = 'verdict-red';
            verdictIcon = '<i class="fa-solid fa-xmark-circle"></i>';
        }

        // Format confidence (e.g., convert 0.95 to 95%)
        let confidenceDisplay = confidence;
        if (!isNaN(confidence) && parseFloat(confidence) <= 1.0) {
            confidenceDisplay = `${Math.round(parseFloat(confidence) * 100)}%`;
        } else if (!isNaN(confidence) && parseFloat(confidence) > 1.0) {
            confidenceDisplay = `${Math.round(parseFloat(confidence))}%`;
        }

        return `
            <div class="claim-card">
                <div class="claim-card-header">
                    <div class="claim-content">
                        <span class="claim-label">Original Claim</span>
                        <h4 class="claim-original">"${originalClaim}"</h4>
                        ${rewrittenClaim ? `<p class="claim-rewritten">Structured: ${rewrittenClaim}</p>` : ''}
                    </div>
                    <div class="claim-badges">
                        <div class="verdict-badge ${verdictClass}">
                            ${verdictIcon}
                            ${verdict}
                        </div>
                        <div class="confidence-score">
                            <i class="fa-solid fa-bullseye" style="margin-right: 4px;"></i>
                            Confidence: ${confidenceDisplay}
                        </div>
                    </div>
                </div>
                <div class="claim-evidence">
                    <div class="evidence-header">
                        <i class="fa-solid fa-vial-circle-check"></i>
                        Supporting Evidence
                    </div>
                    <p class="evidence-text">${evidence}</p>
                </div>
            </div>
        `;
    }

    function showError(msg) {
        loadingState.classList.add('hidden');
        errorState.classList.remove('hidden');
        errorMessage.textContent = msg;
    }
});
