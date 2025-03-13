function generate_sentiment() {
    fetch('/generate-sentiment', {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                document.getElementById('result3').innerText = data.message;
            } else if (data.error) {
                document.getElementById('result3').innerText = 'Error: ' + data.error;
            }
        })
        .catch(error => console.error('Error:', error));
}

document.addEventListener('DOMContentLoaded', function() {
    loadSentiments();

    document.getElementById('searchInput').addEventListener('input', filterSentiments);
    document.getElementById('teamFilter').addEventListener('change', filterSentiments);
    document.getElementById('positionFilter').addEventListener('change', filterSentiments);
    document.getElementById('resetButton').addEventListener('click', resetFilters);
    document.getElementById('startDate').addEventListener('change', loadSentiments);
    document.getElementById('endDate').addEventListener('change', loadSentiments);
    document.getElementById('pastWeek').addEventListener('click', function () {
        const dates = pastWeek();
        document.getElementById('startDate').value = dates.startDate;
        document.getElementById('endDate').value = dates.endDate;
        loadSentiments()
    });
    document.getElementById('pastMonth').addEventListener('click', function () {
        const dates = pastMonth();
        document.getElementById('startDate').value = dates.startDate;
        document.getElementById('endDate').value = dates.endDate;
        loadSentiments();
    });
    document.getElementById('weekFilter').addEventListener('change', function () {
        let week = document.getElementById('weekFilter').value;
        if (week) {
            const dates = getWeek(week);
            document.getElementById('startDate').value = dates.startDate;
            document.getElementById('endDate').value = dates.endDate;
            loadSentiments();
        }
        else {
            document.getElementById('startDate').value = '';
            document.getElementById('endDate').value = '';
            loadSentiments();
        }
    });
    let sentimentsData = [];

    function loadSentiments() {
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;

        let url = '/get-sentiments';

        if (startDate && endDate) {
            url += `?start_date=${startDate}&end_date=${endDate}`;
        }

        fetch(url, { method: 'GET' })
            .then(response => response.json())
            .then(data => {
                sentimentsData = data;
                displaySentiments(data);
            })
            .catch(error => console.error('Error:', error));
    }

    function displaySentiments(data) {
        const sentimentTable = document.getElementById('sentimentTable').getElementsByTagName('tbody')[0];
        sentimentTable.innerHTML = '';
        let start_date = document.getElementById('startDate').value
        let end_date = document.getElementById('endDate').value
        document.getElementById('endDate').value
        data.forEach(player => {
            const avg_sentiment = parseFloat(player.sentiment);
            const row = sentimentTable.insertRow();
            row.innerHTML = `
            <td>${player.name}</td>
            <td>${player.position}</td>
            <td>${player.team}</td>
            <td>${avg_sentiment.toFixed(2)}</td>
            <td>${player.num_quotes > 0 ? `${player.num_quotes} <a href="/?player=${encodeURIComponent(player.name)}&start-date=${start_date}&end-date=${end_date}"">(View Quotes)</a>` : player.num_quotes}</td>
            <td>${player.num_reports > 0 ? `${player.num_reports} <a href="/view-reports?player=${encodeURIComponent(player.name)}&start-date=${start_date}&end-date=${end_date}">(View Reports)</a>` : player.num_reports}</td>
        `;
        });
    }


    function filterSentiments() {
        const searchInputValue = document.getElementById('searchInput').value.toLowerCase();
        const teamFilterValue = document.getElementById('teamFilter').value;
        const positionFilterValue = document.getElementById('positionFilter').value;

        const filteredData = sentimentsData.filter(player => {
            return (
                player.name.toLowerCase().includes(searchInputValue) &&
                (teamFilterValue === '' || player.team === teamFilterValue) &&
                (positionFilterValue === '' || player.position === positionFilterValue)
            );
        });
        displaySentiments(filteredData);
    }

    function resetFilters() {
        document.getElementById('searchInput').value = '';
        document.getElementById('teamFilter').value = '';
        document.getElementById('positionFilter').value = '';
        document.getElementById('startDate').value = '';
        document.getElementById('endDate').value = '';
        loadSentiments();
    }

    document.querySelectorAll('#sentimentTable th').forEach(header => {
        header.addEventListener('click', function() {
            const column = header.getAttribute('data-column');
            const order = header.getAttribute('data-order');

            sentimentsData.sort((a, b) => {
                if (order === 'desc') {
                    return a[column] < b[column] ? 1 : -1;
                } else {
                    return a[column] > b[column] ? 1 : -1;
                }
            });

            // Toggle the sorting order for the next click
            header.setAttribute('data-order', order === 'desc' ? 'asc' : 'desc');

            filterSentiments()
        });
    });

});

