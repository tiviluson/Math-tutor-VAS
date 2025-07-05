
// Send message on Enter key press without Shift
document.addEventListener('DOMContentLoaded', function () {
    const input = document.querySelector('.chat-input');
    const button = document.getElementById('loading-button');

    if (input && button) {
        input.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault(); // prevent newline
                button.click();     // trigger button
            }
        });
    }
});

