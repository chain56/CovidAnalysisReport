import pandas as pd
import argparse
import math
import numpy as np
from datetime import datetime, timedelta

def past_n_days_process(df, ref_date_obj, n, num_states):
    """Calculate daily average cases and top/bottom states for the past n days."""

    # Filter the DataFrame for the past n days from the reference date
    start_date = ref_date_obj - timedelta(days=n-1)  
    df_period = df[(df["date"] >= start_date) & (df["date"] <= ref_date_obj)]
    
    # a. Daily average new COVID-19 cases in Malaysia; 
    daily_avg_malaysia = math.ceil(df_period["cases_new"].sum() / n)
    
    # b. Top N states by highest daily average cases
    avg_cases_by_state = df_period.groupby("state")["cases_new"].mean().reset_index()

    avg_cases_by_state["cases_new"] = avg_cases_by_state["cases_new"].apply(np.ceil).astype(int)

    top_states = avg_cases_by_state.sort_values(by="cases_new", ascending=False).head(num_states)
    
    # c. Bottom N states by lowest daily average cases
    bottom_states = avg_cases_by_state.sort_values(by="cases_new", ascending=True).head(num_states)
    
    return daily_avg_malaysia, top_states, bottom_states


def process_data(ref_date, num_states):
    """Read the CSV file, and retrieve/compute the necessary data to display in the text report."""
    try:
        data_url = 'https://raw.githubusercontent.com/MoH-Malaysia/covid19-public/main/epidemic/cases_state.csv'

        # Read the CSV file, using only the first three columns
        df = pd.read_csv(data_url, usecols=["date", "state", "cases_new"]) 

        # Format the dates in the first column to 'dd-mm-yy'
        df["date"] = pd.to_datetime(df["date"])

        # Getting the data date
        data_date = df["date"].tail(1)

        # Getting the total number of new cases in Malaysia since the data date
        total_new_cases = df["cases_new"].sum()

        # convert the user input date to datetime object to compare with the dates in the df
        ref_date_obj = datetime.strptime(ref_date, "%d-%m-%y")
        df_until_ref = df[df["date"] <= ref_date_obj]
        # Getting the total number of new cases in Malaysia since first day until the reference date (inclusive)
        total_cases_first_to_ref = df_until_ref["cases_new"].sum()

        # For now the number of days is hardcoded to 7, 30, and 90
        days = [7, 30, 90]
        results = {}
        # Get the df for the past n days
        for n in days:
            results[n] = past_n_days_process(df, ref_date_obj,n, num_states)

        current_datetime = datetime.now().strftime('%d-%m-%y %H:%M')
        data_date_str = data_date.dt.strftime('%d-%m-%y').values[0]

        return {
            'current_datetime': current_datetime,
            'ref_date': ref_date,
            'data_date': data_date_str,
            'total_new_cases': f"{total_new_cases:,}",
            'total_cases_first_to_ref': f"{total_cases_first_to_ref:,}",
            'results': results
        }
    except FileNotFoundError:
        print("The file 'covid_data.csv' was not found.")
        return None

def ref_date_validation(input_date):
    """Validate that the format of the reference date is dd-mm-yy"""
    try:
        # Try to parse input date
        return datetime.strptime(input_date, "%d-%m-%y").strftime('%d-%m-%y')
    except (ValueError, TypeError):
        print(f"Warning: Reference date format must be DD-MM-YY. The program will default to use yesterday's date.")
        return (datetime.now() - timedelta(days=1)).strftime('%d-%m-%y')
    
def num_states_validation(num_states):
    """Validate that the number of states is between 1 and 16 inclusive"""
    try:
        v = int(num_states)
        if 1 <= v <= 16:
            return v
        else:
            print(f"Warning: Number of states must be between 1 and 16. Using default value of 3.")
            return 3
    except ValueError:
        print(f"Warning: Invalid number format. Using default value of 3.")
        return 3


def generate_report(data):
    """Generate formatted text report from the processed data"""
    
    # Format the header
    report = f"""{data['current_datetime']}        MALAYSIA COVID-19 NEW CASES ANALYSIS REPORT
                            DATA DATE        : {data['data_date']}
                            TOTAL NEW CASES  : {data['total_new_cases']}

                    REFERENCE DATE {data['ref_date']} (TOTAL NEW CASE {data['total_cases_first_to_ref']})

DAYS         MALAYSIA            HIGHEST {number_of_states} STATES                     LOWEST {number_of_states} STATES
             DAILY AVERAGE    NAME                 DAILY AVERAGE   NAME                 DAILY AVERAGE

------------ ---------------- ----------------------------------  ------------------------------------
"""
    
    # Format the data for each time period
    for day in [7, 30, 90]:
        daily_avg, top_states, bottom_states = data['results'][day]
        
        # Add the first line with the day number and Malaysia average
        report += f"{day:<12} {daily_avg:<16} "
        
        # Add the first top state and bottom state
        report += f"{top_states.iloc[0]['state']:<20} {top_states.iloc[0]['cases_new']:<15} "
        report += f"{bottom_states.iloc[0]['state']:<20} {bottom_states.iloc[0]['cases_new']}\n"
        
        # Add the remaining states (without day and Malaysia average)
        for i in range(1, number_of_states):
            report += f"{'':<12} {'':<16} "
            report += f"{top_states.iloc[i]['state']:<20} {top_states.iloc[i]['cases_new']:<15} "
            report += f"{bottom_states.iloc[i]['state']:<20} {bottom_states.iloc[i]['cases_new']}\n"
        
        # Add some space between days (except after the last one)
        if day != 90:
            report += "\n"
    
    return report

def save_report(report_text, filename="covid_report.txt"):
    """Save the report text to a file"""
    with open(filename, "w") as file:
        file.write(report_text)
    print(f"Text report saved as {filename}")

if __name__ == "__main__":
    # read user inputs from command line arguments
    parser = argparse.ArgumentParser(description="COVID Cases Analysis Report")
    parser.add_argument('-D', type=str, help='Reference date in YYYY-MM-DD format')
    parser.add_argument('-T', type=int, help='(Optional input) Number of states to include (default: 3)', default=3)

    args = parser.parse_args()  
    reference_date = ref_date_validation(args.D)
    number_of_states = num_states_validation(args.T)
    data = process_data(reference_date, number_of_states)
    if data:
        html_content = generate_report(data)
    else:
        print("Failed to process data. Exiting.")
        exit(1)
    save_report(html_content, "covid_report.txt")
    
