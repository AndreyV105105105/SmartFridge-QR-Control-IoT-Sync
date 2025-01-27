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
                        $('#product_name').html(ex['название']);
                        $('#full_information').html(' Подробная информация: ');
                        $('#product_type').html(' Тип: ' + ex['тип']);
                        $('#manufacture_date').html(' Дата изготовления: ' + ex['дата_изготовления']);
                        $('#expiry_date').html(' Дата истечения срока годности: ' + ex['годен_до']);
                        $('#quantity_unit').html('масса/объем, ед. измерения: ' + ex['масса_объем'] + ', ' +  ex['ед_измерения']);
                        $('#measurement_type').html('Тип измерения: ' + ex['тип_измерения']);
                        $('#nutrition_info').html('Пищевая ценность: ');
                        $('#calories').html('Калории: ' + ex['пищевая_ценность']['калории']);
                        $('#proteins').html('Белки: ' + ex['пищевая_ценность']['белки']);
                        $('#fats').html('Жиры: ' + ex['пищевая_ценность']['жиры']);
                        $('#carbohydrates').html('Углеводы: ' + ex['пищевая_ценность']['углеводы']);


                    } else {
                        $('#product_name').html(response.message);
                    }
                },
                error: function(xhr, status, error) {
                    $('#product_name').html('Error processing image. Please try again.');
                }
            });
        }
    });
});