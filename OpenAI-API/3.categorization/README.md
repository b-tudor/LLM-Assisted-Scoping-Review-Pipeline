At this point, we need to parse through the results from the full-text screening and make a master list (a CSV file) that ONLY contains papers selected for the review, along with the full text of said papers.
If you run the script `create-fulltxt-infile.py` on the CSV output from the full-text screening step, such a master list can be easily generated. E.g.:  
  
`./create-fulltxt-input-file.py gpt5-fulltxt-results.csv > master-text-list.csv`  
  
To be clear, every line in master-text-list.csv is a paper that you will include in the categorization and synthesis steps of this review, and there is 1 row for every such paper. This CSV file only has 2 columns: 'id' and 'text', where 'text' is the full text of the article (which typically includes the Title, Abstract, Authors and References).  
  
To run this, you will need the CSV formatted results from the full text screening phase, as well as access to the directory with the full-text files. As an example, we have put a copy of that directory in the local folder for your convenience (since this is a toy example), but in practice you would probably want to use a path to a common directory (or you would want all these scripts located in the same directory as the `full-texts/` folder) Every paper that was selected for inclusion will need to have a full text `ID.txt` file (where ID is the unique study id assigned to the paper) in the directory `full-texts/`.
  
**The CSV file containing the IDs and full-texts is the only input file required for the remaining phases of the review, the one we have called `master-text-list.csv` in our example.**  
  
To generate the batch job file for the categorization step, execute the `create-batch-cat.py` python script from the command line sending the master text list as input. To generate a batch job file, redirect the output to a jsonl file:  
  
`./create-batch-cat.py master-text-list.csv > batch-categorization.jsonl`  
  
Then upload the batch job to the OpenAI API using the `upload-batch-job-file.py` utility located in the `tools/` directory. If this script is in your local directory, run:  
  
`./upload-batch-job-file.py batch-categorization.jsonl`  
  
Make a note of the file ID for the batch file. Start the batch using the `do-batch.py` tool:  
  
`./do-batch.py <fileID>`  
  
Make a note of the batch ID.  
