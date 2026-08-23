The first step in the work flow would be to get a CSV file named `title-abstract-list.csv`, containing a list of candidate papers and their abstracts, to be included in the review. Additionally, each paper should be assigned a unique study identifier. The header row of the CSV file (where columns are named) should be:  

`id,title,abstract`  

Once that has been assembled, create the batch input file by running 

`./create-title-abstract-batch.py > my_new_batch_file.jsonl`  

The script assumes the input file is in the same directory and named `title-abstract-list.csv`. Redirect the output to a batch file that you will upload and execute. This script will also attempt to fix or replace up problematics characters and will produce a cleaned up file named `./title-abstract-list-CLEAN.csv`. Where the title + abstract csv list is needed in downstream scripts, it will usually be better to use the 'CLEAN' version of this file instead.  
  
  
Once your batch file has been generated, upload the file to OpenAI:

`tools/upload-batch-job-file.py my_new_batch_file.json`

Make a note of the file ID for the batch file. Start the batch using the `do-batch.py` tool:

`./do-batch.py <fileID>`

Make a note of the batch ID. This will be needed to check the status or to download output files and error logs.
