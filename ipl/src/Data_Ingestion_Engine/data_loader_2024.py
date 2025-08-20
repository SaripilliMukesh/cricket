import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import re
import json
#############################################
ipl_teams = {
                            "chennai super kings": "CSK",
                            "chennai":"CSK",
                            "mumbai indians": "MI",
                            "mumbai":"MI",
                            "royal challengers bangalore": "RCB",
                            "royal challengers bengaluru":"RCB",
                            "banglore":"RCB",
                            "bengaluru":"RCB",
                            "kolkata knight riders": "KKR",
                            "kolkata":"KKR",
                            "rajasthan royals": "RR",
                            "rajasthan":"RR",
                            "sunrisers hyderabad": "SRH",
                            "sunrisers":"SRH",
                            "delhi capitals": "DC",
                            "delhi":"DC",
                            "punjab kings": "PBKS",
                            "punjab":"PBKS",
                            "lucknow super giants": "LSG",
                            "lucknow":"LSG",
                            "gujarat titans": "GT",
                            "gujarat":"GT"
                        }


                        # Function to map full team name to its short form
def shorten_team_name(team_name):
                            team_name=team_name.lower()
                            return ipl_teams.get(team_name, team_name)
def determine_batting_order(team_a, team_b, toss_win, toss_decision):
    # Strip whitespace and convert to lowercase for consistency
    toss_win = toss_win.strip().lower() if toss_win else None
    toss_decision = toss_decision.strip().lower() if toss_decision else None
    team_a = team_a.strip().lower()
    team_b = team_b.strip().lower()
    if toss_win is None or toss_decision is None:
        return None, None

    # # Print lengths and actual values to debug
    # print(f"toss_win: '{toss_win}', length: {len(toss_win)}")
    # print(f"toss_decision: '{toss_decision}', length: {len(toss_decision)}")
    # print(f"team_a: '{team_a}', team_b: '{team_b}'")

    if toss_win == team_a and toss_decision == 'bat':
        first_bat = team_a
        second_bat = team_b
    elif toss_win == team_a and toss_decision == 'bowl':
        first_bat = team_b
        second_bat = team_a
    elif toss_win == team_b and toss_decision == 'bat':
        first_bat = team_b
        second_bat = team_a
    elif toss_win == team_b and toss_decision == 'bowl':
        first_bat = team_a
        second_bat = team_b
    else:
        print(f"Unexpected values: toss_win: '{toss_win}', toss_decision: '{toss_decision}'")
        raise ValueError("Invalid input")
    
    return first_bat.upper(), second_bat.upper()




