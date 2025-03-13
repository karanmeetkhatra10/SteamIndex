document.addEventListener('DOMContentLoaded', function() {
    const teamFilter = document.getElementById('teamFilter');
    const searchInput = document.getElementById('searchInput');
    const positionFilter = document.getElementById('positionFilter');
    const resetButton = document.getElementById('resetButton');
    let qbData = [];
    let skillPositionData = [];

    loadAdminProjections();

    searchInput.addEventListener('input', filterSentiments);
    teamFilter.addEventListener('change', filterSentiments);
    positionFilter.addEventListener('change', filterSentiments);
    resetButton.addEventListener('click', resetFilters);

    function loadAdminProjections() {
        loadQBData();
        loadSkillPositionData();
    }

    function loadQBData() {
        fetch('/get-qb-projections', { method: 'GET' })
            .then(response => response.json())
            .then(data => {
                qbData = data;
                filterSentiments();  // Apply initial filter for Cardinals
            })
            .catch(error => console.error('Error:', error));
    }

    function loadSkillPositionData() {
        fetch('/get-skill-position-projections', { method: 'GET' })
            .then(response => response.json())
            .then(data => {
                skillPositionData = data;
                filterSentiments();  // Apply initial filter for Cardinals
            })
            .catch(error => console.error('Error:', error));
    }

    function displayQBData(data) {
        const qbTable = document.getElementById('qbTable').getElementsByTagName('tbody')[0];
        qbTable.innerHTML = '';
        data.forEach((player, index) => {
            const row = qbTable.insertRow();
            let totalFPoints = (player.ryds*0.1) + (player.yds*0.04) + (player.td * 4) + (player.rtd * 6) - (player.inter * 1);
            let avgFPoints = totalFPoints/player.gms;
            totalFPoints = isNaN(totalFPoints) ? 0 : totalFPoints.toFixed(2);
            avgFPoints = isNaN(avgFPoints) ? 0 : avgFPoints.toFixed(2);
            row.setAttribute('data-id', player.id);
            row.innerHTML = `
                <td>${player.number}</td>
                <td>${player.player}</td>
                <td>${player.pos}</td>
                <td>${player.nfl_exp}</td>
                <td>${avgFPoints}</td>
                <td>${totalFPoints}</td>
                <td>${player.att}</td>
                <td>${player.ypg}</td>
                <td>${player.ratt}</td>
                <td>${player.rypg}</td>
                <td>${player.notes ? player.notes : ''}</td>
            `;
            row.addEventListener('input', () => rowChanged(row, 'qb'));
        });

    }

    function displaySkillPositionData(data) {
        const skillPositionTable = document.getElementById('skillPositionTable').getElementsByTagName('tbody')[0];
        skillPositionTable.innerHTML = '';
        data.forEach((player, index) => {
            const row = skillPositionTable.insertRow();
            let totalFPoints = (player.ryds*0.1) + (player.reyds*0.1) + (player.rtd * 6) + (player.retd * 6) + (player.rec*1);
            let playerGms = 0;
            if (player.ryds == 0){
                playerGms = Math.round(player.reyds / player.reypg);
            }
            else{
                playerGms = Math.round(player.ryds / player.rypg)
            }
            let avgFPoints = totalFPoints/playerGms;
            totalFPoints = isNaN(totalFPoints) ? 0 : totalFPoints.toFixed(2);
            avgFPoints = isNaN(avgFPoints) ? 0 : avgFPoints.toFixed(2);
            row.setAttribute('data-id', player.id);
            row.innerHTML = `
                <td>${player.number}</td>
                <td>${player.player}</td>
                <td>${player.pos}</td>
                <td>${player.nfl_exp}</td>
                <td>${avgFPoints}</td>
                <td>${totalFPoints}</td>
                <td>${player.ratt}</td>
                <td>${player.rypg}</td>
                <td>${player.tar}</td>
                <td>${player.reypg}</td>
                <td>${player.notes ? player.notes : ''}</td>
            `;
            row.addEventListener('input', () => rowChanged(row, 'skill'));
        });
    }


    function filterSentiments() {
        const searchInputValue = searchInput.value.toLowerCase();
        const teamFilterValue = teamFilter.value || 'Cardinals';
        const positionFilterValue = positionFilter.value;

        let filteredQBData = qbData.filter(player => {
            return (
                player.player.toLowerCase().includes(searchInputValue) &&
                (teamFilterValue === '' || player.team === teamFilterValue) &&
                (positionFilterValue === '' || player.pos === positionFilterValue)
            );
        });

        let filteredSkillPositionData = skillPositionData.filter(player => {
            return (
                player.player.toLowerCase().includes(searchInputValue) &&
                (teamFilterValue === '' || player.team === teamFilterValue) &&
                (positionFilterValue === '' || player.pos === positionFilterValue)
            );
        });
        displayQBData(filteredQBData);
        displaySkillPositionData(filteredSkillPositionData);
        // saveChanges();
    }

    function resetFilters() {
        searchInput.value = '';
        positionFilter.value = '';
        filterSentiments();
    }
});
