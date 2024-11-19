#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 16:48:24 2024

@author: maggli
"""
import pandas as pd
from revenue_analysis import read_file, get_currency_code, convert_currency, get_team, export_to_csv

def sales_rev(sales_id: list, sales_df: pd.DataFrame, teams_df: pd.DataFrame, currency_df: pd.DataFrame) -> str:
    """
    Pull the sales revenue based on a given list of user IDs.

    Args:
        sales_id (list): A list containing user IDs to filter.
        sales_df (pd.DataFrame): The DataFrame containing sales information, 
                                 with at least the columns ['UserID', 'Revenue_USD'].

    Returns:
        str: A formatted string showing the total revenue for the given user IDs.
    """
    # Filter the DataFrame based on the given user IDs
    filtered_sales = sales_df[sales_df['UserID'].isin(sales_id)]    
    #Get currency codes based on the country in teams data
    teams_df = get_currency_code(teams_df)
    #Merge the revenue data with team information
    filtered_sales = get_team(filtered_sales, teams_df)
    #Convert the revenue data to USD based on the currency exchange rates
    filtered_sales = convert_currency(filtered_sales, currency_df)
    # Calculate the total revenue for the selected user IDs
    total_revenue = filtered_sales.groupby(['UserID']).agg({'Email':'first','Name':'first','Rep_Or_Director':'first',
                                                            'Status':'first', 'Region':'first','Team':'first','Country':'first',
                                                            'Currency':'first','Revenue_USD':'sum'})
    
    # Return the result as a formatted string
    return total_revenue


def get_sales_id_input():
    """
    Get user input for sales IDs, ensuring the input is a valid list of integers.
    """
    while True:
        try:
            # Input from user (expecting a comma-separated list of integers)
            user_input = input("Enter a list of user IDs (comma-separated): ")
            # Convert input to a list of integers
            sales_id = [int(id.strip()) for id in user_input.split(',')]
            return sales_id
        except ValueError:
            print("Invalid input. Please enter a comma-separated list of integers.")


def country_rev(country: tuple) -> str:
    """
    pull the country level revenue based on a given list of country

    Parameters
    ----------
    country : tuple
        DESCRIPTION.

    Returns
    -------
    str
        DESCRIPTION.

    """
    pass

def main():
    # Read the sales data from a file (assuming read_file is a function that loads a DataFrame)
    #Read the files
    try:
        teams_df = read_file('teams.csv')  # Assuming 'teams.csv' contains the team data
        revenue_df = read_file('revenue.csv')  # Assuming 'revenue.csv' contains the revenue data
        currency_df = read_file('currency.csv')  # Assuming 'currency.csv' contains currency data
        
    except (FileNotFoundError, ValueError, IOError) as e:
        print(f"Error reading files: {e}")
        return
    
    # Get user input for the list of user IDs
    sales_id = get_sales_id_input()
    
    # Call the sales_rev function to calculate total revenue for the given user IDs
    result = sales_rev(sales_id, revenue_df,teams_df,currency_df)
    
    # Optionally, export the results to a CSV file if needed
    export_to_csv(result, 'sales_revenue_output.csv')  # Replace with the appropriate output file name


# Run the main function
if __name__ == '__main__':
    main()




