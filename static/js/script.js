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
                        $('#result').html('QR Code Data: ' + response.qr_data);
                    } else {
                        $('#result').html(response.message);
                    }
                },
                error: function(xhr, status, error) {
                    $('#result').html('Error processing image. Please try again.');
                }
            });
        }
    });
});