# anything not related to authentication that the user can go to is stored in this file
from flask import Blueprint, render_template, jsonify, request
import website.transcriptGenerator as transcriptGenerator
import website.showQuotes as showQuotes
from website.DatabaseConnector import DatabaseConnector
views = Blueprint('views', __name__)


@views.route('/')  # define a route or view in this case the home page
def home():
    return render_template("home.html")


@views.route('/generate-transcript', methods=['POST'])
def generate_transcript():
    try:
        transcriptGenerator.main()
        return jsonify({"message": "Script executed successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@views.route('/quotes', methods=['GET'])
def show_quotes():
    try:
        player_name = request.args.get('player', None)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        all_quotes = showQuotes.get_quotes(player_name, start_date, end_date)
        return jsonify(all_quotes), 200  # Return the list of quotes directly
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to delete quotes
@views.route('/delete-quotes', methods=['POST'])
def delete_quotes():
    try:
        quote_ids = request.json.get('quoteIds', [])
        if not quote_ids:
            return jsonify({'error': 'No quotes selected for deletion'}), 400
        # Construct delete query
        delete_query = "DELETE FROM quotes WHERE id IN (%s)" % ','.join(['%s'] * len(quote_ids))
        params = tuple(quote_ids)

        # Execute delete operation
        db = DatabaseConnector()
        db.delete(delete_query, params)
        db.close()

        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

