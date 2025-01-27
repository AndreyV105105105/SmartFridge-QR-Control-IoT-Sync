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
                success: function(response) {
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
                        $('#calories').html('Калории: ' + ex['nutrition_info']["калории"]);
                        $('#proteins').html('Белки: ' + ex['nutrition_info']["белки"]);
                        $('#fats').html('Жиры: ' + ex['nutrition_info']["жиры"]);
                        $('#carbohydrates').html('Углеводы: ' + ex['nutrition_info']["углеводы"]);


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
                }
            });
        }
    });
});