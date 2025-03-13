async function runOptimizer() {
    const lockedPlayers = [];
    const excludedPlayers = [];

    // Collect locked players
    $('.lock-checkbox:checked').each(function () {
        lockedPlayers.push($(this).data('name'));
    });

    // Collect excluded players
    $('.exclude-checkbox:checked').each(function () {
        excludedPlayers.push($(this).data('name'));
    });

    const numLineups = $('#numLineups').val();
    const enforceStack = $('#stackCheckbox').is(':checked'); // Get stack state

    // Send data to server
    fetch('/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            locked_players: lockedPlayers,
            excluded_players: excludedPlayers,
            num_lineups: numLineups,
            stack: enforceStack
        }),
    })
        .then((response) => response.json())
        .then((data) => {
            const lineups = data.lineups || [];
            const playerCounts = data.player_counts || [];
            const lineupContainer = $('#optimalLineups');
            const playerSidebar = $('#playerSidebar');
            lineupContainer.empty();
            playerSidebar.empty();

            const rowDiv = $('<div class="row"></div>');

            lineups.forEach((lineup, index) => {
                // Group players by position
                const grouped = {
                    QB: [],
                    RB: [],
                    WR: [],
                    TE: [],
                    DST: [],
                    FLEX: [],
                };

                lineup.forEach((player) => {
                    if (grouped[player.position]) {
                        grouped[player.position].push(player);
                    }
                });

                // Add FLEX player dynamically (any RB, WR, or TE not already used)
                const flexPool = [
                    ...grouped.RB.slice(2), // Exclude first 2 RBs (already used)
                    ...grouped.WR.slice(3), // Exclude first 3 WRs
                    ...grouped.TE.slice(1), // Exclude first TE
                ];
                const flexPlayer = flexPool[0] || null; // Pick the first available FLEX player

                // Arrange players into ordered lineup
                const orderedLineup = [
                    ...grouped.QB.slice(0, 1),
                    ...grouped.RB.slice(0, 2),
                    ...grouped.WR.slice(0, 3),
                    ...grouped.TE.slice(0, 1),
                    ...grouped.DST.slice(0, 1),
                ];
                if (flexPlayer) orderedLineup.push(flexPlayer);

                // Calculate totals
                const totalSalary = orderedLineup.reduce((sum, player) => sum + player.salary, 0);
                const totalPoints = orderedLineup.reduce((sum, player) => sum + player.points, 0);
                const totalOwnership = orderedLineup.reduce((sum, player) => sum + player.ownership, 0);

                // Generate lineup HTML
                const lineupHtml = `
                    <div class="col-md-4">
                        <div class="card mb-3">
                            <div class="card-body">
                                <h5 class="card-title">Lineup ${index + 1}</h5>
                                <p><strong>Salary:</strong> $${totalSalary}</p>
                                <p><strong>Points:</strong> ${totalPoints.toFixed(2)}</p>
                                <p><strong>Ownership:</strong> ${totalOwnership.toFixed(2)}%</p>
                                <table class="table table-sm">
                                    <thead>
                                        <tr>
                                            <th>Name</th>
                                            <th>Pos</th>
                                            <th>Sal</th>
                                            <th>Pts</th>
                                            <th>%</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${orderedLineup
                    .map(
                        (player) => `
                                            <tr>
                                                <td>${player.name}</td>
                                                <td>${player.position}</td>
                                                <td>${player.salary}</td>
                                                <td>${player.points.toFixed(1)}</td>
                                                <td>${player.ownership.toFixed(1)}</td>
                                            </tr>
                                        `
                    )
                    .join('')}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                `;

                rowDiv.append(lineupHtml);

                // Start a new row after every third lineup
                if ((index + 1) % 3 === 0) {
                    lineupContainer.append(rowDiv.clone());
                    rowDiv.empty();
                }
            });

            // Append remaining lineups if any
            if (rowDiv.children().length > 0) {
                lineupContainer.append(rowDiv);
            }
            const playerList = playerCounts
                .map(([name, count]) => `<li>${name}: ${count}/${numLineups}</li>`)
                .join('');
            playerSidebar.html(`<ul>${playerList}</ul>`);

        })
        .catch((error) => {
            console.error('Error:', error);
        });
}
