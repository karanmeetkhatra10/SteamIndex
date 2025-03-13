from website.DatabaseConnector import DatabaseConnector

def get_quotes(player_name=None, start_date=None, end_date=None):
    db = DatabaseConnector()
    if player_name:
        query = "SELECT * FROM quotes WHERE name = %s "
        if start_date and end_date:
            query += '''
            WHERE date >= '{}' AND date <= '{}'
        '''.format(start_date, end_date)
        query += "ORDER BY id desc"
        results_df = db.query_dataframe(query, (player_name,))
    else:
        query = "SELECT * FROM quotes "
        if start_date and end_date:
            query += '''
            WHERE date >= '{}' AND date <= '{}'
        '''.format(start_date, end_date)
        query += "ORDER BY id desc"
        results_df = db.query_dataframe(query)
    db.close()
    return results_df.to_dict(orient='records')


