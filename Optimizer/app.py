from flask import Flask, render_template, request, jsonify
import csv
import pulp

app = Flask(__name__)

# Read player data from CSV
def load_players_from_csv(filepath):
    players = []
    with open(filepath, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        print(f"Headers: {reader.fieldnames}")
        for row in reader:
            players.append({
                "name": row["Player"],
                "team": row["Team"],
                "opponent": row["Opponent"],
                "position": row["DK Position"],
                "salary": int(row["DK Salary"]),
                "points": float(row["DK Ceiling"]),
                "ownership": float(row["DK Large Ownership"]),
            })
    return players

# Load players once at startup
players = load_players_from_csv("DKProj.csv")


@app.route('/')
def index():
    return render_template('index.html', players=players)


@app.route('/optimize', methods=['POST'])
def optimize():
    locked_players = request.json.get('locked_players', [])
    excluded_players = request.json.get('excluded_players', [])
    num_lineups = int(request.json.get('num_lineups', 1))
    enforce_stack = request.json.get('stack', False)  # Get the stack flag

    available_players = [p for p in players if p['name'] not in excluded_players]
    generated_lineups = []
    player_counts = {}

    for _ in range(num_lineups):
        problem = pulp.LpProblem("DraftKingsNFLLineup", pulp.LpMaximize)
        player_vars = {p['name']: pulp.LpVariable(p['name'], cat='Binary') for p in available_players}

        # Objective: maximize projected points
        problem += pulp.lpSum([p['points'] * player_vars[p['name']] for p in available_players])

        # Constraints (same as before)
        problem += pulp.lpSum([p['salary'] * player_vars[p['name']] for p in available_players]) <= 50000
        for lock in locked_players:
            problem += player_vars[lock] == 1

        problem += pulp.lpSum([player_vars[p['name']] for p in available_players if p['position'] == 'QB']) == 1
        problem += pulp.lpSum([player_vars[p['name']] for p in available_players if p['position'] == 'RB']) >= 2
        problem += pulp.lpSum([player_vars[p['name']] for p in available_players if p['position'] == 'WR']) >= 3
        problem += pulp.lpSum([player_vars[p['name']] for p in available_players if p['position'] == 'TE']) >= 1
        problem += pulp.lpSum([player_vars[p['name']] for p in available_players if p['position'] == 'DST']) == 1
        problem += pulp.lpSum([player_vars[p['name']] for p in available_players]) == 9

        # Stack constraint: QB must have at least one WR or TE from the same team
        if enforce_stack:
            for qb in [p for p in available_players if p['position'] == 'QB']:
                teammates = [
                    p for p in available_players
                    if p['team'] == qb['team'] and p['position'] in ['WR', 'TE']
                ]
                problem += pulp.lpSum([player_vars[teammate['name']] for teammate in teammates]) >= player_vars[qb['name']]

        for lineup in generated_lineups:
            problem += pulp.lpSum([player_vars[player['name']] for player in lineup]) <= 8

        problem.solve()

        if pulp.LpStatus[problem.status] != 'Optimal':
            return jsonify({
                "error": "Optimization problem is infeasible. Check constraints and available players.",
                "status": pulp.LpStatus[problem.status],
            })

        current_lineup = [
            {
                "name": p['name'],
                "position": p['position'],
                "salary": p['salary'],
                "points": p['points'],
                "ownership": p['ownership']
            }
            for p in available_players if player_vars[p['name']].value() == 1
        ]

        generated_lineups.append(current_lineup)

        # Track player appearances
        for player in current_lineup:
            if player['name'] in player_counts:
                player_counts[player['name']] += 1
            else:
                player_counts[player['name']] = 1

    # Sort players by appearance count
    sorted_player_counts = sorted(player_counts.items(), key=lambda x: x[1], reverse=True)

    return jsonify({"lineups": generated_lineups, "player_counts": sorted_player_counts})



if __name__ == '__main__':
    app.run(debug=True)
