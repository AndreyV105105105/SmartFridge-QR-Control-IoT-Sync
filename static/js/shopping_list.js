"use strict"

function getCSRFToken() {
  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
  return csrfToken ? csrfToken.value : '';
}


function shopping_list_add(product_name, quantity) {
  return fetch(`/addtoshoppinglist/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken()
    },
    body: JSON.stringify({
      product_name: product_name,
      quantity: quantity
    })
  }).then(async (response) => {
    return await response.json();
  });
}


function shopping_list_update(product_name, quantity) {
  return fetch(`/updateshopinglistquantity/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken()
    },
    body: JSON.stringify({
      product_name: product_name,
      quantity: quantity
    })
  }).then(async (response) => {
    return await response.json();
  });
}


function shopping_list_remove(product_name) {
  return fetch(`/removefromshoppinglist/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken()
    },
    body: JSON.stringify({
      product_name: product_name
    })
  }).then(async (response) => {
    return await response.json();
  });
}

const cart = {};

function handleCart(button) {
    const product = button.closest('.product-card');
    const quantityElement = product.querySelector('.quantity');
    const productId = product.dataset.productId;
    shopping_list_add(product.dataset.name, 1)
      .then(() => {
        button.style.display = 'none';
        product.querySelector('.quantity-controls').style.display = 'flex';
        product.dataset.quantity = 1;
        quantityElement.textContent = 1;
        saveCartState(productId);
      });
}

function updateQuantity(button, change) {
    const product = button.closest('.product-card');
    const quantityElement = product.querySelector('.quantity');
    let quantity = parseInt(product.dataset.quantity);
    const productId = product.dataset.productId;
    console.log(quantity)
    quantity += change;
    if (quantity < 1) {
        shopping_list_remove(product.dataset.name)
          .then(() => {
            const allStates = JSON.parse(localStorage.getItem('cartStates')) || {};
            delete allStates[productId];
            localStorage.setItem('cartStates', JSON.stringify(allStates));

            product.querySelector('.add-btn').style.display = 'block';
            product.querySelector('.quantity-controls').style.display = 'none';
            product.dataset.quantity = 0;
          });
        return;
    }

    shopping_list_update(product.dataset.name, quantity)
      .then(() => {
        product.dataset.quantity = quantity;
        quantityElement.textContent = quantity;
        saveCartState(productId);
      });
}



function saveCartState(productId) {
  const productBlock = document.querySelector(`[data-product-id="${productId}"]`);
  const quantityControls = productBlock.querySelector('.quantity-controls');
  const quantity = productBlock.querySelector('.quantity').textContent;

  const state = {
    isVisible: quantityControls.style.display !== 'none',
    quantity: parseInt(quantity)
  };

  // Сохраняем все состояния в объекте
  const allStates = JSON.parse(localStorage.getItem('cartStates')) || {};
  allStates[productId] = state;
  localStorage.setItem('cartStates', JSON.stringify(allStates));
}


// Восстановление состояния (исправленный селектор)
document.addEventListener('DOMContentLoaded', () => {
  const allStates = JSON.parse(localStorage.getItem('cartStates')) || {};

  // Меняем .product на .product-card
  document.querySelectorAll('.product-card').forEach(productBlock => {
    const productId = productBlock.dataset.productId;
    const state = allStates[productId];

    if (state) {
      const quantityControls = productBlock.querySelector('.quantity-controls');
      const quantityElement = productBlock.querySelector('.quantity');
      const addButton = productBlock.querySelector('.add-btn');

      // Обновляем все связанные свойства
      quantityControls.style.display = state.isVisible ? 'flex' : 'none';
      addButton.style.display = state.isVisible ? 'none' : 'block';
      quantityElement.textContent = state.quantity;
      productBlock.dataset.quantity = state.quantity; // Важно обновить data-атрибут
    }
  });
});
