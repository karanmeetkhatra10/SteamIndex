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
import csv
import whisper
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

def get_audio_files(channel_name, chunk_length_ms=600000, max_file_size_mb=15):
    folder_path = f'videos/{channel_name}'
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.mp3'):
            # Getting the date from the name of the file (to be used when storing)
            date = filename[:8]
            date_obj = datetime.strptime(date, "%Y%m%d")
            formatted_date = date_obj.strftime("%Y-%m-%d")
            # Extracting title of the file to be used when adding source to the db
            title = filename[20:-4]
            print(title)
            # Get the full path to the file
            file_path = f'{folder_path}/{filename}'
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)  # checking the size o
            print(file_size_mb)
            all_transcriptions = []
            # if file_size_mb > max_file_size_mb:
            #     chunk_paths = split_large_file(file_path, chunk_length_ms)
            #     for chunk_path in chunk_paths:
            #         transcription = transcribe_audio(chunk_path)
            #         all_transcriptions.append(transcription)
            #     print("done transcribing chunks")
            #     for chunk_path in chunk_paths:
            #         gc.collect()
            #         print("Removing chunk")
            #         os.remove(chunk_path)
            # else:
            #     print("Not doing much")
            #     transcription = transcribe_audio(file_path)
            #     all_transcriptions.append(transcription)
            # full_transcription = ' '.join(all_transcriptions)
            transcription = transcribe_audio(file_path)
            print(f"Transcription for {filename}:\n{transcription}")

            # print(f"Transcription for {filename}:\n{full_transcription}")
            csv_ai = generate_quotes(transcription, channel_name, title)
            store_quotes(csv_ai, channel_name, formatted_date)
            os.remove(file_path)
            print(f"Deleted original file: {file_path}")


# def transcribe_audio(file_path):
#     start_time = time.time()
#     print("Transcribing...")
#     # audio_file = open(file_path, "rb")
#     with open(file_path, "rb") as audio_file:
#         transcription = client.audio.transcriptions.create(
#             model="whisper-1",
#             file=audio_file
#         )
#     end_time = time.time()
#     execution_time = end_time - start_time  # Calculate the execution time
#     print(f"Execution time of transcribing: {execution_time:.2f} seconds")
#     return transcription.text


def transcribe_audio(file_path):
    start_time = time.time()
    print("Transcribing...")

    model = whisper.load_model("tiny.en")
    model = model.float()

    result = model.transcribe(file_path)

    end_time = time.time()
    execution_time = end_time - start_time  # Calculate the execution time
    print(f"Execution time of transcribing: {execution_time:.2f} seconds")
    return result["text"]


def split_large_file(file_path, chunk_length_ms=600000):
    print("Splitting...")
    audio = AudioSegment.from_file(file_path)
    chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
    chunk_paths = []
    base, ext = os.path.splitext(file_path)
    for i, chunk in enumerate(chunks):
        chunk_name = f"{base}_part{i}{ext}"
        chunk.export(chunk_name, format="mp3")
        chunk_paths.append(chunk_name)
    return chunk_paths


# generate quote method that includes the question and exactly what was said
def generate_quotes(transcription, channel_name, title):
    start_time = time.time()
    print("running")
    team = name_mapping.get(channel_name, channel_name)
    df_allPlayers = get_allplayers_from_team(team)  # all players from db
    allPlayers_values = df_allPlayers['name'].tolist()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": f"""The audio provided is a transcript of a press conference. The speaker will talk about players on the roster and provide insights into their performance, among other topics.

Your task is to extract relevant quotes about the players from the list provided ({allPlayers_values}). The list includes the correct names of all players on the team, which should be used as a reference to ensure accuracy when printing out names. The player names may be mentioned in various forms such as first names, last names, or nicknames. Please refer to the provided list to resolve any ambiguities.

Instructions:
1. Output the information as a CSV with the following headers: name,title,question,quote,speaker.
2. For each player mentioned in the press conference, provide:
   - The player's full name as listed in {allPlayers_values}.
   - A concise summary (title) of the major point said about the player in a few words.
   - The question that prompted the response. If no specific question prompted the response, write "no question".
   - The exact quote about the player. Clean up the text to correct any grammatical errors, spelling mistakes, or incoherent sentences while preserving the original meaning and content. Ensure there are no extra spaces around commas and quotes within the quote field.
   - The name of the speaker who made the quote. Oftentimes, the name of the speaker can be extracted from the title of the transcription file: {title}.
