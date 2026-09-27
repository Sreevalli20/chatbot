document.addEventListener('DOMContentLoaded', function() {
    // View management
    const views = {
        landing: document.getElementById('landingView'),
        extraction: document.getElementById('extractionView'),
        review: document.getElementById('reviewView')
    };

    // Store extracted data globally
    let extractedData = null;
    let currentInvoiceId = null;

    function showView(viewName) {
        Object.values(views).forEach(view => {
            view.classList.remove('active');
        });
        views[viewName].classList.add('active');
    }

    // Navigation buttons
    document.getElementById('newInvoiceBtn').addEventListener('click', () => {
        showView('landing');
        document.getElementById('customerRequest').value = '';
        extractedData = null;
        currentInvoiceId = null;
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

            if (!response.ok) {
                throw new Error('Extraction failed');
            }

            const data = await response.json();
            extractedData = data;

            // Populate extraction view
            document.getElementById('extractedName').textContent = data.customer.name || '-';
            document.getElementById('extractedEmail').textContent = data.customer.email || '-';
            document.getElementById('extractedPhone').textContent = data.customer.phone || '-';

            const servicesContainer = document.getElementById('extractedServices');
            if (data.items && data.items.length > 0) {
                servicesContainer.innerHTML = data.items.map(item => `
                    <div class="extraction-field">
                        <label>Service:</label>
                        <span>${item.service_name} (x${item.quantity}) - INR ${item.unit_price.toFixed(2)}/unit</span>
                    </div>
                `).join('');
            } else {
                servicesContainer.innerHTML = '<div class="extraction-field"><span>No services matched</span></div>';
            }

            if (data.unmatched_services && data.unmatched_services.length > 0) {
                document.getElementById('unmatchedSection').style.display = 'block';
                document.getElementById('unmatchedServices').innerHTML = data.unmatched_services.map(item => `
                    <div class="extraction-field warning">
                        <label>Unmatched:</label>
                        <span>${item} (not in catalogue)</span>
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
    document.getElementById('proceedToReviewBtn').addEventListener('click', async () => {
        if (!extractedData) {
            alert('No extracted data available');
            return;
        }

        const btn = document.getElementById('proceedToReviewBtn');
        btn.textContent = 'Creating Invoice...';
        btn.disabled = true;

        try {
            // Calculate discount amount from percentage
            let discountAmount = 0;
            if (extractedData.discount && extractedData.discount > 0) {
                const subtotal = extractedData.items.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0);
                discountAmount = (subtotal * extractedData.discount) / 100;
            }

            // Create the invoice
            const invoiceResponse = await fetch('/api/invoices', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    customer: extractedData.customer,
                    items: extractedData.items,
                    notes: extractedData.notes,
                    discount: discountAmount
                })
            });

            if (!invoiceResponse.ok) {
                throw new Error('Failed to create invoice');
            }

            const invoice = await invoiceResponse.json();
            currentInvoiceId = invoice.id;

            // Populate review view
            document.getElementById('reviewName').value = invoice.customer.name;
            document.getElementById('reviewEmail').value = invoice.customer.email;
            document.getElementById('reviewPhone').value = invoice.customer.phone || '';

            // Populate items
            const itemsContainer = document.getElementById('reviewItems');
            itemsContainer.innerHTML = invoice.items.map((item, index) => `
                <div class="review-item">
                    <div class="review-field">
                        <label>Service:</label>
                        <span>${item.service_name}</span>
                    </div>
                    <div class="review-field">
                        <label>Description:</label>
                        <span>${item.description}</span>
                    </div>
                    <div class="review-field">
                        <label>Quantity:</label>
                        <span>${item.quantity}</span>
                    </div>
                    <div class="review-field">
                        <label>Unit Price:</label>
                        <span>INR ${item.unit_price.toFixed(2)}</span>
                    </div>
                    <div class="review-field">
                        <label>Tax Rate:</label>
                        <span>${item.tax_rate}%</span>
                    </div>
                    <div class="review-field">
                        <label>Amount:</label>
                        <span>INR ${(item.quantity * item.unit_price).toFixed(2)}</span>
                    </div>
                </div>
            `).join('');

            // Populate totals
            document.getElementById('reviewSubtotal').textContent = `INR ${invoice.subtotal.toFixed(2)}`;
            document.getElementById('reviewDiscount').value = invoice.discount;
            document.getElementById('reviewTax').textContent = `INR ${invoice.tax.toFixed(2)}`;
            document.getElementById('reviewTotal').textContent = `INR ${invoice.total.toFixed(2)}`;

            // Update status badge
            document.getElementById('reviewStatus').textContent = invoice.status;
            document.getElementById('reviewStatus').className = 'badge badge-warning';

            showView('review');
        } catch (error) {
            alert('Error creating invoice: ' + error.message);
        } finally {
            btn.textContent = 'Proceed to Review';
            btn.disabled = false;
        }
    });

    // Cancel button
    document.getElementById('cancelBtn').addEventListener('click', () => {
        showView('landing');
        extractedData = null;
        currentInvoiceId = null;
    });

    // Approve button
    document.getElementById('approveBtn').addEventListener('click', async () => {
        if (!currentInvoiceId) {
            alert('No invoice to approve');
            return;
        }

        const btn = document.getElementById('approveBtn');
        btn.textContent = 'Approving...';
        btn.disabled = true;

        try {
            // First update the invoice with any changes
            const updateData = {
                customer: {
                    name: document.getElementById('reviewName').value,
                    email: document.getElementById('reviewEmail').value,
                    phone: document.getElementById('reviewPhone').value || null
                },
                discount: parseFloat(document.getElementById('reviewDiscount').value) || 0
            };

            const updateResponse = await fetch(`/api/invoices/${currentInvoiceId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updateData)
            });

            if (!updateResponse.ok) {
                throw new Error('Failed to update invoice');
            }

            // Then approve it
            const approveResponse = await fetch(`/api/invoices/${currentInvoiceId}/approve`, {
                method: 'POST'
            });

            if (!approveResponse.ok) {
                throw new Error('Failed to approve invoice');
            }

            const approvedInvoice = await approveResponse.json();

            // Update status badge
            document.getElementById('reviewStatus').textContent = approvedInvoice.status;
            document.getElementById('reviewStatus').className = 'badge badge-success';

            // Download PDF
            const pdfResponse = await fetch(`/api/invoices/${currentInvoiceId}/pdf`);
            if (!pdfResponse.ok) {
                throw new Error('Failed to generate PDF');
            }

            const blob = await pdfResponse.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${approvedInvoice.invoice_number}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            alert('Invoice approved and PDF downloaded successfully!');
        } catch (error) {
            alert('Error: ' + error.message);
        } finally {
            btn.textContent = 'Approve & Generate PDF';
            btn.disabled = false;
        }
    });

    // Add item button (placeholder)
    document.getElementById('addItemBtn').addEventListener('click', () => {
        alert('To add items, please go back and describe additional services in your request.');
    });
});
