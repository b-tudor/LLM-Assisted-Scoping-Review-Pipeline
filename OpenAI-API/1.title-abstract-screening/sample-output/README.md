To get the CSV formatted title + abstract screening results that are used in the next phase, run something like  
  
`batchOut2csv-TitleAbScreen.py gpt5-batch-out_title-abs-screen.jsonl > gpt5-title-abstract-screen-results.csv`  
  
 Recall that using the tailored `batchOut2csv-TitleAbScreen.py` parser will output columnn headers for the CSV file. If you need the output without the headers (e.g. when appending one output file onto another), use the generic parser, `tools/batchOut2csv.py`. 