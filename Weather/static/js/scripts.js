// City autocomplete from Weather API

document.addEventListener('DOMContentLoaded', function () {
    const cityInput = document.getElementById('id_city');
    const cityResults = document.getElementById('city-results');
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    cityInput.addEventListener('input', function () {
        const query = cityInput.value;
        if (query.length >= 3) {
            fetch('/autocomplete/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken, // Передача CSRF-токену
                },
                body: JSON.stringify({query: query}),
            })
                .then(response => response.json())
                .then(data => {
                    cityResults.innerHTML = '';
                    if (data.length > 0) {
                        data.forEach(item => {
                            const resultItem = document.createElement('li');
                            resultItem.textContent = item.name + ', ' + item.country;
                            resultItem.classList.add('dropdown-item');
                            cityResults.appendChild(resultItem);

                            resultItem.addEventListener('click', function () {
                                cityInput.value = item.name;
                                cityResults.classList.remove('show');
                                while (cityResults.firstChild) {
                                    cityResults.removeChild(cityResults.firstChild);
                                }
                            });
                        });
                        cityResults.classList.add('show');
                    } else {
                        cityResults.classList.remove('show');
                    }
                })
                .catch(error => console.error(error));
        } else {
            cityResults.classList.remove('show');
            cityResults.innerHTML = '';
        }
    });

    document.addEventListener('click', function (event) {
        if (!cityResults.contains(event.target)) {
            cityResults.classList.remove('show');
            cityResults.innerHTML = '';
        }
    });
});
