document.getElementById('contact-form').addEventListener('submit', async function (e) {
    e.preventDefault();

    const form = e.target;
    const data = new FormData(form);
    const responseElement = document.getElementById('response');

    try {
        const response = await fetch('https://formspree.io/f/xgvwvyyy', {
            method: 'POST',
            body: data,
            headers: {
                'Accept': 'application/json'
            }
        });

        if (response.ok) {
            responseElement.textContent = 'Thank you for your message. We will get back to you soon!';
            form.reset();
        } else {
            responseElement.textContent = 'Oops! There was a problem submitting your form.';
        }
    } catch (error) {
        responseElement.textContent = 'Oops! There was a problem submitting your form.';
    }
});
