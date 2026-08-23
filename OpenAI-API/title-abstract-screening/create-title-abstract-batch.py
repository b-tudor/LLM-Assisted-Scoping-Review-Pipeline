#!/usr/bin/env python

# This tool creates an OpenAI batch file for the title/abstract screening phase of
# the LLM-assisted Scoping Review Pipeline from a csv file with columns:
# id,title,abstract


import sys
import pandas as pd
import numpy as np




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
        s = s.str.replace(r'[\r\n]+', ' ', regex=True) \
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
def escape_quotes_in_columns(df: pd.DataFrame, columns=["title", "abstract"]) -> pd.DataFrame:

    for col in columns:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: x.replace('"', '\\"') if isinstance(x, str) else x
            )
    return df



# Load the CSV file
df = pd.read_csv("title-abstract-list.csv")
# Clear out any weirdo-caneero characters
df = clean_text_columns(df)
# Keep a copy (wo weirdos for future reference)
df.to_csv("title-abstract-list-CLEAN.csv")
# Change any quotes to escaped quotes so that they can be included in json objects
df = escape_quotes_in_columns(df, columns=["title", "abstract"])

# Set the upper bound for the response length (in words)
#max_token_count = 1000

for index, row in df.iterrows():
    ID = int(row["id"])
    customID = f'req-{(ID):04d}'
    
    sys_instructions = f"You are a researcher conducting a scoping review on the use of human digital twins (HDTs) in healthcare. Your first task is to identify which of these articles discusses human digital twins in healthcare, based only on the title and abstract of each article. An article must clearly describe a human digital twin that directly simulates or monitors a human biological or clinical system. Mere mentions of human digital twins as a potential tool or future research direction do not meet inclusion criteria. Do not attempt to identify new papers online, independently access the full text of papers given to you, or otherwise conduct any literature searches or research on your own.\\nThis is a reasoning task, not a pattern-matching task. You are prohibited from using keyword matching or simple word similarity techniques. Instead, only use conceptual reasoning, inference, and understanding of the meaning behind each description. Think about the relationships and underlying ideas, not just the words used. You will be provided with the title, author(s), and abstract for each article. Respond with \\\"Y\\\" if it meets inclusion criteria and \\\"N\\\" if it does not. You must choose between \\\"Y\\\" or \\\"N\\\" to the best of your ability. If an abstract is not available, use the title only to analyze.  Also return the degree of confidence of your answer (high, medium, low) and one sentence of no more than 20 words explaining your reasoning. The output must be consistent with CSV file formatting: <Y|N>,<high|medium|low>,\\\"<Reason ≤ 20 words; no internal commas>\\\"\\n\\nWork silently—no apologies or clarifying questions."

    query = f'Evaluate this document according to your instructions.\\nTitle:\\n{row["title"]}\\nAbstract:\\n{row["abstract"]}'

    json_string =f'{{"custom_id": "{customID}", "method": "POST", "url": "/v1/responses", "body": {{"model": "gpt-5", "input": [{{"role": "system", "content": "{sys_instructions}"}},{{"role": "user", "content": "{query}"}}], "reasoning":{{"effort":"high"}},"text":{{"format":{{"type":"text"}}}}, "store":false}}}}'
    
    print(f'{json_string}')
    


# client = OpenAI()

# batch_input_file_id = fileID
# batch = client.batches.create(
#     input_file_id=batch_input_file_id,
#     endpoint="/v1/chat/completions",
#     completion_window="24h",
#     metadata={
#         "description": job_desc
#     }
# )

# print(f'Batch ID: {batch.id}')