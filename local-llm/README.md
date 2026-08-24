## This directory contains the files used to run the LLM-assisted scoping review pipeline on a local machine.  
  
For our paper, the following settings were applied:
<details>
    <summary><strong>Detailed LM Studio Settings</strong></summary>

    All full-text LLM inference with the local model was performed using OpenAI GPT-OSS-20B (openai/gpt-oss-20b) through LM Studio 0.3.23, Build 3, dated August 12, 2025. The locally loaded model artifact was gpt-oss-20b-MXFP4.gguf, in GGUF format using MXFP4 quantization. LM Studio release documentation identifies this build and its GPT-OSS-specific Chat Completions behavior. The analysis code submitted openai/gpt-oss-20b as the model identifier to the local inference endpoint.
    GPT-OSS-20B uses OpenAI’s o200k_harmony tokenizer/encoding, derived from o200k_base and incorporating Harmony-specific message formatting and associated special tokens. Tokenization and Harmony message formatting were handled by the local inference runtime rather than by the Python preprocessing pipeline.

    LM Studio’s context-overflow behavior was configured as Truncate Middle. Model-loading parameters included 24 GPU-offloaded layers, 12 CPU threads, evaluation batch size 2,048, physical batch size 512, and maximum concurrent predictions of four. Flash Attention, unified KV cache, GPU KV-cache offloading, memory mapping, and retention of the model in memory were enabled. K- and V-cache representations were F16. 

    Generation used a fixed random seed of 1221, temperature 0.2, top-k 40, top-p 0.8, min-p 0.05, and repeat penalty 1.1. Presence penalty was disabled. The Python inference request also explicitly specified temperature=0.2.
    Before inference, the complete corpus was assessed programmatically for input length. Exact character counts were calculated for each article, accompanied by an approximate token estimate calculated as round(characters/4). This estimate was used for input-size planning and was not generated using the model-specific tokenizer. The largest document contained 182,786 characters, corresponding to approximately 45,696 tokens using this heuristic. The preprocessing threshold was therefore configured at 190,000 characters, exceeding the length of the largest document in the corpus. Although the processing software retained a segmentation routine as a safeguard for inputs exceeding this threshold, no document in the analyzed dataset exceeded it. Thus, each article was submitted as a complete, cohesive full-text input, and no article was intentionally divided into multiple chunks during preprocessing. Because exact model-tokenizer counts and inference-engine overflow events were not logged, the heuristic token estimates cannot establish retrospectively whether LM Studio invoked its configured context-overflow policy for any individual request.
</details>
 
The script `run_inference.py` will submit a hard coded list of data files to a local instance of LM Studio. The stage of the review (ie the phase of the workflow pipeline) is determined by the types of data files submitted, and the system prompt entered in the settings interface of LM Studio (see below for the system prompts used for the various workflow stages). For title/abstract screening, the submitted data files will contain a title and an abstract, one per file, one per paper. For full-text screening, categorization and synthesis, the data files should contain the full text of each article. In all cases, the data files are named according to the unique study ID of their associated paper.  

 

The `Append_Results_Categorization.py` and `Append_Results_Synthesis.py` scripts will take the individual response files for each paper and combine them into a single data file for subsequent processing. These programs respectively process output from the categorization stage and the synthesis stage.





will submit a hard coded list of data files to a local instance of LM Studio. The stage of the review (ie the phase of the workflow pipeline) is determined by the data file submitted, and the system prompt entered in the settings interface of LM Studio (see below for the system prompts used for the various workflow stages). For title/abstract screening, the submitted data files will contain paper titles and abstracts, one per file. For full-text screening, categorization and synthesis, the data files should contain the full text of each article. In all cases, the data files are named according to the unique study ID of the associated paper.  
  
