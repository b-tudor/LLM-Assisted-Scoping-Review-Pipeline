The scripts `batchOut2csv_fulltxt-screen.py` and `synchOut2csv_fulltxt-screen.py` take the raw API output from the full text screening phase and convert it to CSV style data. Each of these scripts will put the CSV header row specidic to the full text screening phase at the top of the file, but what we want here is one large file with all the results and only a single CSV header row at top. As discussed before, all of these phase-specific output parsers are the same except for the fact that they put a CSV header row specific to the particular evaluation phase at the top of the file. You can always opt to use the generic `tools/batchOut2csv.py` or  `tools/synchOut2csv.py` which will do the exact same thing but without the header row.  
  
So in this case, where there is mixed output from batch runs and real-time synchronous runs (or some mixture of both), it is convenient to combine output files using a procedure like the following:
```
batchOut2csv_fulltxt-screen.py gpt5-batch-out_fulltxt-screen.jsonl > gpt5-fulltxt-results.csv
synchOut2csv.py gpt5-synch-out_fulltxt-screen.jsonl >> gpt5-fulltxt-results.csv
```

