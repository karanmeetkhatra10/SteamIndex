const name_mapping = {
    "49ers": "San Francisco 49ers", "AtlantaFalcons": "Atlanta Falcons", "azcardinals": "Arizona Cardinals",
    "BaltimoreRavens": "Baltimore Ravens", "Bengals": "Cincinnati Bengals", "broncos": "Denver Broncos",
    "browns": "Cleveland Browns", "channel": "Tampa Bay Buccaneers", "buffalobills": "Buffalo Bills",
    "CarolinaPanthers": "Carolina Panthers", "chargers": "Los Angeles Chargers", "ChicagoBears": "Chicago Bears",
    "colts": "Indianapolis Colts", "commandersnfl": "Washington Commanders", "DallasCowboys": "Dallas Cowboys",
    "detroitlionsnfl": "Detroit Lions", "eagles": "Philadelphia Eagles", "HoustonTexans": "Houston Texans",
    "jaguars": "Jacksonville Jaguars", "KansasCityChiefs": "Kansas City Chiefs", "LARams": "Los Angeles Rams",
    "MiamiDolphins": "Miami Dolphins", "NewOrleansSaints": "New Orleans Saints", "NewYorkGiants": "NY Giants",
    "nyjets": "NY Jets", "packers": "Green Bay Packers", "raiders": "Las Vegas Raiders",
    "Seahawks": "Seattle Seahawks", "steelers": "Pittsburgh Steelers", "patriots": "New England Patriots",
    "Titans": "Tennessee Titans", "vikings": "Minnesota Vikings"
};

function getNewName(oldName) {
    return name_mapping[oldName] || oldName; // If no mapping found, use the old name
}

document.addEventListener('DOMContentLoaded', function() {
    load_videos();
    populateTeamFilter();

    document.getElementById('teamFilter').addEventListener('change', load_videos);
    document.getElementById('deleteSelected').addEventListener('click', deleteSelectedVideos);

    function populateTeamFilter() {
        const teamFilter = document.getElementById('teamFilter');
        Object.values(name_mapping).forEach(team => {
            const option = document.createElement('option');
            option.value = team;
            option.textContent = team;
            teamFilter.appendChild(option);
        });
    }

    function escapeJSString(str) {
        return str.replace(/'/g, "\\'").replace(/"/g, '&quot;');
    }

    function load_videos() {
        fetch('/list-videos', {
            method: 'GET'
        })
            .then(response => response.json())
            .then(data => {
                const teamFilterValue = document.getElementById('teamFilter').value;
                const filteredData = teamFilterValue === 'all' ? data : data.filter(video => getNewName(video.team) === teamFilterValue);

                const videosTable = document.getElementById('videosTable').getElementsByTagName('tbody')[0];
                videosTable.innerHTML = ''; // Clear the table body
                filteredData.forEach(video => {
                    const escapedPath = encodeURIComponent(video.path);
                    const date = video.title.substring(0, 8);
                    const formattedDate = `${date.substring(0, 4)}-${date.substring(4, 6)}-${date.substring(6, 8)}`;

                    const duration = video.title.substring(11, 17);
                    const hours = duration.substring(0, 2);
                    const minutes = duration.substring(2, 4);
                    const seconds = duration.substring(4, 6);
                    const formattedDuration = `${hours}:${minutes}:${seconds}`;
                    const row = videosTable.insertRow();
                    row.innerHTML = `
                    <td><input name="checkbox" type="checkbox" class="video-checkbox" data-path="${escapedPath}"></td>
                    <td>${video.title.substring(20, video.title.length - 4)}</td>
                    <td>${getNewName(video.team)}</td>
                    <td>${formattedDate}</td>
                    <td>${formattedDuration}</td>
                    <td class="action-buttons">
                        <button class="btn btn-primary" onclick="watchVideo('${escapedPath.replace(/'/g, "\\'").replace(/"/g, '&quot;')}')">Watch</button>
                    </td>
                `;
                });
                updateDeleteButtonState();
                addCheckboxEventListeners();
            })
            .catch(error => console.error('Error:', error));
    }

    function updateDeleteButtonState() {
        const checkboxes = document.querySelectorAll('.video-checkbox');
        const deleteButton = document.getElementById('deleteSelected');
        deleteButton.disabled = !Array.from(checkboxes).some(checkbox => checkbox.checked);
    }

    function addCheckboxEventListeners() {
        const checkboxes = document.querySelectorAll('.video-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', updateDeleteButtonState);
        });
    }

    window.watchVideo = function(path) {
        window.location.href = `/videos/${path}`;
    };

    function deleteSelectedVideos() {
        const selectedPaths = Array.from(document.querySelectorAll('.video-checkbox:checked'))
            .map(checkbox => checkbox.dataset.path);

        // console.log('Selected paths for deletion:', selectedPaths);  // Log paths being sent to the server

        if (selectedPaths.length > 0 && confirm('Are you sure you want to delete the selected videos?')) {
            fetch('/delete-video', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ paths: selectedPaths })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        alert(data.message);
                        load_videos(); // Reload the videos list
                    } else if (data.error) {
                        alert('Error: ' + data.error);
                    }
                })
                .catch(error => console.error('Error:', error));
        }
    }
});





function download_yt() {
    fetch('/download-yt', {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                document.getElementById('result').innerText = data.message;
            } else if (data.error) {
                document.getElementById('result').innerText = 'Error: ' + data.error;
            }
        })
        .catch(error => console.error('Error:', error));
}