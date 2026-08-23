To generate the batch file for upload to the OpenAI API, execute 
the python script from the command line sending the raw input file 
as the first parameter and redirect the output to a JSONL file:

`./create_batch_fr_csv-cat.py id-full-text_sample-raw-input.csv > cat_sample-input.jsonl`

Then upload the batch job to the OpenAI API using the `upload-batch-job-file.py` utility located in the `tools/` directory. If this script is in your local directory, run:

`./upload-batch-job-file.py cat_sample-input.jsonl`

Make a note of the file ID for the batch file. Start the batch using the `do-batch.py` tool:

`./do-batch.py <fileID>`
