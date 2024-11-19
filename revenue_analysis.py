#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 16:44:53 2024

@author: maggli
"""
import pandas as pd
import numpy as np


def read_file(filename: str) -> pd.DataFrame:
    """
    Reads the contents of a file using pandas and returns it as a DataFrame.

    Args:
        filename (str): The path to the file to read.

    Returns:
        pd.DataFrame: A DataFrame containing the file's contents.
    
    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If there is an issue reading the file.
    """
    try:
        # Use pandas to read the file into a DataFrame
        df = pd.read_csv(filename)
        return df
    except FileNotFoundError:
        # Handle the case where the file does not exist
        raise FileNotFoundError(f"The file {filename} does not exist.")
    except pd.errors.EmptyDataError:
        # Handle the case where the file is empty
        raise ValueError(f"The file {filename} is empty.")
    except pd.errors.ParserError as e:
        # Handle errors while parsing the file
        raise ValueError(f"Error parsing the file {filename}: {e}")
    except Exception as e:
        # Catch any other unexpected errors
        raise IOError(f"An error occurred while reading the file: {e}")


def get_currency_code(teams_df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a 'Currency' column to the DataFrame based on the team's country.

    This function assigns a currency code to each row in the DataFrame based on the 
    'Country' column. It uses nested conditions to determine the appropriate currency 
    for each country.

    Args:
        teams_df (pd.DataFrame): DataFrame containing team information, 
                                 with at least a 'Country' column.

    Returns:
        pd.DataFrame: The updated DataFrame with an additional 'Currency' column.

    Example:
        teams_df = pd.DataFrame({
            'Team': ['A', 'B', 'C'],
            'Country': ['US', 'Japan', 'Netherlands']
        })
        
        result = get_currency_code(teams_df)
        
        # Resulting DataFrame:
        #   Team       Country Currency
        # 0    A           US      USD
        # 1    B        Japan      USD
        # 2    C  Netherlands      EUR
    """
    # Add 'Currency' column based on the 'Country' column
    teams_df['Currency'] = np.where(
        teams_df['Country'] == 'US', 'USD',  # If the country is US, assign USD
        np.where(
            teams_df['Country'] == 'Japan', 'JPY',  # If the country is Japan, assign USD
            np.where(
                (teams_df['Country'] == 'Netherlands') | (teams_df['Country'] == 'Spain'), 'EUR',  # If Netherlands or Spain, assign EUR
                np.where(
                    teams_df['Country'] == 'Australia', 'AUD',  # If Australia, assign AUD
                    np.where(
                        teams_df['Country'] == 'UK', 'GBP',  # If UK, assign GBP
                        np.where(
                            teams_df['Country'] == 'Brazil', 'BRL',  # If Brazil, assign BRL
                            np.where(
                                teams_df['Country'] == 'Canada', 'CAD',  # If Canada, assign CAD
                                np.where(
                                    teams_df['Country'] == 'India', 'INR',  # If India, assign INR
                                    np.where(
                                        teams_df['Country'] == 'Mexico', 'MXN',  # If Mexico, assign MXN
                                        np.where(
                                            teams_df['Country'] == 'Singapore', 'SGD',  # If Singapore, assign SGD
                                            'EUR')))))))))) # Default to USD for all other countries
    
    return teams_df


