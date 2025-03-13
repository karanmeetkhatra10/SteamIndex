document.addEventListener('DOMContentLoaded', function() {
    const teamFilter = document.getElementById('teamFilter');
    const searchInput = document.getElementById('searchInput');
    const positionFilter = document.getElementById('positionFilter');
    const resetButton = document.getElementById('resetButton');
    const saveButton = document.getElementById('saveButton');
    let qbData = [];
    let skillPositionData = [];
    let changedRows = { qb: [], skill: [] };

    loadAdminProjections();

    searchInput.addEventListener('input', filterSentiments);
    teamFilter.addEventListener('change', filterSentiments);
    positionFilter.addEventListener('change', filterSentiments);
    resetButton.addEventListener('click', resetFilters);
    saveButton.addEventListener('click', saveChanges);

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
            row.setAttribute('data-id', player.id);
            row.innerHTML = `
                <td><input name="selectOne" type="checkbox" class="reportCheckbox" data-report-id="${player.id}"></td>
                <td contenteditable="true">${player.number}</td>
                <td contenteditable="true">${player.player}</td>
                <td contenteditable="true">${player.pos}</td>
                <td contenteditable="true">${player.school}</td>
                <td contenteditable="true">${player.orig_team}</td>
                <td contenteditable="true">${player.nfl_exp}</td>
                <td contenteditable="true">${player.gms}</td>
                <td contenteditable="true">${player.att}</td>
                <td contenteditable="true">${player.cmp}</td>
                <td contenteditable="true">${player.pct}</td>
                <td contenteditable="true">${player.yds}</td>
                <td contenteditable="true">${player.ypa}</td>
                <td contenteditable="true">${player.td}</td>
                <td contenteditable="true">${player.td_pct}</td>
                <td contenteditable="true">${player.inter}</td>
                <td contenteditable="true">${player.ypg}</td>
                <td contenteditable="true">${player.sack}</td>
                <td contenteditable="true">${player.ratt}</td>
                <td contenteditable="true">${player.ryds}</td>
                <td contenteditable="true">${player.ravg}</td>
                <td contenteditable="true">${player.rypg}</td>
                <td contenteditable="true">${player.rlg}</td>
                <td contenteditable="true">${player.rtd}</td>
                <td contenteditable="true">${player.notes ? player.notes : ''}</td>
            `;
            row.addEventListener('input', () => rowChanged(row, 'qb'));
        });
    }

    function displaySkillPositionData(data) {
        const skillPositionTable = document.getElementById('skillPositionTable').getElementsByTagName('tbody')[0];
        skillPositionTable.innerHTML = '';
        data.forEach((player, index) => {
            const row = skillPositionTable.insertRow();
            row.setAttribute('data-id', player.id);
            row.innerHTML = `
                <td><input name="selectOne" type="checkbox" class="reportCheckbox" data-report-id="${player.id}"></td>
                <td contenteditable="true">${player.number}</td>
                <td contenteditable="true">${player.player}</td>
                <td contenteditable="true">${player.pos}</td>
                <td contenteditable="true">${player.school}</td>
                <td contenteditable="true">${player.orig_team}</td>
                <td contenteditable="true">${player.nfl_exp}</td>
                <td contenteditable="true">${player.gms}</td>
                <td contenteditable="true">${player.ratt}</td>
                <td contenteditable="true">${player.ryds}</td>
                <td contenteditable="true">${player.ravg}</td>
                <td contenteditable="true">${player.rypg}</td>
                <td contenteditable="true">${player.rlg}</td>
                <td contenteditable="true">${player.rtd}</td>
                <td contenteditable="true">${player.rec}</td>
                <td contenteditable="true">${player.reyds}</td>
                <td contenteditable="true">${player.reavg}</td>
                <td contenteditable="true">${player.reypg}</td>
                <td contenteditable="true">${player.relg}</td>
                <td contenteditable="true">${player.retd}</td>
                <td contenteditable="true">${player.tar}</td>
                <td contenteditable="true">${player.notes ? player.notes : ''}</td>
            `;
            row.addEventListener('input', () => rowChanged(row, 'skill'));
        });
    }

    function rowChanged(row, type) {
        const id = row.getAttribute('data-id');
        const data = Array.from(row.cells).map(cell => cell.innerText.trim());
        if (type === 'qb') {
            const existingIndex = changedRows.qb.findIndex(item => item.id === id);
            if (existingIndex !== -1) {
                changedRows.qb[existingIndex] = { id, data };
            } else {
                changedRows.qb.push({ id, data });
            }
        } else if (type === 'skill') {
            const existingIndex = changedRows.skill.findIndex(item => item.id === id);
            if (existingIndex !== -1) {
                changedRows.skill[existingIndex] = { id, data };
            } else {
                changedRows.skill.push({ id, data });
            }
        }
    }

    function saveChanges() {
        const payload = { qb: changedRows.qb, skill: changedRows.skill };
        fetch('/save-projections', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        })
            .then(response => {
                if (response.ok) {
                    console.log('Changes saved successfully!');
                    changedRows = { qb: [], skill: [] };
                } else {
                    console.log('Failed to save changes.');
                }
            })
            .catch(error => console.error('Error:', error));
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
        console.log("Filtering");
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
