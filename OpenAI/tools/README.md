These files are utilities for interacting with the OpenAI API. 
They are used to upload files, download files, start batch jobs,
query the status of files and jobs, delete files, etc. 

Before using any of these tools, you must export your OpenAI API
key to the environment variable:

OPENAI_API_KEY
(See: export-key.sh)

Additionally, you must install python's OpenAI library so the 
OpenAI functions will be available for import via the statement:
from openai import OpenAI

Additionally, there are a few tools for manipulating the OpenAI
output/input into CSV files, etc. (Useful utilities that don't 
actually interact with the OpenAI API).