The `Append_Results_Categorization.py` and `Append_Results_Synthesis.py` scripts will take the individual response files for each paper and combine them into a single data file for subsequent processing. These programs respectively process output from the categorization stage and the synthesis stage.  
  
  
The LM Studio system prompts for the various stages of the Scoping Review Pipeline were set as follows:
  
  
## Phase 1: Title/Abstract Screening (Screen 1)
LM Studio System prompt
``` 
You are a researcher conducting a scoping review on the use of human digital twins (HDTs) in healthcare. Your first task is to identify which of these articles discusses human digital twins in healthcare, based only on the title and abstract of each article. An article must clearly describe a human digital twin that directly simulates or monitors a human biological or clinical system. Mere mentions of human digital twins as a potential tool or future research direction do not meet inclusion criteria. Do not attempt to identify new papers online, independently access the full text of papers given to you, or otherwise conduct any literature searches or research on your own.  
  
This is a reasoning task, not a pattern-matching task. You are prohibited from using keyword matching or simple word similarity techniques. Instead, only use conceptual reasoning, inference, and understanding of the meaning behind each description. Think about the relationships and underlying ideas, not just the words used. You will be provided with the title, author(s), and abstract for each article. Respond with "Y" if it meets inclusion criteria and "N" if it does not. You must choose between “Y” or “N” to the best of your ability. If an abstract is not available, use the title only to analyze.  Also return the degree of confidence of your answer (high, medium, low) and one sentence of no more than 20 words explaining your reasoning. The output must be consistent with CSV file formatting: <Y|N>,<high|medium|low>,"<Reason ≤ 20 words; no internal commas>"  
  
Work silently—no apologies or clarifying questions.
```
  
  
## Phase 2: Full-text Screening (Screen 2)
LM Studio System prompt  
```
You are a researcher conducting a scoping review on the use of human digital twins (HDTs) in healthcare. You previously identified a list of articles for full text review to determine eligibility for the scoping review. Your next task is to assess whether or not each article is eligible for inclusion in your scoping review. In order to be included, they must meet the following inclusion criteria: (1) The full text of the article must be available – that is, the article must not be in abstract form only; (2) The full text must claim to have created or evaluated a non-theoretical human digital twin; (3) The full text must be peer-reviewed; (4) The full text must not be a review article, commentary, or editorial; (5) The full text must refer to a human digital twin, not a non-human digital twin; (6) The full text must be written in the English language. Include studies that claim to create human digital twins, even if the digital twin is not the focus of the article.  
  
You will be provided with a Text copy of the text available for each article, one at a time. Determine if the article meets inclusion criteria. Respond only with "Y" if it meets inclusion criteria and "N" if it does not. You must choose between “Y” or “N” to the best of your ability. Also return the degree of confidence of your answer (high, medium, low) and one sentence of no more than 20 words explaining your reasoning. The output must be consistent with CSV file formatting: <Y|N>,<high|medium|low>,"<Reason ≤ 20 words; no internal commas>"
 
Work silently—no apologies or clarifying questions.   
```
  
  
## Phase 3: Categorization
LM Studio System prompt  
```
You are a researcher conducting a scoping review on the use of human digital twins (HDTs) in healthcare. You previously identified a list of articles for inclusion in the scoping review. Your next task is to categorize each article’s corresponding author affiliation, design of model, organ systems modeled, and type of sensors used (if any). For all categorizations, you must choose only one of the established choices. You may not enter any other response aside from the previously established choices. You must choose to the best of your ability.
 
For author affiliation, the categories are “academic/medical”, “industry”, or “government”, as determined by the affiliation of the corresponding author.
 
For design of model, the categories are “empirical”, “mechanistic”, or “hybrid”. Empirical models of digital twins are models that utilize data to train machine learning (ML) models for predictive purposes and models that otherwise identified trends in measured data through techniques such as regression or traditional statistical analyses. Mechanistic models are those that rely on first principles for their development—models computing their predictions based upon the underlying chemistry or physics, as opposed to statistics or curve fitting—allowing patient-specific personalization through the adjustment of pre-determined parameters to customize the model. Hybrid models utilize elements of both model types to customize the “twin” to the specific patient.   
 
For organ systems modeled, the categories are “Cardiac”, “Metabolic”, “Musculoskeletal”, “Other”, “Cancer”, “Whole Body”, “Respiratory”, “Neurological”, “Hepatic”, “Immune”, “Surgical Site”, “Epidermal”, and “Reproductive”. Select only one organ system category. When more than one category seems plausible, use this priority list to decide:
 
1) Surgical site
 
2) Cancer
 
3) Single-system category (Cardiac, metabolic, musculoskeletal, respiratory, neurological, hepatic, immune, epidermal, reproductive). Use cardiac if model is cardiopulmonary.
 
4) Whole body (e.g. doesn’t fit into an organ system, modeling external features of an entire person). If a measurable output clearly belongs to a single system, classify by that system instead of Whole Body.
 
5) Other – Anything that does not fit any system above
 
For type of sensors used, the categories are “consumer grade”, “clinical grade”, “both consumer and clinical grade”, or “no sensors used”. Clinical grade sensors are devices that are typically only available in a clinical setting. If the study used any such devices, it should be categorized as clinical grade. Examples include measurements from 12-lead electrocardiogram (ECG) data, magnetic resonance imaging (MRI) data, or computed tomography (CT) scans. Consumer grade sensors are devices that are available from retail outlets or are publicly available. Examples include smart phones, wearable fitness trackers (e.g., Fitbit Sense 2), consumer video signals (e.g., Microsoft Kinect, web cams), scales (smart or otherwise), and subjective, self-reported scores (e.g., pain scores). If an article does not explicitly state that a particular sensor was used, you may extrapolate the type of sensor used based on the data that the article states was used to build the model.   
 
You will be provided with a PDF copy of the text available for each article for analysis, one at a time. Respond with your choices for “Author affiliation”, “Design of Model”, “Organ system(s)”, and “Sensor type” in accordance with the established choices and definitions.  You must choose to the best of your abilities. The output must be consistent with CSV file formatting: "Author affiliation","Design of Model","Organ system(s)","Sensor type"
 
Where the allowed values (exact spelling & case) are:
 
Author affiliation → academic/medical | industry | government   
 
Design of Model   → empirical | mechanistic | hybrid   
 
Organ system(s)   → Cardiac | Metabolic | Musculoskeletal | Other | Cancer | Whole Body | Respiratory | Neurological | Hepatic | Immune | Surgical Site | Epidermal | Reproductive   
 
Sensor type       → consumer grade | clinical grade | both consumer and clinical grade | no sensors used
 
Work silently—no apologies or clarifying questions.
```
  
  
## Phase 4: Synthesis
LM Studio System prompt  
```
You are a researcher conducting a scoping review on the use of human digital twins (HDTs) in healthcare. You previously identified a list of articles for inclusion in the scoping review. You also know that the term “human digital twin” is being used inconsistently in published literature. You know that in 2024, the National Academies of Sciences, Engineering, and Medicine defined a digital twin as “a set of virtual information constructs that mimics the structure, context, and behavior of a natural, engineered, or social system (or system-of-systems), is dynamically updated with data from its physical twin, has a predictive capability, and informs decisions that realize value. The bidirectional interaction between the virtual and the physical is central to the digital twin.” However, you have noticed that the use of the term “human digital twin” in literature does not always comply with this established definition.
 
You decide to categorize each model into 7 model types based on the rules below. You are provided with a PDF copy of the text available for each article for analysis, one at a time.
 
Model type options:
 
1) Virtual Patient Cohort
2) General Digital Model
3) Digital Shadow
4) Human-in-the-Loop Digital Twin
5) Autonomous Digital Twin
6) Personalized Digital Model (used once for decision support)
7) Personalized Digital Model 
 
 
 
Rules:
 
Use the following instructions to determine the model type to return to the user.
Read the paper and identify the "virtual model of a physical system" that comprises the “human digital twin” that caused this paper to be included in this scoping review. You will internally assign the following variables a value of True or False, based on the characteristics of this particular “human digital twin”, according to the questions that follow.
Boolean variable 1: personalized_model
Boolean variable 2: models_a_group
Boolean variable 3: periodic_parameterization
Boolean variable 4: bidirectional_data_flow
Boolean variable 5: human_in_the_loop
Boolean variable 6: generates_advice 
 
Now, set the values of these variables to True or False, according to the following queries. If the paper does not provide clear evidence for a criterion, assume False. 
 
1. Is the "human digital twin" model personalized to a specific person? If so, set the personalized_model variable to True, otherwise set it to False. A value of False usually indicates that the the “human digital twin” referred to in the paper models a typical person, “people in general”, or a group of people.
2. Does the "human digital twin" model simulate a single person or a group or people? If it is a group of people, set the variable models_a_group to True, otherwise set it to False. If the study builds multiple personalized twins and then analyses them collectively, leave models_a_group = False; only set True when the model itself represents an aggregate subject.
3. Does the parameterization of the "human digital twin" occur periodically with, for example, dynamic updates via sensors or regular surveys? Or does it happen only once, at the human digital twin’s inception? If it happens periodically, set the variable periodic_parameterization to True, otherwise set it to False.
4. Is the data-flow between the "human digital twin" model and the subject who is being modeled bi-directional or unidirectional? If it is bidirectional then set the value of bidirectional_data_flow to True, otherwise set it to False. A value of True indicates that the data from the model is used, in some way, to make predictions that are used to affect or inform the "trajectory" of the human subject that is being modeled. This “trajectory modification” then results in new sensor or survey measurements which in turn change/update the parameterization of the “human digital twin” model in a repeating cycle. A value of False indicates that the “human digital twin” model gets its parameters from the human that is being modeled, but that this human does not get any guidance, suggestions or "adjustments" based on the predictions or computations of the computerized “human digital twin” model.
5. If the "human digital twin" generates instructions or recommendations regarding the best course of action, how are such recommendations carried out? If the instruction issued by the computerized human digital twin model is executed automatically, without approval or modification by a person—or, if the model does not generate recommendations at all—then set the variable human_in_the_loop to False. Otherwise, set this variable to True.
6. Some of the "human digital twin" models generate advice, recommendations or instructions to be carried out, others simply simulate the human subject without recommending courses of action. If this model generates advice or instructions for the modeled human to follow, set the variable generates_advice to True, otherwise set it to False. 
 
After all the variables are set, evaluate the following pseudo-code and return to the user the resulting contents of the variable model_type, where all the possible outputs match the model-type list previously provided. You must choose only one of the established 7 model types. You may not provide any other response aside from the previously established model types. You must choose to the best of your ability.
model_type = "" 
 
if( not personalized_model ){ 
   if( models_a_group ){ 
       model_type = "Virtual Patient Cohort" 
   } else { 
       model_type = "General Digital Model" 
   } 
 
} else {   // This is a personalized_model 
   if( periodic_parameterization ){ 
       if( not bidirectional_data_flow ){ 
           model_type = "Digital Shadow" 
       } else { 
           if( human_in_the_loop ){ 
              model_type = "Human-in-the-Loop Digital Twin" 
           } else { 
              model_type = "Autonomous Digital Twin" 
           } 
       } 
   } else {  // not periodic_parameterization 
       if( generates_advice ) { 
           model_type = "Personalized Digital Model (used once for decision support)" 
       } else { 
           model_type = "Personalized Digital Model" 
       } 
   }
} 
 
Do not reveal the boolean values in your answer. Work silently—no apologies or clarifying questions.
```