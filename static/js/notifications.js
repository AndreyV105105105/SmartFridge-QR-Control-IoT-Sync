"use strict"

function getCSRFToken() {
  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
  return csrfToken ? csrfToken.value : '';
}

// функция для удаления прочитанных уведомлений
document.querySelectorAll('.notification-card button').forEach(button => {
    button.addEventListener('click', function() {
        const notification_card = this.closest('.notification-card');
        const productId = notification_card.dataset.productId;
        fetch(`/mark_as_read/${productId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => {
            if (response.ok) {
                notification_card.remove();
                location. reload();
            }
        });
    });
});