"use strict"


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


function getCSRFToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfToken ? csrfToken.value : '';
}


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
                        const ex = JSON.parse(response.qr_data)
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
                        const item = await use_bd(ex['product_name'], ex['expiry_date']);
                        console.log(item);
                        $('#test').html(item['product_name']);

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
                        $('#test').html('');
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
                    $('#test').html('');
                }
            });
        }
    });
});