3. Combine all quotes about the same player throughout the conference into a single entry. Ensure the information is comprehensive.
4. Focus on extracting quotes that provide **specific insights into player performance and status**. Only include quotes that address the following types of information:
   - "getting more playing time"
   - "running with the first team" or changes in team roles
   - "currently injured" or injury status
   - "will see increased usage" or expected impact on the team
   - "will lead the backfield" or significant roles
   - "will get more carries"
   - "needs a lot of work" or performance concerns
   - "is third on the depth chart" or position on the depth chart
   - Avoid quotes that are general praise, contract-related, speculative, or not closely related to these performance and status details.
   
5. Evaluate the relevance of each quote based on the summary (title):
   - Include quotes where the title indicates specific, actionable insights about the player's current performance, role, or status (e.g., "Building chemistry with Bryce Young", "Running with first team").
   - Exclude quotes where the title indicates speculative comments, general praise, or non-specific insights (e.g., "Flexibility in situational passes", "Finding check downs", "Massive receiver with explosive ability").

6. Ensure each row in the CSV matches the format specified in the headers. Pay attention to:
   - No extra spaces around commas.
   - Properly formatted quotes with no spaces immediately inside the quotes.
   - Correct handling of special characters, such as apostrophes, in player names.
   - Ensure that apostrophes within quotes or the question are preserved correctly and do not cause formatting issues.
   - Verify that all lines in the CSV are complete and avoid EOF issues by ensuring each row follows the correct structure and format without missing or extra fields.

7. Do not include the "```csv" symbols at the top or bottom of the output.

Example Output:
name,title,question,quote,speaker
Brock Bowers,Lots of work,"What about Brock Bowers? I know he's a tight end, but he's really a weapon. I mean just what do you see when you see him?","Brock will get a lot of work this year and has the ability of being a good tight end.",John Harbaugh
Isaiah Michael,Will be a big part of the offense,"How about Isaiah Michael? We know what he can do over the last couple of years. He's made quite a few wild plays this week. How impressed have you been with his game?","He's talented. He's going to be a big part of what we do and have a big role in the offense with the first team.",John Harbaugh

Please ensure the final CSV is properly formatted and contains accurate information.


"""},
            {"role": "user", "content": [
                {"type": "text", "text": f"The audio transcription is: {transcription}"}
            ],
             }
        ],
        temperature=0,
    )
    print(response.choices[0].message.content)
    end_time = time.time()
    execution_time = end_time - start_time  # Calculate the execution time
    print(f"Execution time of get_csv: {execution_time:.2f} seconds")
    return response.choices[0].message.content


def store_quotes(csv_data, channel_name, date):
    db = DatabaseConnector()
    csv_file_like = StringIO(csv_data)
    # Use csv.DictReader to handle the CSV parsing more robustly
    reader = csv.DictReader(csv_file_like)
    rows = list(reader)
    df = pd.DataFrame(rows)
    team = name_mapping.get(channel_name, channel_name)
    df_allPlayers = get_allplayers_from_team(team)  # all players from db
    add_tweet = ("INSERT INTO quotes"
                 "(name, team, position, question, quote, source, title, date)"
                 "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")

    for i, row in df.iterrows():
        try:
            player_name = row['name']
            player_info = df_allPlayers[df_allPlayers['name'] == player_name].iloc[0]
            position = player_info['position']
            team = player_info['team']
            tweets = (player_name, team, position, row['question'], row['quote'], row['speaker'], row['title'], date)
            db.insert(add_tweet, tweets)
        except IndexError:
            print(f"No information found for {player_name}")
        except RuntimeError:
            print('Error')
    db.close()


def get_allplayers_from_team(team):
    db = DatabaseConnector()
    allPlayersQuery = "SELECT * FROM allplayers WHERE team = %s"
    df_allPlayers = db.query_dataframe(allPlayersQuery, (team,))
    db.close()
    return df_allPlayers


# # Define a function to check for fuzzy matches using rapidfuzz
# def is_fuzzy_match(value, choices, threshold=80):
#     return any(fuzz.ratio(value, choice) >= threshold for choice in choices)
#
#
# def filtered_players(df, df_allPlayers):
#     # Filter the original DataFrame to keep rows where 'name' is a fuzzy match with the
#     allPlayers_values = df_allPlayers['name'].tolist()
#     filteredPlayers_df = df[df['name'].apply(lambda x: is_fuzzy_match(x, allPlayers_values))]
#
#     return filteredPlayers_df


def main():
    start_time = time.time()
    for channel_name in channel_names:
        get_audio_files(channel_name)
    end_time = time.time()
    execution_time = end_time - start_time  # Calculate the execution time
    print(f"Execution time: {execution_time:.2f} seconds")


if __name__ == "__main__":
    main()
    print("Done!")
