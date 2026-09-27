document.addEventListener('DOMContentLoaded', function() {
    // View management
    const views = {
        landing: document.getElementById('landingView'),
        extraction: document.getElementById('extractionView'),
        review: document.getElementById('reviewView')
    };

    function showView(viewName) {
        Object.values(views).forEach(view => {
            view.classList.remove('active');
        });
        views[viewName].classList.add('active');
    }

    // Navigation buttons
    document.getElementById('newInvoiceBtn').addEventListener('click', () => {
        showView('landing');
    });

    document.getElementById('historyBtn').addEventListener('click', () => {
        alert('History feature coming soon!');
    });

    // Example prompts
    document.querySelectorAll('.example-prompt').forEach(btn => {
        btn.addEventListener('click', () => {
            document.getElementById('customerRequest').value = btn.textContent.trim();
        });
    });

    // Generate invoice button
    document.getElementById('generateBtn').addEventListener('click', async () => {
        const text = document.getElementById('customerRequest').value;
        if (!text.trim()) {
            alert('Please enter a customer request');
            return;
        }

        const btn = document.getElementById('generateBtn');
        btn.querySelector('.btn-text').style.display = 'none';
        btn.querySelector('.btn-loader').style.display = 'inline';

        try {
            const response = await fetch('/api/extract', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text })
            });

            const data = await response.json();

            // Populate extraction view
            document.getElementById('extractedName').textContent = data.customer.name || '-';
            document.getElementById('extractedEmail').textContent = data.customer.email || '-';
            document.getElementById('extractedPhone').textContent = data.customer.phone || '-';

            const servicesContainer = document.getElementById('extractedServices');
            servicesContainer.innerHTML = data.items.map(item => `
                <div class="extraction-field">
                    <label>Service:</label>
                    <span>${item.service_name} (x${item.quantity})</span>
                </div>
            `).join('');

            if (data.unmatched_items && data.unmatched_items.length > 0) {
                document.getElementById('unmatchedSection').style.display = 'block';
                document.getElementById('unmatchedServices').innerHTML = data.unmatched_items.map(item => `
                    <div class="extraction-field">
                        <label>Unmatched:</label>
                        <span>${item}</span>
                    </div>
                `).join('');
            } else {
                document.getElementById('unmatchedSection').style.display = 'none';
            }

            showView('extraction');
        } catch (error) {
            alert('Error extracting data: ' + error.message);
        } finally {
            btn.querySelector('.btn-text').style.display = 'inline';
            btn.querySelector('.btn-loader').style.display = 'none';
        }
    });

    // Back button
    document.getElementById('backBtn').addEventListener('click', () => {
        showView('landing');
    });

    // Proceed to review button
    document.getElementById('proceedToReviewBtn').addEventListener('click', () => {
        // Populate review view with extracted data
        document.getElementById('reviewName').value = document.getElementById('extractedName').textContent;
        document.getElementById('reviewEmail').value = document.getElementById('extractedEmail').textContent;
        document.getElementById('reviewPhone').value = document.getElementById('extractedPhone').textContent;

        showView('review');
    });

    // Add item button
    document.getElementById('addItemBtn').addEventListener('click', () => {
        alert('Add item feature coming soon!');
    });
});