#############################################
def extract_cricket_data(url,Match_Details):
    # Send a request to the webpage
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        winner_element = soup.select_one("body > section > div > div > div > div:nth-child(2) > div:nth-child(2) > div > p")
        winner = winner_element.text.strip() if winner_element else "Winner not found"
        toss_element = soup.select_one("#info > div > div.col-xl-6.col-lg-6.col-md-12.col-12.\\.d-md-none.\\.d-lg-block.order-first.order-sm-1.order-md-1.order-lg-2 > div > div > table > tbody > tr:nth-child(6) > td:nth-child(2)")
        toss = toss_element.text.strip() if toss_element else None
        toss_info=toss
        # toss_win,toss_decision=toss.split(" & ")
        if toss:
            toss_win, toss_decision = toss.split(" & ")
        
            toss_win=toss_win.replace("toss", "")

            toss_decision=toss_decision.strip().lower()
            toss_win=shorten_team_name(toss_win.strip())
        else:
            toss,toss_info,toss_win, toss_decision=None,None,None,None
        # Extract Venue
        venue_element = soup.select_one("#info > div > div.col-xl-6.col-lg-6.col-md-12.col-12.\\.d-md-none.\\.d-lg-block.order-first.order-sm-1.order-md-1.order-lg-2 > div > div > table > tbody > tr:nth-child(5) > td:nth-child(2)")
        venue = venue_element.text.strip() if venue_element else None
        try:
            venue= venue.split(",") 
            venue=venue[-2].strip() # Use maxsplit to avoid too many values
        except ValueError:
            raise ValueError("The venue string is not in the expected format.")


        # List of accordion containers to search
        accordion_ids = ["accordionExample", "accordionExample8"]

        # Dictionary to store data for each accordion
        dataframes = {}

        for accordion_id in accordion_ids:
            accordion = soup.select_one(f"#{accordion_id}")

            if accordion:
                print(f"\n=== Extracting Data from {accordion_id} ===\n")

                table_data = []

                # Find all collapsible sections inside the accordion
                collapsible_sections = accordion.find_all("div", class_="accordion-collapse")

                for section in collapsible_sections:
                    # Find all tables inside each collapsible section
                    tables = section.find_all("table")

                    for table in tables:
                        rows = table.find_all("tr")

                        for row in rows:
                            columns = row.find_all(["td", "th"])
                            column_text = [col.text.strip() for col in columns]
                            table_data.append(column_text)

                # Convert extracted data to a DataFrame
                if table_data:
                    df = pd.DataFrame(table_data)

                    # Ensure enough columns exist before renaming
                    if df.shape[1] >= 5:
                        df.columns = ["Ball", "Fav", "Odds", "Score", "Overs"]

                        # Split 'Odds' into 'Odd_A' and 'Odd_B'
                        df[['Odd_A', 'Odd_B']] = df['Odds'].str.split("\n", expand=True, n=1)
                        df['org_Odd_A'] = df['Odd_A']
                        df['org_Odd_B'] = df['Odd_B']
                        df[['Runs', 'Wkts']] = df['Score'].str.split("/", expand=True, n=1)

                        # Split 'Overs' into 'Overs' and 'TimeStamp'
                        df[['Overs', 'TimeStamp']] = df['Overs'].str.split("\n\n", expand=True, n=1)
                        df['Overs'] = df['Overs'].str.replace(" Overs", "", regex=False)
                        df['Overs'] = pd.to_numeric(df['Overs'], errors='coerce')  # Handle non-numeric gracefully
                        df['Odd_A'] = pd.to_numeric(df['Odd_A'], errors='coerce')
                        df['Odd_B'] = pd.to_numeric(df['Odd_B'], errors='coerce')
                        df['Runs'] = pd.to_numeric(df['Runs'], errors='coerce')
                        df['Wkts'] = pd.to_numeric(df['Wkts'], errors='coerce')
                        df = df.iloc[::-1].reset_index(drop=True)
                        pattern = re.compile(r"DONO.*")
                        df['Result']=winner
                        df['Winner'] = df['Result'].str.split(' ').str[0]

                    # Apply the function to the 'Fav' column
                        df['Fav'] = df['Fav'].apply(shorten_team_name)
                        df.loc[df['Fav'].str.contains(pattern, na=False), ['Odd_A', 'Odd_B']] = 100
                        Teams,match_num=Match_Details.split(",")
                        match_num=match_num.strip()
                        match_num= re.sub(r'\D','',match_num) 
                        match_num=int(match_num)
                        df['Match Number']=match_num
                        df['Fixture Full Name']=Teams
                        team_a,team_b=Teams.split('vs')
                        team_a=shorten_team_name(team_a.strip())
                        team_b=shorten_team_name(team_b.strip())
                        df['Team A']=team_a
                        df['Team B']=team_b
                        Fixture= " vs ".join([shorten_team_name(team_a.strip()).upper(), shorten_team_name(team_b.strip()).upper()])
                        df['Fixture'] =Fixture
                        first_bat,second_bat=determine_batting_order(team_a, team_b, toss_win, toss_decision)
                        df['first_bat']=first_bat.upper()
                        df['second_bat']=second_bat.upper()
                        df['toss_info']=toss_info
                        df['toss_win']=toss_win.upper()
                        df['toss_decision']=toss_decision.upper()
                        df['year']=2024

                        ####################################################
                        #feat#
                        for index, row in df.iterrows():
                          if row['Fav'] != row['Winner'] and row['Fav'] != 'DONO (Both)':
                              df.at[index, 'Odd_A'] = -row['Odd_A']
                              df.at[index, 'Odd_B'] = -row['Odd_B']
                        #standard scale#
                        df['std_Odd_A'] = df['Odd_A'].apply(lambda x: 100 - x if x > 0 else abs(x) - 100)
                        df['std_Odd_B'] = df['Odd_B'].apply(lambda x: 100 - x if x > 0 else abs(x) - 100)

                    dataframes[accordion_id] = df
                    print(f"Data extracted successfully for {accordion_id} ✅")
                else:
                    print(f"No table data found in {accordion_id} ❌")

            else:
                print(f"Accordion container {accordion_id} not found!")

        # Get the innings data (if available)
        innings1 = dataframes.get("accordionExample", None)
        innings2 = dataframes.get("accordionExample8", None)

        if innings1 is None and innings2 is None:
            print("No data found for any accordion, skipping concatenation.")
            return None, None, None

        # Concatenate data if available
        innings1['innings'] = 1
        innings2['innings'] = 2
        result = pd.concat([innings1, innings2], ignore_index=True) if innings1 is not None and innings2 is not None else None
        result['org_overs']=result['Overs']
        result.loc[result['innings'] == 2, 'Overs'] += 20
        # Return the dataframes
        name = url[-4:-2]
        name = name.replace('-', '0')

        # Ensure the directories exist before saving the files
        os.makedirs('/home/umukesh/Desktop/algorithmic_trading/data/raw/2024/innings1', exist_ok=True)
        os.makedirs('/home/umukesh/Desktop/algorithmic_trading/data/raw/2024/innings2', exist_ok=True)
        os.makedirs('/home/umukesh/Desktop/algorithmic_trading/data/processed/2024', exist_ok=True)

        # Construct full file paths for the directories
        innings1_filename = f'innings1_{name}_2024.csv'
        innings2_filename = f'innings2_{name}_2024.csv'
        result_filename = f'data_{name}_2024.csv'

        innings1_filepath = f'/home/umukesh/Desktop/algorithmic_trading/data/raw/2024/innings1/{innings1_filename}'
        innings2_filepath = f'/home/umukesh/Desktop/algorithmic_trading/data/raw/2024/innings2/{innings2_filename}'
        result_filepath = f'/home/umukesh/Desktop/algorithmic_trading/data/raw/2024/match/{result_filename}'

        # Write DataFrames to CSV if they are not None
        if innings1 is not None:
            innings1.to_csv(innings1_filepath, index=False)
            print(f"Data for innings1 saved to {innings1_filepath}")
        
        if innings2 is not None:
            innings2.to_csv(innings2_filepath, index=False)
            print(f"Data for innings2 saved to {innings2_filepath}")
        
        if result is not None:
            result.to_csv(result_filepath, index=False)
            print(f"Data for result saved to {result_filepath}")

        return innings1, innings2, result



    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

        # Extract 'name' from URL for match number and filenames
        name = url[-4:-2]
        name = name.replace('-', '0')  # Ensure 'name' is formatted correctly

        # Create an empty DataFrame with the required columns
        columns = ['Ball', 'Fav', 'Odds', 'Score', 'Overs', 'Odd_A', 'Odd_B', 'org_Odd_A',
                'org_Odd_B', 'Runs', 'Wkts', 'TimeStamp', 'Result', 'Winner',
                'Match Number', 'Fixture Full Name', 'Team A', 'Team B', 'Fixture',
                'first_bat', 'second_bat', 'toss_info', 'toss_win', 'toss_decision',
                'year', 'std_Odd_A', 'std_Odd_B', 'innings', 'org_overs']

        empty_row = {col: None for col in columns}
        empty_row['Match Number'] = name  # Set the 'Match Number' to the extracted 'name'

        # Create a DataFrame with a single row (all None except 'Match Number')
        df_empty = pd.DataFrame([empty_row], columns=columns)

        # Set file paths for saving the empty DataFrame
        innings1_filename = f'innings1_{name}_2024.csv'
        innings2_filename = f'innings2_{name}_2024.csv'
        result_filename = f'data_{name}_2024.csv'

        innings1_filepath = f'/home/umukesh/Desktop/algorithmic_trading/data/raw/2024/innings1/{innings1_filename}'
        innings2_filepath = f'/home/umukesh/Desktop/algorithmic_trading/data/raw/2024/innings2/{innings2_filename}'
        result_filepath = f'/home/umukesh/Desktop/algorithmic_trading/data/raw/2024/match/{result_filename}'

        # Ensure the directories exist before saving the files
        os.makedirs('/home/umukesh/Desktop/algorithmic_trading/data/raw/2024/innings1', exist_ok=True)
        os.makedirs('/home/umukesh/Desktop/algorithmic_trading/data/raw/2024/innings2', exist_ok=True)
        os.makedirs('/home/umukesh/Desktop/algorithmic_trading/data/processed/2024', exist_ok=True)

        # Save the empty DataFrame to CSV files
        df_empty.to_csv(innings1_filepath, index=False)
        df_empty.to_csv(innings2_filepath, index=False)
        df_empty.to_csv(result_filepath, index=False)

        print(f"Empty data saved to {innings1_filepath}, {innings2_filepath}, {result_filepath}")

        # Now handle the missing_data.json to add the 'name'

        # Check if the missing_data.json file exists
        missing_data_path = '/home/umukesh/Desktop/algorithmic_trading/data/raw/missing_data.json'

    # Check if the missing_data.json file exists
        if os.path.exists(missing_data_path):
            try:
                with open(missing_data_path, 'r') as file:
                    missing_data = json.load(file)
            except (json.JSONDecodeError, TypeError):
                print("Error: The JSON file is empty or malformed. Initializing empty data.")
                missing_data = {}
        else:
            missing_data = {}  # Initialize an empty dictionary if the file doesn't exist

        # Ensure all years exist in the dictionary
        # Add more years as needed
        year=2024
        if str(year) not in missing_data:
                missing_data[str(year)] = []

        # Append the match name to the correct year without duplicates
        if name not in missing_data['2024']:
            missing_data['2024'].append(name)

        # Save the updated data back to the JSON file
        with open(missing_data_path, 'w') as file:
            json.dump(missing_data, file, indent=4)

        print(f"Added {name} to missing_data.json")

        # Return None as no actual data was retrieved
        return None, None, None




# Example usage:
# url = "https://www.cricketmazza.com/gameinfo/indian-premier-league-2024-kolkata-knight-riders-royal-challengers-bengaluru-ipl--36th"
# innings1, innings2, result = extract_cricket_data(url)


df = pd.read_csv('/home/umukesh/Desktop/algorithmic_trading/data/raw/URL/ipl2024.csv')
match_url_list = df['Match URL'].tolist()
Match_Details=df['Match Details'].tolist()

for i,j in zip(match_url_list,Match_Details):
    extract_cricket_data(i,j)
