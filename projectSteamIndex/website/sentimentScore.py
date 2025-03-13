import pandas as pd
from tqdm.notebook import tqdm  # more useful for jupyter notebook to display a progress bar
from datetime import datetime
from io import StringIO
from openai import OpenAI
from rapidfuzz import fuzz, process
from pydub import AudioSegment
import os
import gc
import time
from website.DatabaseConnector import DatabaseConnector

pd.set_option('display.max_columns', None)  # Show all columns

client = OpenAI(
    api_key="sk-proj-dHtSQFcagTSv5mq1YFdRT3BlbkFJFnRLZYOiwsQeZOKOaLkh",
)
MODEL = "gpt-4o"

# Mapping the channel_names to the actual team name to use when filtering out players
channel_names = ["49ers", "AtlantaFalcons", "azcardinals", "BaltimoreRavens", "Bengals",
                 "broncos", "browns", "channel/UC0Wwu7r1ybaaR09ANhudTzA", "buffalobills",
                 "CarolinaPanthers", "chargers", "ChicagoBears", "colts", "commandersnfl",
                 "DallasCowboys", "detroitlionsnfl", "eagles", "HoustonTexans", "jaguars", "KansasCityChiefs",
                 "LARams", "MiamiDolphins", "NewOrleansSaints","NewYorkGiants", "nyjets", "packers",
                 "raiders", "Seahawks", "steelers", "patriots", "Titans", "vikings"]

name_mapping = {"49ers": "San Francisco 49ers", "AtlantaFalcons": "Atlanta Falcons", "azcardinals": "Arizona Cardinals",
                "BaltimoreRavens": "Baltimore Ravens", "Bengals": "Cincinnati Bengals",
                "broncos": "Denver Broncos", "browns": "Cleveland Browns",
                "channel/UC0Wwu7r1ybaaR09ANhudTzA": "Tampa Bay Buccaneers", "buffalobills": "Buffalo Bills",
                "CarolinaPanthers": "Carolina Panthers", "chargers": "Los Angeles Chargers",
                "ChicagoBears": "Chicago Bears", "colts": "Indianapolis Colts",
                "commandersnfl": "Washington Commanders",
                "DallasCowboys": "Dallas Cowboys", "detroitlionsnfl": "Detroit Lions", "eagles": "Philadelphia Eagles",
                "HoustonTexans": "Houston Texans", "jaguars": "Jacksonville Jaguars",
                "KansasCityChiefs": "Kansas City Chiefs",
                "LARams": "Los Angeles Rams", "MiamiDolphins": "Miami Dolphins",
                "NewOrleansSaints": "New Orleans Saints", "NewYorkGiants": "NY Giants", "nyjets": "NY Jets",
                "packers": "Green Bay Packers",
                "raiders": "Las Vegas Raiders", "Seahawks": "Seattle Seahawks", "steelers": "Pittsburgh Steelers",
                "patriots": "New England Patriots", "Titans": "Tennessee Titans", "vikings": "Minnesota Vikings"
                }
team_names = [name_mapping.get(name, name) for name in channel_names]


