// UET Data Science Portal JavaScript Helpers

document.addEventListener('DOMContentLoaded', function() {
    // Auto dismiss messages after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // AJAX Upvote Handler
    const upvoteForms = document.querySelectorAll('.upvote-form');
    upvoteForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const btn = form.querySelector('.btn-upvote');
            const countSpan = form.querySelector('.upvote-count');
            const url = form.action;
            const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                    return;
                }
                return response.json();
            })
            .then(data => {
                if (data) {
                    countSpan.textContent = data.total_upvotes;
                    if (data.upvoted) {
                        btn.classList.add('active');
                    } else {
                        btn.classList.remove('active');
                    }
                }
            })
            .catch(error => {
                console.error('Error upvoting:', error);
                form.submit(); // fallback to standard submit if fetch fails
            });
        });
    });
});
