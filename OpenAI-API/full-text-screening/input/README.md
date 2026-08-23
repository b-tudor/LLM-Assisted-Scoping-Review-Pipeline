These files must exist in the directory:

`complete-title-abstract-list_input.csv`

A csv file with the columbs 'Title', 'Abstract', and 'id', where 'id' is the unique study id for this paper.


`gpt5-title-abstract-screen-results.csv`

A csv file made from the LLM output of the previous step (gpt5, in our case). This CSV has the columns 'id', 'include', 'confidence', and 'reasoning'. 'id' is the unique study id for this study. 'include' is either a 'Y' or an 'N' and is the LLM's determination whether the study was to be included or not, based on the title and abstract alone. 

`full-texts/ID.txt`

There must be a text file in this folder for each study marked as a 'Y' in the title/abstract screening results. Here ID (as in ID.txt) is the unique study id for this paper. eg. The text of study 42 should be named `42.txt`.

Redirect this output to the batch file for upload to the OpenAI API.
Eg:

`./create-fulltext-screen-batch.py > batchJob-sample_full-text-screen.jsonl`
