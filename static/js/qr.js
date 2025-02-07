"use strict"
let json_item;


// функция для уменьшения количества товара в БД
async function delete_item(event) {
  event.preventDefault();
  let btn = document.getElementById('delete_btn');
  let data1 = btn.name.split('===');

  return fetch(`/del_item/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken()
    },
    body: JSON.stringify({
      product_name: data1[0],
      expiry_date: data1[1]
    })
  })
      .then(response => response.json()) // Парсим JSON из ответа
      .then(data => {
        $('#product_status_in_bd').html('Товар успешно удалён!');
        $('#number_of_item').html('Колличество товара в холодильнике: ' + data.number); // Используем значение из ответа
        return data;
      })
      .catch(error => {
        console.error('Error:', error);
      });
}

// функция для увелечения количества товара в БД
async function add_item(event) {
  event.preventDefault();
  let btn = document.getElementById('add_btn');
  let data1 = btn.name.split('===');

  return fetch(`/add_item/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken()
    },
    body: JSON.stringify({
      product_name: data1[0],
      expiry_date: data1[1]
    })
  })
      .then(response => response.json()) // Парсим JSON из ответа
      .then(data => {
        $('#product_status_in_bd').html('Товар успешно добавлен!');
        $('#number_of_item').html('Колличество товара в холодильнике: ' + data.number); // Используем значение из ответа
        return data;
      })
      .catch(error => {
        console.error('Error:', error);
      });
}

// функция для получения информации о товаре из БД
function use_bd(product_name, expiry_date) {
  return fetch(`/usebd/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken()
    },
    body: JSON.stringify({
      product_name: product_name,
      expiry_date: expiry_date
    })
  }).then(async (response) => {
    return await response.json();
  });
}

// функция для добавления товара в БД
function add_product(product_name, product_type, manufacture_date, expiry_date, quantity, unit, nutrition_info, measurement_type) {
  return fetch(`/addproduct/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken()
    },
    body: JSON.stringify({
      product_name: product_name,
      product_type: product_type,
      manufacture_date: manufacture_date,
      expiry_date: expiry_date,
      quantity: quantity,
      unit: unit,
      nutrition_info: nutrition_info,
      measurement_type: measurement_type
    })
  })
}


function getCSRFToken() {
  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
  return csrfToken ? csrfToken.value : '';
}

// функция для сканирования QR и вывода информации о нём
$(document).ready(function() {
  $('#openCameraButton').click(function() {
    $('#cameraInput').click();
  });

  $('#cameraInput').change(function(event) {
    var file = event.target.files[0];
    if (file) {
      var formData = new FormData();
      formData.append('image', file);

      $.ajax({
        url: '/upload',
        type: 'POST',
        data: formData,
        contentType: false,
        processData: false,
        success: async function(response) {
          if (response.success) {
            var ex = JSON.parse(response.qr_data);
            $('#product_name').html(ex['product_name']);
            $('#full_information').html(' Подробная информация: ');
            $('#product_type').html(' Тип: ' + ex['product_type']);
            $('#manufacture_date').html(' Дата изготовления: ' + ex['manufacture_date']);
            $('#expiry_date').html(' Дата истечения срока годности: ' + ex['expiry_date']);
            $('#quantity_unit').html('масса/объем, ед. измерения: ' + ex['quantity'] + ', ' +  ex['unit']);
            $('#measurement_type').html('Тип измерения: ' + ex['measurement_type']);
            $('#nutrition_info').html('Пищевая ценность: ');
            $('#calories').html('Калории: ' + ex['nutrition_info']["calories"]);
            $('#proteins').html('Белки: ' + ex['nutrition_info']["proteins"]);
            $('#fats').html('Жиры: ' + ex['nutrition_info']["fats"]);
            $('#carbohydrates').html('Углеводы: ' + ex['nutrition_info']["carbohydrates"]);
            $('#product_status_in_bd').html('');
            const item = await use_bd(ex['product_name'], ex['expiry_date']);

            if (!item){
              add_product(ex['product_name'], ex['product_type'], ex['manufacture_date'], ex['expiry_date'], ex['quantity'], ex['unit'], ex['nutrition_info'], ex['measurement_type'])
              $('#product_status_in_bd').html('ДОБАВЛЕНО');}
            else if(item.number === 0){
              fetch(`/add_item/`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                  product_name: item.product_name,
                  expiry_date: item.expiry_date
                })
              })
                  .then(response => response.json()) // Парсим JSON из ответа
                  .then(data => {
                    $('#product_status_in_bd').html('ДОБАВЛЕНО');
                    // $('#number_of_item').html('Колличество товара в холодильнике: ' + data.number);
                    return data;
                  })
                  .catch(error => {
                    console.error('Error:', error);
                  });
            }
            else{
              let delete_btn = document.getElementById('delete_btn');
              let add_btn = document.getElementById('add_btn');
              delete_btn.classList.remove('hidden');
              delete_btn.disabled = false;
              add_btn.classList.remove('hidden');
              add_btn.disabled = false;
              delete_btn.setAttribute('name', `${ex['product_name']}===${ex['expiry_date']}`);
              add_btn.setAttribute('name', `${ex['product_name']}===${ex['expiry_date']}`);



            }

          } else {
            $('#product_name').html(response.message);
            $('#full_information').html('');
            $('#product_type').html('');
            $('#manufacture_date').html('');
            $('#expiry_date').html('');
            $('#quantity_unit').html('');
            $('#measurement_type').html('');
            $('#nutrition_info').html('');
            $('#calories').html('');
            $('#proteins').html('');
            $('#fats').html('');
            $('#carbohydrates').html('');
            $('#product_status_in_bd').html('');
          }
        },
        error: function(xhr, status, error) {
          $('#product_name').html('Error processing image. Please try again.');
          $('#full_information').html('');
          $('#product_type').html('');
          $('#manufacture_date').html('');
          $('#expiry_date').html('');
          $('#quantity_unit').html('');
          $('#measurement_type').html('');
          $('#nutrition_info').html('');
          $('#calories').html('');
          $('#proteins').html('');
          $('#fats').html('');
          $('#carbohydrates').html('');
          $('#product_status_in_bd').html('');
        }
      });
    }
  });
});