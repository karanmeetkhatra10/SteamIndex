from datetime import datetime

import pandas as pd
from flask import Blueprint, render_template, jsonify, send_from_directory, request, url_for, redirect
import os
import website.downloadYT as downloadYT
import website.sentimentScore as sentimentScore
import website.showReports as showReports
from website.DatabaseConnector import DatabaseConnector
from urllib.parse import unquote
from datetime import datetime, timedelta


auth = Blueprint('auth', __name__)


@auth.route('/videos', methods=['GET','POST'])
def videos():
    return render_template("videos.html")


@auth.route('/sentiment', methods=['GET','POST'])
def sentiment():
    return render_template("sentiment.html")


@auth.route('/reports', methods=['GET','POST'])
def reports():
    return render_template('reports.html')


@auth.route('/view-reports', methods=['GET','POST'])
def view_reports():
    return render_template('viewreports.html')


@auth.route('/projections')
def projections():
    return render_template('projections.html')


@auth.route('/admin-projections', methods=['GET', 'POST'])
def admin_projections():
    return render_template('admin_projections.html')


@auth.route('/download-yt', methods=['POST'])
def download_yt():
    try:
        downloadYT.main()
        return jsonify({"message": "Script executed successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth.route('/generate-sentiment', methods=['POST'])
def generate_sentiment():
    try:
        sentimentScore.main()
        return jsonify({"message": "Script executed successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth.route('/get-sentiments', methods=['GET'])
def get_sentiments():
    db = DatabaseConnector()

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Construct the base SQL query
    # sentiment_query = '''
    #     SELECT name, position, team, sentiment, COUNT(name) as num_quotes
    #     FROM quotes
    # '''
    sentiment_quotes_query = '''
        SELECT name, position, team, sentiment
        FROM quotes
    '''
    # Initialize an empty list to hold the WHERE clauses
    where_clauses = ['sentiment IS NOT NULL']

    # Add the date range conditions if start_date and end_date are provided
    if start_date and end_date:
        where_clauses.append("date >= '{}' AND date <= '{}'".format(start_date, end_date))

    # If there are any WHERE clauses, add them to the query
    if where_clauses:
        sentiment_quotes_query += ' WHERE ' + ' AND '.join(where_clauses)
    sentiments_quotes_df = db.query_dataframe(sentiment_quotes_query)


    allPlayers_query = "SELECT name, position, team FROM allPlayers"
    allPlayers_df = db.query_dataframe(allPlayers_query)

    sentiment_reports_query = '''
        SELECT player_name as name, sentiment
        FROM reports
    '''
    # Initialize an empty list to hold the WHERE clauses
    where_clauses_reports = ['sentiment IS NOT NULL']

    # Add the date range conditions if start_date and end_date are provided
    if start_date and end_date:
        where_clauses_reports.append("report_date >= '{}' AND report_date <= '{}'".format(start_date, end_date))

    # If there are any WHERE clauses, add them to the query
    if where_clauses_reports:
        sentiment_reports_query += ' WHERE ' + ' AND '.join(where_clauses_reports)
    sentiments_reports_df = db.query_dataframe(sentiment_reports_query)

    df_combined_reports_players = pd.merge(sentiments_reports_df, allPlayers_df, on='name', how='left')

    df_combined_reports_quotes = pd.concat([df_combined_reports_players, sentiments_quotes_df], ignore_index=True)

    avg_sentiments = df_combined_reports_quotes.groupby(['name', 'position', 'team'])['sentiment'].mean().reset_index()

    # Query to fetch total number of quotes per player
    query_quotes = '''
    SELECT name, COUNT(name) as num_quotes
    FROM quotes
    '''
    if start_date and end_date:
        query_quotes += '''
            WHERE date >= '{}' AND date <= '{}'
        '''.format(start_date, end_date)
    query_quotes += '''
        GROUP BY name
    '''
    df_num_quotes = db.query_dataframe(query_quotes)

    # Query to fetch total number of reports per player
    query_reports = '''
    SELECT player_name as name, COUNT(player_name) as num_reports
    FROM reports
    '''
    if start_date and end_date:
        query_reports += '''
            WHERE report_date >= '{}' AND report_date <= '{}'
        '''.format(start_date, end_date)
    query_reports += '''
        GROUP BY name
    '''
    df_num_reports = db.query_dataframe(query_reports)

    df_merged = pd.merge(avg_sentiments, df_num_quotes, on='name', how='left')
    df_merged = pd.merge(df_merged, df_num_reports, on='name', how='left')
    df_merged['num_quotes'] = df_merged['num_quotes'].fillna(0).astype(int)
    df_merged['num_reports'] = df_merged['num_reports'].fillna(0).astype(int)
    df_sorted = df_merged.sort_values(by='sentiment', ascending=False)
    db.close()
    result = df_sorted.to_dict(orient='records')
    return jsonify(result)



BASE_VIDEO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'videos'))


@auth.route('/list-videos', methods=['GET'])
def list_videos():
    videos_all = []
    for root, dirs, files in os.walk(BASE_VIDEO_PATH):
        for video_file in files:
            video_path = os.path.join(root, video_file)
            team_dir = os.path.relpath(root, BASE_VIDEO_PATH).split(os.sep)[0]  # Get the team directory name
            if os.path.isfile(video_path) and video_file != 'downloaded_videos.json':
                videos_all.append({
                    'team': team_dir,
                    'title': video_file,
                    'path': os.path.relpath(video_path, BASE_VIDEO_PATH).replace(os.sep, '/'),
                    'date': datetime.fromtimestamp(os.path.getmtime(video_path)).strftime('%Y-%m-%d %H:%M:%S')
                })
    return jsonify(videos_all)


@auth.route('/delete-video', methods=['POST'])
def delete_video():
    data = request.json
    not_found_videos = []

    for video_path in data['paths']:
        decoded_path = unquote(video_path)
        full_video_path = os.path.join(BASE_VIDEO_PATH, os.path.normpath(decoded_path))
        # print(f"Received path for deletion: {full_video_path}")  # Log the received path
        if os.path.exists(full_video_path):
            os.remove(full_video_path)
            print(f"Deleted: {full_video_path}")  # Log successful deletion
        else:
            print(f"File not found: {full_video_path}")  # Log file not found
            not_found_videos.append(video_path)

    if not_found_videos:
        return jsonify({'error': f'These videos were not found: {", ".join(not_found_videos)}'}), 404
    return jsonify({'message': 'Videos deleted successfully'}), 200


@auth.route('/videos/<path:filename>')
def get_video(filename):
    decoded_path = unquote(filename)
    full_path = os.path.join(BASE_VIDEO_PATH, os.path.normpath(decoded_path))
    if os.path.exists(full_path):
        return send_from_directory(BASE_VIDEO_PATH, decoded_path)
    else:
        return "Not Found", 404


@auth.route('/submit', methods=['POST'])
def submit_reports():
    if request.method == 'POST':
        player_names = request.form.getlist('playerName[]')
        report_dates = request.form.getlist('reportDate[]')
        sources = request.form.getlist('source[]')
        report_texts = request.form.getlist('reportText[]')
        questions = request.form.getlist('question[]')

        # Validate form data (example: check if fields are not empty)
        db = DatabaseConnector()
        add_report = ("INSERT INTO reports"
                      "(player_name, report_date, source, report_text, question)"
                      "VALUES (%s, %s, %s, %s, %s)")
        # Validate and insert each report
        for i in range(len(player_names)):
            player_name = player_names[i]
            report_date = report_dates[i]
            source = sources[i]
            report_text = report_texts[i]
            question = questions[i] if i < len(questions) else None  # Optional question

            if player_name and report_date and source and report_text:
                reports_data = (player_name, report_date, source, report_text, question)
                db.insert(add_report, reports_data)
            else:
                return f"Error: Report {i+1} has missing fields."
        db.close()
        return redirect(url_for('auth.reports'))  # Redirect to index after all reports are inserted

    return "Error: Invalid request method."


@auth.route('/get_all_players')
def get_all_players():
    try:
        db = DatabaseConnector()
        query = "SELECT name FROM allPlayers ORDER BY name ASC"
        results = db.query(query)

        # Extract player names from the query results
        player_names = [row[0] for row in results]
        db.close()
        return jsonify(player_names)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth.route('/all-reports', methods=['GET'])
def all_reports():
    try:
        player_name = request.args.get('player', None)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        all_reports_df = showReports.get_reports(player_name, start_date, end_date)
        return jsonify(all_reports_df)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth.route('/delete-reports', methods=['POST'])
def delete_reports():
    try:
        data = request.json
        print(data)
        report_ids = data.get('reportIds', [])

        if not report_ids:
            return jsonify({'error': 'No report IDs provided'}), 400

        db = DatabaseConnector()
        delete_query = "DELETE FROM reports WHERE id IN ({})".format(','.join(['%s'] * len(report_ids)))
        db.delete(delete_query, report_ids)
        db.close()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth.route('/get-trending-players', methods=['GET'])
def get_trending_players():
    db = DatabaseConnector()

    # Calculate the date one week ago from today
    one_week_ago = datetime.now() - timedelta(days=7)
    one_week_ago_str = one_week_ago.strftime('%Y-%m-%d')

    trending_query = f'''
        SELECT p.name, p.position, p.team, AVG(s.sentiment) as sentiment, COUNT(CASE WHEN s.source = 'quote' THEN 1 END) as quote_count, COUNT(CASE WHEN s.source = 'report' THEN 1 END) as report_count,(COUNT(CASE WHEN s.source = 'quote' THEN 1 END) + COUNT(CASE WHEN s.source = 'report' THEN 1 END)) as total_count
        FROM (
            SELECT name, sentiment, date, 'quote' as source FROM quotes
            WHERE date >= '{one_week_ago_str}'
            UNION ALL
            SELECT player_name as name, sentiment, report_date as date, 'report' as source FROM reports
            WHERE report_date >= '{one_week_ago_str}'
        ) s
        INNER JOIN allPlayers p ON s.name = p.name
        WHERE sentiment IS NOT NULL
        GROUP BY p.name, p.position, p.team
        HAVING total_count >= 2
        ORDER BY sentiment DESC, total_count DESC
        LIMIT 20
    '''

    trending_df = db.query_dataframe(trending_query)
    db.close()
    result = trending_df.to_dict(orient='records')
    return jsonify(result)


@auth.route('/get-not-trending-players', methods=['GET'])
def get_not_trending_players():
    db = DatabaseConnector()

    # Calculate the date one week ago from today
    one_week_ago = datetime.now() - timedelta(days=7)
    one_week_ago_str = one_week_ago.strftime('%Y-%m-%d')

    not_trending_query = f'''
        SELECT p.name, p.position, p.team, AVG(s.sentiment) as sentiment, COUNT(CASE WHEN s.source = 'quote' THEN 1 END) as quote_count, COUNT(CASE WHEN s.source = 'report' THEN 1 END) as report_count,(COUNT(CASE WHEN s.source = 'quote' THEN 1 END) + COUNT(CASE WHEN s.source = 'report' THEN 1 END)) as total_count
        FROM (
            SELECT name, sentiment, date, 'quote' as source FROM quotes
            WHERE date >= '{one_week_ago_str}'
            UNION ALL
            SELECT player_name as name, sentiment, report_date as date, 'report' as source FROM reports
            WHERE report_date >= '{one_week_ago_str}'
        ) s
        INNER JOIN allPlayers p ON s.name = p.name
        WHERE sentiment IS NOT NULL
        GROUP BY p.name, p.position, p.team
        ORDER BY sentiment ASC, total_count DESC
        LIMIT 20
    '''

    not_trending_df = db.query_dataframe(not_trending_query)
    db.close()
    result = not_trending_df.to_dict(orient='records')
    return jsonify(result)


@auth.route('/get-qb-projections')
def get_qb_projections():
    try:
        db = DatabaseConnector()
        query = "SELECT * FROM qb_data ORDER BY pos DESC"
        results = db.query_dataframe(query)
        db.close()
        results = results.to_dict(orient='records')
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth.route('/get-skill-position-projections')
def get_skill_position_projections():
    try:
        db = DatabaseConnector()
        query = "SELECT * FROM rb_wr_te_data ORDER BY pos DESC"
        results = db.query_dataframe(query)
        db.close()
        results = results.to_dict(orient='records')
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth.route('/save-projections', methods=['POST'])
def save_projections():
    data = request.json
    qb_changes = data.get('qb', [])
    skill_changes = data.get('skill', [])
    db = DatabaseConnector()

    for row in qb_changes:
        query = """
        UPDATE qb_data
        SET number = %s, player = %s, pos = %s, school = %s, orig_team = %s, nfl_exp = %s, gms = %s, att = %s, cmp = %s, pct = %s, yds = %s, ypa = %s, td = %s, td_pct = %s, inter = %s, ypg = %s, sack = %s, ratt = %s, ryds = %s, ravg = %s, rypg = %s, rlg = %s, rtd = %s, notes = %s
        WHERE id = %s
        """
        db.update(query, (*row['data'][1:], row['id']))

    for row in skill_changes:
        query = """
        UPDATE rb_wr_te_data
        SET number = %s, player = %s, pos = %s, school = %s, orig_team = %s, nfl_exp = %s, gms = %s, ratt = %s, ryds = %s, ravg = %s, rypg = %s, rlg = %s, rtd = %s, rec = %s, reyds = %s, reavg = %s, reypg = %s, relg = %s, retd = %s, tar = %s, notes = %s
        WHERE id = %s
        """
        db.update(query, (*row['data'][1:], row['id']))

    db.close()
    return jsonify(success=True)

