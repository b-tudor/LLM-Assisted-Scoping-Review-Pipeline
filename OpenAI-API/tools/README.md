## Tools and Utilities 

All instructions assume your are using a Linux or MacOS shell. Please adjust accordingly.  

These files are utilities for interacting with the OpenAI API. They are used to upload files, download files, start batch jobs, query the status of files and jobs, delete files, etc. 
  
Before using any of the API tools, you must install the Python openai library and export your OpenAI API key to the environment variable:  
  
OPENAI_API_KEY  
  
(See: `export-key.sh`, run using the command `source export-key.sh`)
You do need to enter your OpenAI API key into the script first.

**WARNING**: Do not use this script if you are not on a single-user secure, trusted computer, where you can't, say, leave your secret API key sitting unencrypted in a random text file.  

Additionally, you must install python's OpenAI library so the OpenAI functions will be available for import via the statement:  
`from openai import OpenAI`  
  
Additionally, there are a few tools for manipulating the OpenAI output/input into CSV files, etc. (Useful utilities that don't actually interact with the OpenAI API).
