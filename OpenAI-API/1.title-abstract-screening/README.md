The first step in the work flow would be to get a CSV file named `title-abstract-list.csv`, containing a list of all the candidate papers and their abstracts. One line/row for each paper that is in consideration for inclusion in the review. Additionally, each paper should be assigned a unique study identifier. The header row of the CSV file (where columns are named) should be:  

`id,title,abstract`  

Once that has been assembled, create the batch input file by running: 

`./create-title-abstract-batch.py > my_new_batch_file.jsonl`  
  
... or, for example:    
  
`./create-title-abstract-batch.py > batchJob-sample-title-abstract-screen.jsonl`  


The script assumes the input file is in the same directory and named `title-abstract-list.csv`. Redirect the output to a batch file that you will upload and execute. This script will also attempt to fix or replace up problematics characters and will produce a cleaned up file named `./title-abstract-list-CLEAN.csv`. Where the title + abstract csv list is needed in downstream scripts, it will usually be better to use the 'CLEAN' version of this file instead.  
  
  
Once your batch file has been generated, upload the file to OpenAI:

`tools/upload-batch-job-file.py my_new_batch_file.json`

The output of this should look something like:
```
Batch file name: batch_title-abs-screen.jsonl
FileObject(id='file-4httJRGxDQJbUtqJqDWa6G', bytes=509860, created_at=1787512530, filename='batch_title-abs-screen.jsonl', object='file', purpose='batch', status='processed', expires_at=1790104530, status_details=None)

Batch File ID: file-4httJRGxDQJbUtqJqDWa6G
         Name: batch_title-abs-screen.jsonl
         Size: 509860
      Purpose: batch
 status_deets: None
```
Make a note of the Batch File ID. Start the batch using the `do-batch.py` tool:

`./do-batch.py <fileID>`

or in the case of the example:  
  
`./do-batch.py file-4httJRGxDQJbUtqJqDWa6G`  

The batch id will be output. The output should look like this:

`Batch ID: batch_6a8b47c384748190bb22810ba35cb1dc`
  
Make a note of the batch ID. This will be needed to check the status or to download output files and error logs.

Eg:

``
yields:  
```
Batch(id='batch_6a8b4a388a088190a3ddfa9bb635b4da', completion_window='24h', created_at=1787513400, endpoint='/v1/responses', input_file_id='file-4httJRGxDQJbUtqJqDWa6G', object='batch', status='validating', cancelled_at=None, cancelling_at=None, completed_at=None, error_file_id=None, errors=None, expired_at=None, expires_at=1787599800, failed_at=None, finalizing_at=None, in_progress_at=None, metadata={'description': 'ENTER JOB DESCRIPTION HERE (OPTIONAL).'}, output_file_id=None, request_counts=BatchRequestCounts(completed=0, failed=0, total=0), model=None, usage={'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0, 'input_tokens_details': {'cached_tokens': 0}, 'output_tokens_details': {'reasoning_tokens': 0}})

      Batch ID: batch_6a8b4a388a088190a3ddfa9bb635b4da
          File: file-4httJRGxDQJbUtqJqDWa6G
        Errors: None
        Status: validating
Output File ID: None




Batch(id='batch_6a8b4a388a088190a3ddfa9bb635b4da', completion_window='24h', created_at=1787513400, endpoint='/v1/responses', input_file_id='file-4httJRGxDQJbUtqJqDWa6G', object='batch', status='in_progress', cancelled_at=None, cancelling_at=None, completed_at=None, error_file_id=None, errors=None, expired_at=None, expires_at=1787599800, failed_at=None, finalizing_at=None, in_progress_at=1787513463, metadata={'description': 'ENTER JOB DESCRIPTION HERE (OPTIONAL).'}, output_file_id=None, request_counts=BatchRequestCounts(completed=0, failed=0, total=99), model='gpt-5-2025-08-07', usage={'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0, 'input_tokens_details': {'cached_tokens': 0}, 'output_tokens_details': {'reasoning_tokens': 0}})

      Batch ID: batch_6a8b4a388a088190a3ddfa9bb635b4da
          File: file-4httJRGxDQJbUtqJqDWa6G
        Errors: None
        Status: in_progress
Output File ID: None








Batch(id='batch_6a8b47c384748190bb22810ba35cb1dc', completion_window='24h', created_at=1787512771, endpoint='/v1/responses', input_file_id='file-4httJRGxDQJbUtqJqDWa6G', object='batch', status='completed', cancelled_at=None, cancelling_at=None, completed_at=1787513142, error_file_id=None, errors=None, expired_at=None, expires_at=1787599171, failed_at=None, finalizing_at=1787513137, in_progress_at=1787512833, metadata={'description': 'ENTER JOB DESCRIPTION HERE (OPTIONAL).'}, output_file_id='file-UVVggugJ3PchPjXDUmSXUU', request_counts=BatchRequestCounts(completed=99, failed=0, total=99), model='gpt-5-2025-08-07', usage={'input_tokens': 99355, 'output_tokens': 112736, 'total_tokens': 212091, 'input_tokens_details': {'cached_tokens': 0}, 'output_tokens_details': {'reasoning_tokens': 106752}})

      Batch ID: batch_6a8b47c384748190bb22810ba35cb1dc
          File: file-4httJRGxDQJbUtqJqDWa6G
        Errors: None
        Status: completed
Output File ID: file-UVVggugJ3PchPjXDUmSXUU
```

Finally, raw output can be parsed into a csv file for the next step using the generic `batchOut2csv.py` (which will not include CSV header rows, which you will need to add manually), or using  `batchOut2csv-TitleAbScreen.py` which will do the same thing but will add the header rows for you. In both cases, output will need to be redirected to an input file for use in the next stage. E.g.:

`batchOut2csv.py gpt5-batch-out_title-abs-screen.jsonl > gpt5-title-abstract-screen-results.csv`
