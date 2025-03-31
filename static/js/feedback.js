document.addEventListener('DOMContentLoaded', function() {
    const feedbackContainer = document.getElementById('feedback-container');
    
    // Display feedback/corrections
    window.displayFeedback = function(corrections) {
        if (!corrections || corrections.length === 0) {
            return;
        }
        
        // Clear previous feedback
        feedbackContainer.innerHTML = '<h5 class="h6 mb-2">Recent Corrections</h5>';
        
        // Create feedback elements
        corrections.forEach(correction => {
            const card = document.createElement('div');
            card.className = 'correction-card card bg-warning bg-opacity-10 mb-2';
            
            const cardBody = document.createElement('div');
            cardBody.className = 'card-body py-2 px-3';
            
            const original = document.createElement('p');
            original.className = 'mb-1 small';
            original.innerHTML = `<span class="text-danger"><del>${correction.original}</del></span>`;
            
            const corrected = document.createElement('p');
            corrected.className = 'mb-1 small';
            corrected.innerHTML = `<span class="text-success">${correction.corrected}</span>`;
            
            const explanation = document.createElement('p');
            explanation.className = 'mb-0 small text-muted';
            explanation.textContent = correction.explanation;
            
            cardBody.appendChild(original);
            cardBody.appendChild(corrected);
            cardBody.appendChild(explanation);
            card.appendChild(cardBody);
            
            feedbackContainer.appendChild(card);
        });
    };
});
