# General API Workflow Instructions 
## (And general noob guidance for interacting with the OpenAI API)

The `OpenAI-API/` directory contains the files used to manage the scoping review workflow using OpenAI's API.
  
The general workflow is to:  
1. Generate a jsonl file, where each line is an individual request to the API.  
2. Upload the file to OpenAI as batch job.  
3. Run the batch.  
4. Check for completion/errors.  
5. Download output or error logs.  
  
There is an limit to how many tokens you can have enqueued for jobs in the batch system which varies by user access-tier (among other factors). If you have large jobs, you will need to create batch files with fewer jobs. If you have jobs that by themselves exceed the enqueued token limit, collect these jobs into a separate file and submit them to the synchronous pathway (see below). Alternately, you can submit all jobs to the synchronous API, but I *think* at the time it was slower and cost more--ymmv.  The batch file error logs will let you know if a batch failed due to the batch having exceeded the enqueued token limit.  
  
There are several utilities here for turning raw data or the output from a previous pipeline stage into a batch job for a downstream pipeline stage.  
```
title-abstract-screening ---------> -----+-----> full-text-screening ----+--> categorization
                                         |                               | 
               full text files >---------+                               +--> synthesis
```
Once you've generated a batch input jsonl file, it is uploaded to the API. You can use the tool `tool/upload-batch-job-file.py` for this.  
  
Then, submit the file as a batch job and enqueue it for execution. This can be done with the tool `tool/do-batch.py`  
  
Finally, output or errors can be retrieved using:  
```
tools/get-output.py
tools/display-error-file.py
tools/check-batch-status.py
```  
  
**NOTE:** You may find that a job is too large to submit via the batch system. In that case, put these jsonl request lines in a file of their own and submit them to the synchronous API using the script `tools/real-time-job-runner.py`. The output from these files will be ever-so-slightly different, but nevertheless they will need to be parsed differently. **In this archive the batch output is generally referred to as type A while the synchronous jobs are referred to as type B.** So parsers like typeA2csv.py will convert batch output to a CSV file, and so on. You get  the picture.  





## i. Load the API key into the OPENAI_API_KEY environment variable:

	source export-key.sh


**NOTE**:    You do need to enter your OpenAI API key into the script first. 

**NOTE**:    This is intended for a Linux/MacOS Bash shell, please adjust accordingly.

**WARNING**: Do not use this script if you are not on a trusted computer, 
         where you can't, say, leave your secret API key sitting unencrypted
         in a random text file.


  
## ii. Make a batch file
This is a .jsonl file where each line is an independent request/job to the API. Example:  
```
{"custom_id": "request-1", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-5", "messages": [{"role": "system", "content": "You are a helpful assistant."},{"role": "user", "content": "Help me write Hello world! in Python"}]}}
{"custom_id": "request-2", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-5", "messages": [{"role": "system", "content": "You are an unhelpful assistant."},{"role": "user", "content": "Help me write Hello world! in C++"}]}}
```

Here, each line is a separate request.  

In the OpenAI chat completions format, body.messages is essentially the conversation history you send to the model, and each object has:  
role → who is "speaking" in that turn  
content → what that "speaker" says  
  
The possible role values are:  
  
Role        Meaning  
"system"    Special instructions to set behavior, tone, or constraints for the model. Think of this as meta-guidance about how the assistant should respond, not part of the user’s conversation.  
"user"      Input from the human user (the actual prompt or question).  
"assistant" A prior response from the model (used when sending conversation history for continuity).  
"tool"      (optional / advanced) Used when the model is interacting with a tool call in the newer API designs (Assistants API, function calling).  
  
How They’re Used in Practice    
System message:  
`{"role": "system", "content": "You are a helpful assistant that answers in pirate slang."}`  
This sets the context and persona for all subsequent completions.  
  
User message:    
`{"role": "user", "content": "How do I bake a cake?"}`   
This is like typing into ChatGPT’s input box.  
  
assistant message:   
`{"role": "assistant", "content": "Here’s a simple recipe for baking a cake..."}`   
  
If you want the model to keep continuity over multiple turns, you include past assistant messages too.   
  
  
## iii. Upload the file to OpenAI
  
`./upload-batch-job-file.py <filename-of-your-jsonl-file>`  

This loads the file onto the OpenAI server so that it can be referenced by the other things that you do. It also marks the purpose as "batch" which allows you to run it like a batch job (not sure if this is required or not). This script will return a file ID. You need this to send to the batch runner script. If you did not copy/paste it somewhere, you can see what files you have on the server by running:  
  
`./list-file-IDs.py`  
  
  
  
## iv. Run the batch file
  
`./do-batch.py <file-ID>`

If you copied the fileID from the previous step onto the clipboard, you can just paste it onto the end of this command. THIS command will return a batch id. You will need this ID to check on the status of the batch job and to retrieve results, etc.  
  
If you did not write down or copy/paste the batch ID somewhere, you can find a list of the batches that have been submitted recently (last 24 hours, I think) by running:  
`./recent-batches.py`  
  
If you like, you can edit the job_desc variable at the top of the do_batch.py file to attached a description string to the job (maybe useful if you are sending a bunch of unrelated batch jobs).  
  
Batch IDs should look something like:    
```
batch_689d6509dbb8819085a05fd71aea0a14  
batch_689d6548f1108190aaf997a958605074
```


