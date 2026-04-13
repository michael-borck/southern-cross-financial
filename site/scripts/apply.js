/* Company site — inline job application form handler.
 *
 * POSTs to the WorkReady API's /api/v1/resume endpoint (same pipeline
 * as seek.jobs Quick Apply). The API URL is read from the form's
 * data-api-base attribute.
 *
 * This script is shared across all 6 company sites — each site includes
 * a copy in its site/scripts/ directory. The form markup and CSS classes
 * are consistent across sites; only the visual theme differs.
 */

(function () {
    'use strict';

    var form = document.getElementById('apply-form');
    if (!form) return;

    var resultEl = document.getElementById('apply-result');
    var submitBtn = form.querySelector('button[type="submit"]');
    var apiBase = form.getAttribute('data-api-base') || 'https://workready-api.eduserver.au';

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        var fd = new FormData();
        fd.append('posting_id', form.querySelector('[name="posting_id"]').value);
        fd.append('job_title', form.querySelector('[name="job_title"]').value);
        fd.append('applicant_name', form.querySelector('[name="applicant_name"]').value);
        fd.append('applicant_email', form.querySelector('[name="applicant_email"]').value);
        fd.append('cover_letter', form.querySelector('[name="cover_letter"]').value || '');
        fd.append('source', 'company_site');

        var resumeInput = form.querySelector('[name="resume"]');
        if (resumeInput && resumeInput.files[0]) {
            fd.append('resume', resumeInput.files[0]);
        } else {
            showResult('Please attach your resume (PDF).', 'error');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = 'Submitting…';
        hideResult();

        fetch(apiBase + '/api/v1/resume', { method: 'POST', body: fd })
            .then(function (r) {
                if (r.ok) return r.json();
                throw new Error('Submission failed — please try again.');
            })
            .then(function (data) {
                showResult(
                    'Application submitted! Check your WorkReady portal inbox for the outcome.',
                    'success'
                );
                form.reset();
            })
            .catch(function (err) {
                showResult(err.message, 'error');
            })
            .finally(function () {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Submit application';
            });
    });

    function showResult(msg, type) {
        if (!resultEl) return;
        resultEl.textContent = msg;
        resultEl.className = 'apply-result apply-result-' + type;
        resultEl.style.display = 'block';
    }

    function hideResult() {
        if (resultEl) resultEl.style.display = 'none';
    }
})();
