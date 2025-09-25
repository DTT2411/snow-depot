var stripe_public_key = $('#id_stripe_public_key').text().slice(1, -1);
var client_secret = $('#id_client_secret').text().slice(1, -1);
var stripe = Stripe(stripe_public_key);
var elements = stripe.elements();
var style = {
    base: {
        color: '#1C3738',
        fontFamily: '"DM Sans", sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4'
        }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};
var card = elements.create('card', {style: style});
card.mount('#card-element');

// Handle validation errors on card element
card.addEventListener('change', function (event) {
    var errorDiv = document.getElementById('card-errors')
    if (event.error) {
        var html_to_insert = `
            <span class="icon" role="alert">
                <i class="fas fa-exclamation"></i>
            </span>
            <span>${event.error.message}</span>
        `
        $(errorDiv).html(html_to_insert);
    } else {
        errorDiv.textContent = '';
    }
})