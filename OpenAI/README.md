These are the files used to run the pipeline using OpenAI's API.
The model we used in our paper was GPT-5. 

Generally, the instructions for running a batch job are as follows:




##Step 1: Load the API key into the OPENAI_API_KEY environment variable:

	source export-key.sh


**NOTE**:    You do need to enter your OpenAI API key into the script first. 

**NOTE**:    This is intended for a Linux Bash shell, please adjust accordingly.

**WARNING**: Do not use this script if you are not on a trusted computer, 
         where you can't, say, leave your secret API key sitting unencrypted
         in a random text file.


  
##Step 2: Make a batch file. This is a .jsonl file with your requests. Example (indentation not present on actual file):

	{"custom_id": "request-1", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-5", "messages": [{"role": "system", "content": "You are a helpful assistant."},{"role": "user", "content": "Hello world!"}],"max_completion_tokens": 1000}}
	{"custom_id": "request-2", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-5", "messages": [{"role": "system", "content": "You are an unhelpful assistant."},{"role": "user", "content": "Hello world!"}],"max_completion_tokens": 1000}}

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
			{"role": "system", "content": "You are a helpful assistant that answers in pirate slang."}
			This sets the context and persona for all subsequent completions.

			User message:
			{"role": "user", "content": "How do I bake a cake?"}
			This is like typing into ChatGPT’s input box.

			assistant message:
			{"role": "assistant", "content": "Here’s a simple recipe for baking a cake..."}

		If you want the model to keep continuity over multiple turns, you include past assistant messages too.


##Step 3: Upload the file to OpenAI. Use the script upload-batch.py

	./upload-batch-job-file.py <filename-of-your-.jsonl-file>

	This loads the file onto the OpenAI server so that it can be referenced by the other things that you do. It also marks the purpose as "batch" which allows you to run it like a batch job. (Not sure if this is required or not)
	This script will return a file ID. You need this to send to the batch runner script. 
	If you did not copy/paste it somewhere, you can see what files you have on the server by running:

		./list-file-IDs.py



##Step 4: Run the batch file

	./do-batch.py <file-ID>

	If you copied the fileID from the previous step onto the clipboard, you can just paste it onto the end of this command. THIS command will return a batch id. You will need this ID to check on the status of the batch job and to retrieve results, etc.
	If you did not write down or copy/paste the batch ID somewhere, you can find a list of the batches that have been submitted recently (last 24 hours, I think) by running:
		./recent-batches.py

	If you like, you can edit the job_desc variable at the top of the do_batch.py file to attached a description string to the job (maybe useful if you are sending a bunch of unrelated batch jobs to OpenAI)



BATCH1:
batch_689d6509dbb8819085a05fd71aea0a14

BATCH 2:
batch_689d6548f1108190aaf997a958605074



