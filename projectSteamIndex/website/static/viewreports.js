
let allReports = [];

function load_all_reports() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    let url = '/all-reports';
    if (startDate && endDate){
        url += `?start_date=${startDate}&end_date=${endDate}`;
    }
    fetch(url, {
        method: 'GET'
    })
        .then(response => response.json())
        .then(data => {
            if (Array.isArray(data)) {
                allReports = data;
                applyFilters()
                document.getElementById('loadingSpinner').style.display = 'none';
            } else if (data.error) {
                document.getElementById('reportsTable').innerText = 'Error: ' + data.error;
                document.getElementById('loadingSpinner').style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('loadingSpinner').style.display = 'none';
        });
}

function displayReports(reports) {
    const reportsTableBody = document.querySelector('#reportsTable tbody');
    reportsTableBody.innerHTML = '';
    reports.forEach(report => {
        const row = document.createElement('tr');
        row.dataset.reportId = report.id;
        let dateString = report.report_date;
        let date = new Date(dateString);
        let year = date.getUTCFullYear();
        let month = ('0' + (date.getUTCMonth() + 1)).slice(-2);  // Months are zero based
        let day = ('0' + date.getUTCDate()).slice(-2);
        let formattedDate = `${year}-${month}-${day}`;
        row.innerHTML = `
            <td><input name = "selectOne" type="checkbox" class="reportCheckbox" data-report-id="${report.id}"></td>
            <td>${report.player_name}</td>
            <td>${report.team}</td>
            <td>${report.position}</td>
            <td>${formattedDate}</td>
            <td>${report.source}</td>
            <td>${report.question ? `<b>${report.question}</b><br><br>` : ''}${report.report_text}</td>
        `;
        reportsTableBody.appendChild(row);
    });
}

function applyFilters() {
    const teamFilter = document.getElementById('teamFilter').value.toLowerCase();
    const positionFilter = document.getElementById('positionFilter').value.toLowerCase();
    const searchInput = document.getElementById('searchInput').value.toLowerCase();
    const filteredReports = allReports.filter(report => {
        return (
            (report.player_name.toLowerCase().includes(searchInput)) &&
            (teamFilter === '' || report.team.toLowerCase().includes(teamFilter)) &&
            (positionFilter === '' || report.position.toLowerCase().includes(positionFilter))
        );
    });

    displayReports(filteredReports);
}

function resetFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('teamFilter').value = '';
    document.getElementById('positionFilter').value = '';
    document.getElementById('startDate').value = '';
    document.getElementById('endDate').value = '';
    load_all_reports();
}

function deleteSelectedReports() {
    const selectedCheckboxes = document.querySelectorAll('.reportCheckbox:checked');
    const reportIdsToDelete = Array.from(selectedCheckboxes).map(cb => cb.getAttribute('data-report-id'));

    fetch(`/delete-reports`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ reportIds: reportIdsToDelete })
    })
        .then(response => {
            if (response.ok) {
                selectedCheckboxes.forEach(checkbox => {
                    const row = checkbox.closest('tr');
                    row.remove();
                });
            } else {
                console.error('Error deleting reports:', response.statusText);
            }
        })
        .catch(error => console.error('Error:', error));
}

document.getElementById('teamFilter').addEventListener('change', applyFilters);
document.getElementById('positionFilter').addEventListener('change', applyFilters);
document.getElementById('searchInput').addEventListener('input', applyFilters);
document.getElementById('resetButton').addEventListener('click', resetFilters);
document.getElementById('deleteButton').addEventListener('click', deleteSelectedReports);
document.getElementById('startDate').addEventListener('change', load_all_reports);
document.getElementById('endDate').addEventListener('change', load_all_reports);
document.getElementById('pastWeek').addEventListener('click', function () {
    const dates = pastWeek();
    document.getElementById('startDate').value = dates.startDate;
    document.getElementById('endDate').value = dates.endDate;
    load_all_reports()
});
document.getElementById('pastMonth').addEventListener('click', function () {
    const dates = pastMonth();
    document.getElementById('startDate').value = dates.startDate;
    document.getElementById('endDate').value = dates.endDate;
    load_all_reports();
});
document.getElementById('weekFilter').addEventListener('change', function () {
    let week = document.getElementById('weekFilter').value;
    if (week) {
        const dates = getWeek(week);
        document.getElementById('startDate').value = dates.startDate;
        document.getElementById('endDate').value = dates.endDate;
        load_all_reports();
    }
    else {
        document.getElementById('startDate').value = '';
        document.getElementById('endDate').value = '';
        load_all_reports();
    }
});

document.getElementById('selectAll').addEventListener('change', function() {
    const checkboxes = document.querySelectorAll('.reportCheckbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = this.checked;
    });
});

document.addEventListener('DOMContentLoaded', function (){
    const urlParams = new URLSearchParams(window.location.search);
    const playerName = urlParams.get('player');
    const startDate = urlParams.get('start-date');
    const endDate = urlParams.get('end-date');
    if (playerName) {
        setSearchInputValue(playerName, startDate, endDate)
        load_all_reports()
        removeQueryParameters();
    } else {
        load_all_reports();
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

