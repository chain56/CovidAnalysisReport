# COVID-19 Analysis Report Generator

A Python tool that generates comprehensive COVID-19 case analysis reports for Malaysia, providing insights into national and state-level trends over various time periods.

## Features

- Analyzes COVID-19 case data from Malaysia's Ministry of Health public repository
- Generates reports for customizable reference dates
- Calculates daily average cases for 7-day, 30-day, and 90-day periods
- Identifies states with highest and lowest case averages
- Outputs clean, formatted reports in text format

## Installation

### Prerequisites

- Python 3.11 or higher
- Pandas library

```bash
pip install pandas
```

## Usage

Run the program with the following command:

```bash
python covidAnalysis.py [-D REF_DATE] [-T NUM_STATES] 
```

### Parameters

| Parameter | Description | Default | Format |
|-----------|-------------|---------|--------|
| `-D` | Reference date | Yesterday | DD-MM-YY |
| `-T` | Number of states  | 3 | Integer (1-16) |

### Examples

Basic usage (uses yesterday's date and shows 3 states):
```bash
python covidAnalysis.py
```

Specify a reference date:
```bash
python covidAnalysis.py -D 20-09-20
```

Customize number of states to display:
```bash
python covidAnalysis.py -D 20-09-20 -T 4
```

## Data Source

The program fetches data from Malaysia's Ministry of Health public GitHub repository:
`https://raw.githubusercontent.com/MoH-Malaysia/covid19-public/main/epidemic/cases_state.csv`

## Notes

- The average values are rounded up to the nearest whole number
- The program assumes the CSV data is sorted by date in ascending order
- Maximum number of states is 16
-Done the following input validations:
    - The reference date must follow the following format "DD-MM-YY"
    - Number of states must be 1-16