# generate quote method that includes the question and exactly what was said
def generate_sentiment_transcripts_quotes(id, quote, question, title):
    start_time = time.time()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": f"""
                I have some quotes about NFL players and I need to analyze the sentiment of these quotes in the context of their performance and progression. 
                Each quote is in response to a question from a news reporter.
                The sentiment should be evaluated based on the quote itself, with the question providing context. 
                The sentiment score should range from -1 to 1, where -1 is strongly negative, 0 is neutral, and 1 is strongly positive. Please provide a sentiment score for each quote. Here are some guidelines:
                
                Guidelines: 
                - If the text indicates improvement, a positive trend, or positive evaluation (e.g., "This player is starting with the first team"), it should be classified as being more positive.
                - If the text is mixed or neutral without clear positive or negative implications (e.g., "This player is working really hard, but currently isn't there right now"), it should be classified as being more neutral.
                - If the text indicates a negative trend, lack of improvement, or negative evaluation, it should be classified as being negative (e.g., "This player is working with the second team. Or working with the backups.").
                - Focus on the quote for the sentiment analysis.
                - Use the question to understand the context of the quote.
                - The concise summary (title) indicates the major point of the quote and can be used for the sentiment analysis as well.
                - Provide a sentiment score from -1 to 1.
                - Output the information as a CSV with the following headers: id,score,question,quote. 
                - Ensure each row in the CSV matches the format specified in the headers. Pay attention to:
                    - No extra spaces around commas.
                    - Properly formatted quotes with no spaces immediately inside the quotes.
                    - Correct handling of special characters, such as apostrophes, in player names.
                    - Do not include the "```csv" symbols at the top or bottom of the output.
                Example Output:
                id,score,question,quote
                1,0.2,"How has this player been doing?","This player is working really hard, but currently isn't there right now."
                3,-0.6,"What are your thoughts on Player B’s recent performance in the last few games?","Despite the effort, this player's performance is still lacking."
                """
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"The question is: {question}. The quote is: {quote}. The consise summary (title) is: {title}. And, the id to use is: {id}"}
                ]
            }
        ],
        temperature=0,
    )

    print(response.choices[0].message.content)
    end_time = time.time()
    execution_time = end_time - start_time  # Calculate the execution time
    print(f"Execution time of get_csv: {execution_time:.2f} seconds")
    return response.choices[0].message.content


# generate report method that includes what reporter said
def generate_sentiment_transcripts_reports(id, report, question):
    start_time = time.time()
    print("starting")
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": f"""
                I have some reports about NFL players written by news reporters, and I need to analyze the sentiment of these reports in the context of the players' performance, roles, and projections. 
                The sentiment should be evaluated based on the content of the report, considering any mentioned questions for context if they are present. 
                The sentiment score should range from -1 to 1, where -1 is strongly negative, 0 is neutral, and 1 is strongly positive. 
                Please provide a sentiment score for each report. Here are some guidelines:
            
                Guidelines: 
                - If the text indicates improvement, a positive trend, or positive evaluation (e.g., "This player is starting with the first team"), it should be classified as being more positive.
                - If the text is mixed or neutral without clear positive or negative implications (e.g., "This player is working really hard, but currently isn't there right now"), it should be classified as being more neutral.
                - If the text indicates a negative trend, lack of improvement, or negative evaluation, it should be classified as being more negative (e.g., "This player is working with the second team. Or working with the backups.").
                - Focus on the content of the report for the sentiment analysis.
                - Use any questions (if no question is given the question will be "No Question") to understand the context better.
                - Provide a sentiment score from -1 to 1.
                - Output the information as a CSV with the following headers: id,score,question,quote. 
                - Ensure each row in the CSV matches the format specified in the headers. Pay attention to:
                    - No extra spaces around commas.
                    - Properly formatted quotes with no spaces immediately inside the quotes.
                    - Correct handling of special characters, such as apostrophes, in player names.
                    - Do not include the "```csv" symbols at the top or bottom of the output.
                Example Output:
                id,score,question,quote
                0.8,"Greg Dortch’s role is expected to expand in 2024 even though the Cardinals landed a potential superstar wide receiver in rookie first-round draft pick Marvin Harrison Jr. Dortch is projected to be the team’s primary slot receiver in addition to his work on special teams as a returner. There likely will be times when he also slides outside to the wideout spot to give opposing defenses a different look."
                -1,"Despite high expectations, Player X has been struggling to find his form during the training camp. His performance has been inconsistent, raising concerns among the coaching staff."
                """
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"The question is: {question}. The report  is: {report}. And, the id to use is: {id}"}
                ]
            }
        ],
        temperature=0,
    )
    print(response.choices[0].message.content)
    end_time = time.time()
    execution_time = end_time - start_time  # Calculate the execution time
    print(f"Execution time of get_csv: {execution_time:.2f} seconds")
    return response.choices[0].message.content


def store_sentiment(csv, query):
    db = DatabaseConnector()
    csv_file_like = StringIO(csv)
    df = pd.read_csv(csv_file_like)  # error_bad_lines=False, warn_bad_lines=True
    for i, row in df.iterrows():
        try:
            sentiment_id = row['id']
            score = row['score']
            sentiment = (score, sentiment_id)
            db.update(query, sentiment)
        except IndexError:
            print(f"No information found for {sentiment_id}")
        except RuntimeError:
            print('Error')
    db.close()


def get_quotes_for_sentiment():
    db = DatabaseConnector()
    allPlayersQuery = "SELECT * FROM quotes WHERE sentiment IS NULL"
    df_allPlayers = db.query_dataframe(allPlayersQuery)
    db.close()
    return df_allPlayers


def get_reports_for_sentiment():
    db = DatabaseConnector()
    allPlayersQuery = "SELECT * FROM reports WHERE sentiment IS NULL"
    df_allPlayers = db.query_dataframe(allPlayersQuery)
    db.close()
    return df_allPlayers


def main():
    start_time = time.time()
    sentiment_quotes = get_quotes_for_sentiment()
    for i, row in sentiment_quotes.iterrows():
        try:
            csv_sentiment = generate_sentiment_transcripts_quotes(row['id'], row['quote'], row['question'], row['title'])
            add_quotes_query = """UPDATE quotes SET sentiment = %s WHERE id = %s"""
            store_sentiment(csv_sentiment, add_quotes_query)
        except IndexError:
            print(f"No information found for")
        except RuntimeError:
            print('Error')
    print("Done quotes")
    sentiment_reports = get_reports_for_sentiment()
    for i, row in sentiment_reports.iterrows():
        try:
            print("trying")
            csv_sentiment = generate_sentiment_transcripts_reports(row['id'], row['report_text'], row['question'])
            add_reports_query = """UPDATE reports SET sentiment = %s WHERE id = %s"""
            store_sentiment(csv_sentiment, add_reports_query)
        except IndexError:
            print(f"No information found for")
        except RuntimeError:
            print('Error')
    end_time = time.time()
    execution_time = end_time - start_time  # Calculate the execution time
    print(f"Execution time: {execution_time:.2f} seconds")
    end_time = time.time()
    execution_time = end_time - start_time  # Calculate the execution time
    print(f"Execution time: {execution_time:.2f} seconds")


if __name__ == "__main__":
    main()
    print("Done!")
