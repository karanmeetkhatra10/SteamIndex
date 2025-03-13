from website.DatabaseConnector import DatabaseConnector

def get_reports(player_name=None, start_date=None, end_date=None):
    db = DatabaseConnector()
    print("Here");
    if player_name:
        query = """
            SELECT 
                r.id, p.name AS player_name, p.team, p.position, r.report_date, r.source, r.report_text, r.question 
            FROM 
                reports r
            JOIN 
                allPlayers p ON r.player_name = p.name 
            WHERE r.player_name = %s
        """
        if start_date and end_date:
            query += '''
            WHERE report_date >= '{}' AND report_date <= '{}'
        '''.format(start_date, end_date)
        query += "ORDER BY r.report_date DESC"
        results_df = db.query_dataframe(query, (player_name,))
    else:
        query = """
            SELECT 
                r.id, p.name AS player_name, p.team, p.position, r.report_date, r.source, r.report_text, r.question 
            FROM 
                reports r
            JOIN 
                allPlayers p ON r.player_name = p.name 
        """
        if start_date and end_date:
            query += '''
            WHERE report_date >= '{}' AND report_date <= '{}'
        '''.format(start_date, end_date)
        query += "ORDER BY r.report_date DESC"
        results_df = db.query_dataframe(query)
    db.close()
    return results_df.to_dict(orient='records')

