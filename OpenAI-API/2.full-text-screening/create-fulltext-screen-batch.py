#!/usr/bin/env python3
import sys
import pandas as pd
import numpy as np
import json as json




# This is a function to convert \r and \n characters to spaces and it
# also gets rid of a lot of commonly malformed UTF-8/unicode characters
# It does it in place, after the dataframe is loaded, so as not to affect
# the way the original delimiters were interpreted. 

def clean_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Work only on string-like columns so numbers/dates stay untouched
    cols = df.select_dtypes(include=["object", "string"]).columns
    sub = df[cols].copy()

    # Map of Unicode curly quotes → straight quotes
    quote_map = {
        ord("“"): '"', ord("”"): '"', ord("„"): '"', ord("‟"): '"',
        ord("«"): '"', ord("»"): '"',
        ord("‘"): "'", ord("’"): "'", ord("‚"): "'", ord("‛"): "'",
    }

    def _clean_series(s: pd.Series) -> pd.Series:
        # Replace newlines/carriage returns and odd breaks with a space
        s = s.str.replace(r'[\r]+', ' ', regex=True) \
             .str.replace(r'[\n]+', '\\n', regex=True) \
             .str.replace(r'[\x0b\x0c\x85\u0085]+', ' ', regex=True)
        # Fix common mojibake for curly quotes
        s = s.str.replace('â€œ', '"', regex=False) \
             .str.replace('â€\x9d', '"', regex=False) \
             .str.replace('â€˜', "'", regex=False) \
             .str.replace('â€™', "'", regex=False)
        # Translate true Unicode curly quotes
        s = s.apply(lambda x: x.translate(quote_map) if isinstance(x, str) else x)
        # Collapse multiple spaces and trim
        s = s.str.replace(r'\s{2,}', ' ', regex=True).str.strip()
        return s

    df[cols] = sub.apply(_clean_series)
    return df


# Escapes double quotes in the specified DataFrame columns by replacing " with \"
# does not alter nan's. The df passed is modified in place. Columns is a list of
# the columns to which this processing should be applied. 
def escape_quotes_in_columns(df: pd.DataFrame, columns=["Title", "Abstract"]) -> pd.DataFrame:

    for col in columns:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: x.replace('"', '\\"') if isinstance(x, str) else x
            )
    return df


def clean_text_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean only the 'text' column in a dataframe, removing problematic characters
    like newlines, curly quotes, and mojibake.
    
    Args:
        df: DataFrame containing a 'text' column to clean
    
    Returns:
        DataFrame with cleaned 'text' column
    """
    # Check if 'text' column exists
    if 'text' not in df.columns:
        print("Warning: 'text' column not found in dataframe")
        return df
    
    # Make a copy to avoid modifying the original
    result_df = df.copy()
    
    # Map of Unicode curly quotes → straight quotes
    quote_map = {
        ord('"'): '"', 
        ord('"'): '"', 
        ord("„"): '"', ord("‟"): '"', 
        ord("«"): '"', ord("»"): '"', 
        ord("'"): "'", ord("'"): "'", ord("‚"): "'", ord("‛"): "'"
    }
    
    # Ensure the text column is string type
    result_df['text'] = result_df['text'].fillna('').astype(str)
    
    # Clean the text column
    text_series = result_df['text']
    
    # Replace newlines/carriage returns and odd breaks with a space
    text_series = text_series.str.replace(r'[\r]+', ' ', regex=True) \
                            .str.replace(r'[\n]+', '\\n', regex=True) \
                            .str.replace(r'[\x0b\x0c\x85\u0085]+', ' ', regex=True)
    
    # Fix common mojibake for curly quotes
    text_series = text_series.str.replace('â€œ', '"', regex=False) \
                            .str.replace('â€\x9d', '"', regex=False) \
                            .str.replace('â€˜', "'", regex=False) \
                            .str.replace('â€™', "'", regex=False)
    
    # Translate true Unicode curly quotes
    text_series = text_series.apply(lambda x: x.translate(quote_map) if isinstance(x, str) else x)
      
    # Update the dataframe
    result_df['text'] = text_series
    
    return result_df



sys_instructions = f"You are a researcher conducting a scoping review on the use of human digital twins (HDTs) in healthcare. You previously identified a list of articles for full text review to determine eligibility for the scoping review. Your next task is to assess whether or not each article is eligible for inclusion in your scoping review. In order to be included, they must meet the following inclusion criteria: (1) The full text of the article must be available – that is, the article must not be in abstract form only; (2) The full text must claim to have created or evaluated a non-theoretical human digital twin; (3) The full text must be peer-reviewed; (4) The full text must not be a review article, commentary, or editorial; (5) The full text must refer to a human digital twin, not a non-human digital twin; (6) The full text must be written in the English language. Include studies that claim to create human digital twins, even if the digital twin is not the focus of the article.\\nYou will be provided with a Text copy of the text available for each article, one at a time. Determine if the article meets inclusion criteria. Respond only with \\\"Y\\\" if it meets inclusion criteria and \\\"N\\\" if it does not. You must choose between \\\"Y\\\" or \\\"N\\\" to the best of your ability. Also return the degree of confidence of your answer (high, medium, low) and one sentence of no more than 20 words explaining your reasoning. The output must be consistent with CSV file formatting: <Y|N>,<high|medium|low>,\\\"<Reason ≤ 20 words; no internal commas>\\\"\\nWork silently—no apologies or clarifying questions."

record_df = pd.read_csv('title-abstract-list-CLEAN.csv')

# Load the CSV file
N=0
df_in = pd.read_csv("gpt5-title-abstract-screen-results.csv")
df = df_in.merge(record_df, on='id', how="left")
df['text']=''

# # Clear out any weirdo-caneero characters
# df = clean_text_columns(df)
# # Change any quotes to escaped quotes so that they can be included in json objects
# df = escape_quotes_in_columns(df, columns=["Title", "Abstract"])


for id, include in zip(df['id'], df['include']):
    include = include.strip()

    if include=="Y":
        content = ''
        
        N += 1

        try:
            filename = f'full-texts/{id}.txt'
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read()
                file.close()
                df.loc[df['id'] == id, 'text'] = json.dumps(content)[1:-1]
             
        except FileNotFoundError:
            print(f"File not found: {filename}")
            exit(1)
        except Exception as e:
            print(f"Error reading file: {e}")
            exit(1)



for id, include, contents in zip(df['id'], df['include'], df['text']):
    include = include.strip()
    if include=="Y":
        ID = int(id)
        customID = f'{(ID):04d}'
        query = f'Evaluate this document according to your instructions:\\n\\n{contents}'
        json_string =f'{{"custom_id": "{customID}", "method": "POST", "url": "/v1/responses", "body": {{"model": "gpt-5", "input": [{{"role": "system", "content": "{sys_instructions}"}},{{"role": "user", "content": "{query}"}}], "reasoning":{{"effort":"high"}},"text":{{"format":{{"type": "text"}}}}, "store":false}}}}'
        print(f'{json_string}')
        

