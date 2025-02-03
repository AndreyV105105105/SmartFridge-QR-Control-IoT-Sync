"use strict"

function getCSRFToken() {
  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
  return csrfToken ? csrfToken.value : '';
}


butt.onclick = function() {
		const start_date = document.getElementById('start_date').value;
		const end_date = document.getElementById('end_date').value;
		return fetch(`/getanalytics/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
          start_date: start_date,
          end_date: end_date
        })
      }).then(async (response) => {
        console.log(response.json());
//      	document.getElementById('str').innerHTML="Вы ввели: " + start_date + end_date;
        return await response.json();
      });
};