def convert_currency(revenue_df: pd.DataFrame, currency_df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts revenue values from various currencies to USD using exchange rates.

    This function merges a revenue dataset with a currency dataset based on matching 
    currency and date values, then calculates the USD equivalent for each revenue entry.

    Args:
        revenue_df (pd.DataFrame): DataFrame containing revenue information with at least the columns:
                                   ['Team_Currency', 'Date', 'Revenue'].
        currency_df (pd.DataFrame): DataFrame containing exchange rate information with at least the columns:
                                    ['FROM_CURRENCY', 'DATE', 'EXCHANGE_RATE'].

    Returns:
        pd.DataFrame: A new DataFrame containing the merged data with an additional column 
                      'Revenue_USD' that holds the revenue converted to USD.

    Example:
        revenue_df = pd.DataFrame({
            'Team_Currency': ['MXN', 'JPY', 'AUD'],
            'Date': ['2024-09-02', '2024-02-05', '2024-07-08'],
            'Revenue': [1000, 200000, 1500]
        })
        
        currency_df = pd.DataFrame({
            'FROM_CURRENCY': ['MXN', 'JPY', 'AUD'],
            'DATE': ['2024-09-02', '2024-02-05', '2024-07-08'],
            'EXCHANGE_RATE': [0.05073, 0.00674, 0.67495]
        })

        result = convert_currency(revenue_df, currency_df)
        
        # Resulting DataFrame:
        #   Team_Currency        Date  Revenue FROM_CURRENCY      DATE  EXCHANGE_RATE  Revenue_USD
        # 0            MXN  2024-09-02   1000           MXN 2024-09-02       0.05073     50.73
        # 1            JPY  2024-02-05  200000           JPY 2024-02-05       0.00674   1348.00
        # 2            AUD  2024-07-08    1500           AUD 2024-07-08       0.67495   1012.43
    """
    # Merge the datasets based on currency and date
    revenue_df['Date'] = pd.to_datetime(revenue_df['Date'])
    currency_df['DATE'] = pd.to_datetime(currency_df['DATE'])
    revenue_df['Revenue'] = revenue_df['Revenue'].astype(float)
    new_df = pd.merge(revenue_df, currency_df, how='left', left_on=['Currency', 'Date'], right_on=['FROM_CURRENCY', 'DATE'])

    # Calculate revenue in USD
    new_df['Revenue_USD'] = np.where(new_df['Currency']=='USD',new_df['Revenue'],new_df['Revenue'] * new_df['EXCHANGE_RATE'])

    return new_df


def get_team(revenue_df: pd.DataFrame, teams_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merges revenue data with team data to associate each revenue record with its corresponding team.

    This function performs a left join between `revenue_df` and `teams_df` based on the 
    `UserID` column in `revenue_df` and the `ID` column in `teams_df`.

    Args:
        revenue_df (pd.DataFrame): DataFrame containing revenue information with at least the column:
                                   ['UserID'].
        teams_df (pd.DataFrame): DataFrame containing team information with at least the column:
                                 ['ID'].

    Returns:
        pd.DataFrame: A new DataFrame containing the merged data, associating each revenue 
                      record with its corresponding team.

    Example:
        revenue_df = pd.DataFrame({
            'UserID': [1, 2, 3],
            'Revenue': [1000, 1500, 2000]
        })
        
        teams_df = pd.DataFrame({
            'ID': [1, 2, 4],
            'Team': ['A', 'B', 'C']
        })

        result = get_team(revenue_df, teams_df)

        # Resulting DataFrame:
        #    UserID  Revenue   ID Team
        # 0       1     1000  1.0    A
        # 1       2     1500  2.0    B
        # 2       3     2000  NaN  NaN
    """
    # Perform a left join between revenue_df and teams_df
    df = pd.merge(revenue_df, teams_df, how='left', left_on='UserID', right_on='ID')
    
    return df
    

def get_quarterly_rev(revenue_df:pd.DataFrame) -> pd.DataFrame:
    """
    Groups the revenue data by 'ID' and 'Date', and aggregates it to calculate quarterly revenue.

    This function groups the revenue data by 'ID' and 'Date', then aggregates other columns
    like 'Email', 'Name', and 'Team Name' by taking the first entry within each group.
    The 'Revenue_USD' column is summed to get the total revenue for each group. 

    Args:
        revenue_df (pd.DataFrame): DataFrame containing revenue data, including 'ID', 'Date', 'Email', 
                                   'Name', 'Team Name', and 'Revenue_USD' columns.

    Returns:
        pd.DataFrame: A new DataFrame with aggregated data by 'ID' and 'Date', including the summed 
                      'Revenue_USD' and the first entries for 'Email', 'Name', and 'Team Name'.
                      
    Example:
        revenue_df = pd.DataFrame({
            'ID': [1, 1, 2, 2],
            'Date': ['2024-01-01', '2024-01-01', '2024-01-01', '2024-01-02'],
            'Email': ['email1', 'email1', 'email2', 'email2'],
            'Name': ['John', 'John', 'Tom', 'Tom'],
            'Team Name': ['A', 'A', 'B', 'B'],
            'Revenue_USD': [1000, 1500, 2000, 2500]
        })
        
        result = get_quarterly_rev(revenue_df)
        
        # Resulting DataFrame:
        #    ID        Date  Email  Name  Team Name  Revenue_USD
        # 0   1  2024-01-01  email1  John          A         2500
        # 1   2  2024-01-01  email2   Tom          B         2000
        # 2   2  2024-01-02  email2   Tom          B         2500
    """
    # Group the DataFrame by 'ID' and 'Date', and aggregate the values
    df = revenue_df.groupby(['ID','Date'],as_index=False).agg({'Email':'first','Name':'first','Team':'first','Revenue_USD':'sum'})
    
    return df



def get_total_monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """
    Groups the data by month and calculates total revenue for each month.
    
    Args:
        df (pd.DataFrame): The input DataFrame containing a 'Date' and 'Revenue_USD' column.
    
    Returns:
        pd.DataFrame: DataFrame with total revenue for each month.
    """
    df['Month'] = pd.to_datetime(df['Date']).dt.to_period('M')
    return df.groupby('Month')['Revenue_USD'].sum().reset_index()


def export_to_csv(df: pd.DataFrame, file_path: str) -> None:
    """
    Exports the DataFrame to a CSV file.

    Args:
        df (pd.DataFrame): The DataFrame to export.
        file_path (str): The path (including the file name) where the CSV should be saved.

    Returns:
        None: Saves the DataFrame as a CSV file at the specified location.

    Raises:
        ValueError: If the DataFrame is empty.
        IOError: If there is an issue writing the file.
    """
    if df.empty:
        raise ValueError("The DataFrame is empty and cannot be exported.")

    try:
        # Export the DataFrame to a CSV file
        df.to_csv(file_path, index=False)
        print(f"DataFrame successfully exported to {file_path}")
    except Exception as e:
        raise IOError(f"An error occurred while exporting the DataFrame to CSV: {e}")

def main():
    #Read the files
    try:
        teams_df = read_file('teams.csv')  # Assuming 'teams.csv' contains the team data
        revenue_df = read_file('revenue.csv')  # Assuming 'revenue.csv' contains the revenue data
        currency_df = read_file('currency.csv')  # Assuming 'currency.csv' contains currency data
        
    except (FileNotFoundError, ValueError, IOError) as e:
        print(f"Error reading files: {e}")
        return

    #Get currency codes based on the country in teams data
    teams_df = get_currency_code(teams_df)
    #Merge the revenue data with team information
    revenue_df = get_team(revenue_df, teams_df)
    #Convert the revenue data to USD based on the currency exchange rates
    revenue_df = convert_currency(revenue_df, currency_df)
    export_to_csv(revenue_df, 'revenue_df.csv')
    #Get quarterly revenue
    quarterly_rev = get_quarterly_rev(revenue_df)
    export_to_csv(quarterly_rev, 'quarterly_rev.csv')
    #Step 6: Get monthly revenue
    monthly_rev = get_total_monthly_revenue(revenue_df)
    export_to_csv(monthly_rev, 'monthly_rev.csv')

# Ensure to call main function to execute the code
if __name__== '__main__':
    main()
    import doctest

    doctest.testmod(verbose=True)