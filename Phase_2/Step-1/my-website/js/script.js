let loggedInUser = null;

function showLogin() {
    document.getElementById('login-form').style.display = 'block';
    document.getElementById('products').style.display = 'none';
}

function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    // Test credentials by making a request to the API
    fetch('https://vk5qbe6nh9.execute-api.us-west-2.amazonaws.com/prod/cart', {
        method: 'GET',
        headers: {
            'Authorization': `${username}:${password}`
        }
    })
    .then(response => {
        if (response.status === 200) {
            loggedInUser = { username, password };
            document.getElementById('user-status').innerText = `Logged in as ${username}`;
            document.getElementById('login-btn').style.display = 'none';
            document.getElementById('logout-btn').style.display = 'inline';
            document.getElementById('login-form').style.display = 'none';
            document.getElementById('products').style.display = 'block';
            fetchCart();
        } else {
            throw new Error('Invalid credentials');
        }
    })
    .catch(err => {
        document.getElementById('login-error').innerText = err.message || 'Login failed';
    });
}

function logout() {
    loggedInUser = null;
    document.getElementById('user-status').innerText = 'Not logged in';
    document.getElementById('login-btn').style.display = 'inline';
    document.getElementById('logout-btn').style.display = 'none';
    document.getElementById('cart-status').innerText = 'Cart is empty';
    document.getElementById('cart-items').innerHTML = '';
}

function addToCart(itemId, itemName, price) {
    if (!loggedInUser) {
        alert('Please log in to add items to cart');
        return;
    }
    fetch('https://vk5qbe6nh9.execute-api.us-west-2.amazonaws.com/prod/cart', {
        method: 'POST',
        headers: {
            'Authorization': `${loggedInUser.username}:${loggedInUser.password}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            itemId: itemId,
            itemName: itemName,
            price: price,
            quantity: 1
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('cart-status').innerText = data.message || 'Item added to cart!';
        fetchCart();
    })
    .catch(err => {
        document.getElementById('cart-status').innerText = 'Error adding item';
    });
}

function fetchCart() {
    if (!loggedInUser) return;
    fetch('https://vk5qbe6nh9.execute-api.us-west-2.amazonaws.com/prod/cart', {
        method: 'GET',
        headers: {
            'Authorization': `${loggedInUser.username}:${loggedInUser.password}`
        }
    })
    .then(response => response.json())
    .then(data => {
        const cartItems = document.getElementById('cart-items');
        cartItems.innerHTML = '';
        if (data.items && Object.keys(data.items).length > 0) {
            for (const [itemId, details] of Object.entries(data.items)) {
                const li = document.createElement('li');
                li.innerText = `${details.itemName}: $${details.price} (Qty: ${details.quantity})`;
                cartItems.appendChild(li);
            }
        } else {
            document.getElementById('cart-status').innerText = 'Cart is empty';
        }
    })
    .catch(err => {
        document.getElementById('cart-status').innerText = 'Error fetching cart';
    });
}