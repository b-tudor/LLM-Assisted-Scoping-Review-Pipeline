To create a batch job for the synthesis stage of the review, you need the `master-text-list.csv` created during stage 3:  
  
`./create-batch-synth.py master-text-list.csv > batch-synth.jsonl`

Then, submit this batch file to the API in the usual manner. 