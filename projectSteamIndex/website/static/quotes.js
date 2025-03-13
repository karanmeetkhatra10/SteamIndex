function generate_transcript() {
    fetch('/generate-transcript', {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                document.getElementById('result2').innerText = data.message;
            } else if (data.error) {
                document.getElementById('result2').innerText = 'Error: ' + data.error;
            }
        })
        .catch(error => console.error('Error:', error));
}

let allQuotes = [];
let quotesToShow = 1000; // keep increasing if needed

function load_all_quotes() {
    document.getElementById('loadingSpinner').style.display = 'block';
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    let url = '/quotes';
    if (startDate && endDate){
        url += `?start_date=${startDate}&end_date=${endDate}`;
    }
    fetch(url, {
        method: 'GET'
    })
        .then(response => response.json())
        .then(data => {
            if (Array.isArray(data)) {
                allQuotes = data;
                applyFilters();
                document.getElementById('loadingSpinner').style.display = 'none';
            } else if (data.error) {
                document.getElementById('quotes').innerText = 'Error: ' + data.error;
                document.getElementById('loadingSpinner').style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('loadingSpinner').style.display = 'none';
        });
}


function displayQuotes(quotes) {
    const quotesDiv = document.getElementById('quotes');
    quotesDiv.innerHTML = '';

    const quotesToDisplay = quotes.slice(0, quotesToShow);

    quotesToDisplay.forEach(quote => {
        const quoteElement = document.createElement('div');
        quoteElement.className = 'card';
        quoteElement.setAttribute('data-quote-id', quote.id); // Set data-quote-id attribute
        let dateString = quote.date;
        let date = new Date(dateString);
        let year = date.getUTCFullYear();
        let month = ('0' + (date.getUTCMonth() + 1)).slice(-2);  // Months are zero based
        let day = ('0' + date.getUTCDate()).slice(-2);
        let formattedDate = `${year}-${month}-${day}`;
        quoteElement.innerHTML = `
            <div class="card-body">
<!--                <input type="checkbox" class="quote-checkbox">-->
                <div class="quote-header">
                    <img src="static/nfl.png" alt="${quote.name}" width="50" height="50">
                    <div class="quote-details">
                        <h5 class="card-title quote-title">${quote.name}</h5>
                        <h6 class="card-subtitle quote-subtitle">${quote.team} - ${quote.position}</h6>
                    </div>
                    <input name="checkbox" type="checkbox" class="quote-checkbox">

                </div>
                <div class="quote-summary" onclick="toggleQuote(this)">
                    <div class="quote-text"><h5>${quote.title}</h5></div>
                    <div class="quote-footer">
                        <span>${formattedDate} &bull; ${quote.source}</span>
                        <span class="expand-button"><i class="fas fa-chevron-down"></i></span>
                    </div>
                </div>
                <div class="quote-body" style="display: none;">
                    <p class="card-text"><strong>${quote.question}</strong></p>
                    <p class="card-text">${quote.quote}</p>
                </div>
            </div>
        `;
        quotesDiv.appendChild(quoteElement);
    });
}

function selectAllQuotes() {
    const checkboxes = document.querySelectorAll('.quote-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = true;
    });
}

