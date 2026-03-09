document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const uploadForm = document.getElementById("upload-form");
    const videoFileInput = document.getElementById("video-file");
    const analyzeBtn = document.getElementById("analyze-btn");
    const loadingState = document.getElementById("loading-state");
    const videoContainer = document.getElementById("video-container");
    const sourceVideo = document.getElementById("source-video");
    const resultsDashboard = document.getElementById("results-dashboard");

    // Verdict Elements
    const verdictIcon = document.getElementById("verdict-icon");
    const verdictText = document.getElementById("verdict-text");
    const verdictDisplay = document.getElementById("verdict-display");
    
    // Score Elements
    const scoreNumber = document.getElementById("score-number");
    const scoreRating = document.getElementById("score-rating");
    
    // Stats Elements
    const statClaims = document.getElementById("stat-claims");
    const statConflicts = document.getElementById("stat-conflicts");
    const statManipulation = document.getElementById("stat-manipulation");
    
    // Lists & Containers
    const conflictsSection = document.getElementById("conflicts-section");
    const conflictsList = document.getElementById("conflicts-list");
    const claimsContainer = document.getElementById("claims-container");
    const disclaimerText = document.getElementById("disclaimer-text");

    // Handle Upload & Analysis
    uploadForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const file = videoFileInput.files[0];
        if (!file) return;

        // 1. Show Local Video in Player Immediately
        const videoURL = URL.createObjectURL(file);
        sourceVideo.src = videoURL;
        videoContainer.classList.remove("hidden");

        // 2. Prepare UI for loading
        analyzeBtn.disabled = true;
        analyzeBtn.textContent = "Uploading...";
        loadingState.classList.remove("hidden");
        resultsDashboard.classList.add("hidden");

        // Clear previous results
        conflictsList.innerHTML = "";
        claimsContainer.innerHTML = "";
        verdictDisplay.className = "verdict-display";

        // 3. Send file to backend
        const formData = new FormData();
        formData.append("video", file);

        try {
            analyzeBtn.textContent = "Processing Pipeline...";
            
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Server error during analysis');
            }

            const data = await response.json();
            
            // 4. Render Results
            renderDashboard(data);
            
            // Show Results & Reset UI
            resultsDashboard.classList.remove("hidden");
            loadingState.classList.add("hidden");
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = "Analyze Another Video";

        } catch (error) {
            console.error(error);
            alert(`Analysis Failed: ${error.message}`);
            loadingState.classList.add("hidden");
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = "Retry Upload";
        }
    });


    // Render the Dashboard Logic
    function renderDashboard(data) {
        const analysis = data.video_analysis;
        
        // 1. Render Overview Stats
        statClaims.textContent = analysis.total_claims_analyzed;
        statConflicts.textContent = analysis.logical_conflicts.length;
        statManipulation.textContent = analysis.manipulative_sentences_detected;
        
        // 2. Render Overall Verdict
        const verdict = analysis.overall_verdict;
        verdictText.textContent = verdict;
        
        if (verdict === "VERIFIED") {
            verdictDisplay.classList.add("verified");
            verdictIcon.textContent = "✅";
        } else if (verdict === "MISLEADING") {
            verdictDisplay.classList.add("misleading");
            verdictIcon.textContent = "⚠️";
        } else if (verdict === "FALSE / MISLEADING" || verdict === "FALSE") {
            verdictDisplay.classList.add("false");
            verdictIcon.textContent = "🚨";
        }

        // 3. Render Credibility Score
        const score = analysis.creator_credibility.score;
        scoreNumber.textContent = score;
        scoreRating.textContent = analysis.creator_credibility.rating;
        
        if (score < 50) {
            scoreNumber.style.color = "var(--clr-danger)";
        } else if (score < 80) {
            scoreNumber.style.color = "var(--clr-warning)";
        } else {
            scoreNumber.style.color = "var(--clr-success)";
        }
        
        // 4. Render Logical Conflicts if any
        if (analysis.logical_conflicts.length > 0) {
            conflictsSection.classList.remove("hidden");
            analysis.logical_conflicts.forEach(conflict => {
                const item = document.createElement("div");
                item.className = "conflict-item";
                item.innerHTML = `
                    <p><strong>Claim A:</strong> ${conflict.claim_1}</p>
                    <p><strong>Claim B:</strong> ${conflict.claim_2}</p>
                    <p style="color: var(--clr-text-light); font-size: 0.8rem; margin-top:0.25rem;">AI Confidence: ${conflict.confidence * 100}%</p>
                `;
                conflictsList.appendChild(item);
            });
        }

        // 5. Render Claim-by-Claim Breakdown
        data.claims_breakdown.forEach(claim => {
            const card = document.createElement("div");
            card.className = "claim-card box-shadow";
            
            // Format Verdict Style
            let verdictClass = "unverified";
            if (claim.verdict === "VERIFIED" || claim.verdict === "TRUE") verdictClass = "verified";
            else if (claim.verdict.includes("MISLEADING")) verdictClass = "misleading";
            else if (claim.verdict.includes("FALSE")) verdictClass = "false";
            
            // Manipulation Flag
            let manipulationHTML = "";
            if (claim.manipulation_analysis.is_flagged) {
                const cats = claim.manipulation_analysis.manipulation_categories.join(", ");
                manipulationHTML = `
                    <div class="manipulation-flag">
                        <strong>⚠️ Misinformation Flags:</strong> Formatted with pattern [${cats}]
                    </div>
                `;
            }

            // Evidence HTML
            let evidenceHTML = `<div class="evidence-list"><h4>Supported By Evidence:</h4>`;
            if (claim.evidence && claim.evidence.length > 0) {
                claim.evidence.forEach(ev => {
                    evidenceHTML += `
                        <div class="evidence-item">
                            <span class="evidence-source">${ev.source}</span>
                            <span>${ev.text}</span>
                        </div>
                    `;
                });
            } else {
                evidenceHTML += `<p style="font-size:0.85rem; color:var(--clr-text-light);">No external medical evidence found.</p>`;
            }
            evidenceHTML += "</div>";

            // Card Structure
            card.innerHTML = `
                <div class="claim-header">
                    <div class="claim-content">
                        <!-- Clickable Timestamp -->
                        <button class="timestamp-btn" data-time="${claim.timestamp.start}" title="Play Video from this timestamp">
                            ▶ ${(claim.timestamp.start).toFixed(2)}s - ${(claim.timestamp.end).toFixed(2)}s
                        </button>
                        
                        <p class="original-claim">"${claim.original_sentence}"</p>
                        <p class="normalized-claim">Normalized: ${claim.normalized_claim}</p>
                    </div>
                    <div class="claim-verdict ${verdictClass}">${claim.verdict}</div>
                </div>
                
                ${manipulationHTML}

                <div class="explanations-area">
                    <div class="expl-toggles">
                        <button class="expl-btn active-mode" data-target="simplified">Simplified Context</button>
                        <button class="expl-btn" data-target="detailed">Detailed Analysis</button>
                    </div>
                    <div class="expl-content" data-simplified="${claim.explanations.simplified.replace(/"/g, '&quot;')}" data-detailed="${claim.explanations.detailed.replace(/"/g, '&quot;')}">
                        ${claim.explanations.simplified}
                    </div>
                </div>
                ${evidenceHTML}
            `;
            
            claimsContainer.appendChild(card);
            
            // Hook up Explanation Toggles
            const toggles = card.querySelectorAll(".expl-btn");
            const contentBox = card.querySelector(".expl-content");
            toggles.forEach(btn => {
                btn.addEventListener("click", (e) => {
                    toggles.forEach(t => t.classList.remove("active-mode"));
                    e.target.classList.add("active-mode");
                    const targetTextType = e.target.dataset.target;
                    contentBox.textContent = contentBox.dataset[targetTextType];
                });
            });

            // Hook up Timestamp Sync logic
            const timeBtn = card.querySelector(".timestamp-btn");
            timeBtn.addEventListener("click", () => {
                // Seek video to the exact start second
                sourceVideo.currentTime = parseFloat(timeBtn.dataset.time);
                sourceVideo.play();
                // Scroll player into view smoothly
                sourceVideo.scrollIntoView({ behavior: 'smooth', block: 'center' });
            });
        });

        // 6. Disclaimer
        disclaimerText.textContent = data.disclaimer;
    }
});
