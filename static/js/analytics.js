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
        const data = await response.json();
      	document.getElementById('str1').innerHTML = 'Всего товаров добавлено: ' + data.added_count;
      	document.getElementById('str2').innerHTML = 'Всего товаров удалено: ' + data.removed_count;
      	const container = document.getElementById('products-container');

        // Очищаем предыдущие результаты
        container.innerHTML = '';

        // Проверяем и обрабатываем список продуктов
        if (data.quantity_diffs && Array.isArray(data.quantity_diffs)) {
            data.quantity_diffs.forEach(item => {
                // Создаем элементы
                const div = document.createElement('div');
                div.className = 'product-item'; // для стилей

                const namePara = document.createElement('p');
                namePara.textContent = `Продукт: ${item.product_name}`;

                const addPara = document.createElement('p');
                addPara.textContent = `Добавлено: ${item.diff[0]}`;

                const dellPara = document.createElement('p');
                dellPara.textContent = `Удалено: ${item.diff[1]}`;

                // Добавляем элементы в div
                div.appendChild(namePara);
                div.appendChild(addPara);
                div.appendChild(dellPara);

                // Добавляем div в контейнер
                container.appendChild(div);
            });
        }

        return data;
        return data;
      });
};