function deselectAllQuotes() {
    const checkboxes = document.querySelectorAll('.quote-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });
}

document.addEventListener('change', () => {
    const checkboxes = document.querySelectorAll('.quote-checkbox');
    const deleteButton = document.getElementById('deleteSelected');
    let anyChecked = false;

    checkboxes.forEach(checkbox => {
        if (checkbox.checked) {
            anyChecked = true;
        }
    });

    deleteButton.disabled = !anyChecked;
});

function deleteSelectedQuotes() {
    const checkboxes = document.querySelectorAll('.quote-checkbox:checked');
    const quoteIds = Array.from(checkboxes).map(checkbox => {
        return parseInt(checkbox.closest('.card').getAttribute('data-quote-id'), 10);
    });

    // Send request to delete quotes via fetch
    fetch('/delete-quotes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ quoteIds }),
    })
        .then(response => response.json())
        .then(data => {
            // Handle success or error response
            if (data.success) {
                // Handle success message
                console.log('Quotes deleted successfully');
                // Optionally, reload quotes or update UI
            } else {
                // Handle error message
                console.error('Error:', data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function toggleQuote(element) {
    const quoteBody = element.nextElementSibling;
    const expandButton = element.querySelector('.expand-button');

    if (quoteBody.style.display === 'none' || !quoteBody.style.display) {
        quoteBody.style.display = 'block';
        expandButton.querySelector('i').classList.remove('fa-chevron-down');
        expandButton.querySelector('i').classList.add('fa-chevron-up');
    } else {
        quoteBody.style.display = 'none';
        expandButton.querySelector('i').classList.remove('fa-chevron-up');
        expandButton.querySelector('i').classList.add('fa-chevron-down');
    }
}

function applyFilters() {
    const searchInput = document.getElementById('searchInput').value.toLowerCase();
    const teamFilter = document.getElementById('teamFilter').value.toLowerCase();
    const positionFilter = document.getElementById('positionFilter').value.toLowerCase();
    const sourceFilter = document.getElementById('sourceFilter').value.toLowerCase();

    const filteredQuotes = allQuotes.filter(quote => {
        return (
            (quote.name.toLowerCase().includes(searchInput)) &&
            (teamFilter === '' || quote.team.toLowerCase().includes(teamFilter)) &&
            (positionFilter === '' || quote.position.toLowerCase().includes(positionFilter)) &&
            (sourceFilter === '' || quote.source.toLowerCase().includes(sourceFilter))
        );
    });

    displayQuotes(filteredQuotes);
}

function resetFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('teamFilter').value = '';
    document.getElementById('positionFilter').value = '';
    document.getElementById('sourceFilter').value = '';
    document.getElementById('startDate').value = '';
    document.getElementById('endDate').value = '';
    load_all_quotes();
}

document.getElementById('searchInput').addEventListener('input', applyFilters);
document.getElementById('teamFilter').addEventListener('change', applyFilters);
document.getElementById('positionFilter').addEventListener('change', applyFilters);
document.getElementById('sourceFilter').addEventListener('change', applyFilters);
document.getElementById('resetButton').addEventListener('click', resetFilters);
document.getElementById('startDate').addEventListener('change', load_all_quotes);
document.getElementById('endDate').addEventListener('change', load_all_quotes);
document.getElementById('pastWeek').addEventListener('click', function () {
    const dates = pastWeek();
    document.getElementById('startDate').value = dates.startDate;
    document.getElementById('endDate').value = dates.endDate;
    load_all_quotes();
});
document.getElementById('pastMonth').addEventListener('click', function () {
    const dates = pastMonth();
    document.getElementById('startDate').value = dates.startDate;
    document.getElementById('endDate').value = dates.endDate;
    load_all_quotes();
});
document.getElementById('weekFilter').addEventListener('change', function () {
    let week = document.getElementById('weekFilter').value;
    if (week) {
        const dates = getWeek(week);
        document.getElementById('startDate').value = dates.startDate;
        document.getElementById('endDate').value = dates.endDate;
        load_all_quotes();
    }
    else {
        document.getElementById('startDate').value = '';
        document.getElementById('endDate').value = '';
        load_all_quotes();
    }
});

// window.addEventListener('scroll', () => {
//     if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 10) {
//         quotesToShow += 10;
//         // applyFilters();
//     }
// }); fix for error where descriptions close (can try fixing later)

document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const playerName = urlParams.get('player');
    const startDate = urlParams.get('start-date');
    const endDate = urlParams.get('end-date');
    if (playerName) {
        setSearchInputValue(playerName, startDate, endDate)
        load_all_quotes()
        removeQueryParameters();
    } else {
        load_all_quotes();
    }
});

function removeQueryParameters() {
    const url = window.location.href;
    const urlWithoutParams = url.split('?')[0];
    window.history.replaceState({}, document.title, urlWithoutParams);
}

function setSearchInputValue(name, startDate, endDate) {
    document.getElementById('searchInput').value = name;
    document.getElementById('startDate').value = startDate;
    document.getElementById('endDate').value = endDate;

}
