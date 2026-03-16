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
        if (!url) return;
        startAnalysis(url);
    });

    // Enter Key
    urlInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const url = urlInput.value.trim();
            if (url) startAnalysis(url);
        }
    });

    // Retry Button
    retryBtn.addEventListener('click', () => {
        const url = urlInput.value.trim();
        if (url) startAnalysis(url);
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
        // Reset states
        errorState.classList.add('hidden');
        resultsState.classList.add('hidden');
        loadingState.classList.remove('hidden');
        claimsList.innerHTML = '';
        analyzeBtn.disabled = true;
        
        // Start loading animation text
        cycleLoadingText();

        try {
            // Encode the URL parameter
            const encodedUrl = encodeURIComponent(url);
            const apiUrl = `http://localhost:8000/analyze_youtube?url=${encodedUrl}`;

            const response = await fetch(apiUrl, {
                method: 'GET', // or POST if required by backend, user asked for endpoint: return JSON
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`Server returned error status: ${response.status}`);
            }

            const data = await response.json();
            
            clearInterval(loadingInterval);
            renderResults(data);
            
        } catch (error) {
            console.error("Analysis Error:", error);
            clearInterval(loadingInterval);
            showError("Failed to connect to the analysis server. Please make sure the backend API is running.");
        } finally {
            analyzeBtn.disabled = false;
        }
    }

    function renderResults(data) {
        loadingState.classList.add('hidden');
        
        let claims = [];
        
        // Handle different possible JSON structures
        if (Array.isArray(data)) {
            claims = data;
        } else if (data.data && Array.isArray(data.data)) {
            claims = data.data;
        } else if (data.claims && Array.isArray(data.claims)) {
            claims = data.claims;
        } else {
            // Try to extract an array if the structure is unexpected
            claims = [data]; // Fallback
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
        
        // Scroll to results
        setTimeout(() => {
            resultsState.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }

    function createClaimCard(claim) {
        const originalClaim = claim.original_claim || claim.claim || claim.original || "Unknown Claim";
        const rewrittenClaim = claim.rewritten_claim || claim.rewritten || claim.structured_claim || "";
        const verdict = claim.verdict || claim.classification || "Unknown";
        const confidence = typeof claim.confidence_score !== 'undefined' ? claim.confidence_score : (claim.confidence || "N/A");
        const evidence = claim.supporting_evidence || claim.evidence || "No evidence provided.";

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
