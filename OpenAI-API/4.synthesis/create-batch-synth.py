#!/usr/bin/env python
import sys
import pandas as pd
import numpy as np
import json as json



argc = len(sys.argv)
if (argc != 2):
    print(f"Usage:\n\t{sys.argv[0]} <input.csv>\n")
    print(f"This code generates a batch file for upload to OpenAI's API.")
    print(f'JSONL data is output to terminal. To generate a batch job file,')
    print(f'redirect this output to a JSONL file.\nE.g.:')
    print(f'\t{sys.argv[0]} master-text-list.csv > batch-synth.jsonl\n')
    exit(1)

filename = sys.argv[1]



sys_instructions = 'You are a researcher conducting a scoping review on the use of human digital twins (HDTs) in healthcare. You previously identified a list of articles for inclusion in the scoping review. You also know that the term “human digital twin” is being used inconsistently in published literature. You know that in 2024, the National Academies of Sciences, Engineering, and Medicine defined a digital twin as “a set of virtual information constructs that mimics the structure, context, and behavior of a natural, engineered, or social system (or system-of-systems), is dynamically updated with data from its physical twin, has a predictive capability, and informs decisions that realize value. The bidirectional interaction between the virtual and the physical is central to the digital twin.” However, you have noticed that the use of the term “human digital twin” in literature does not always comply with this established definition.  \nYou decide to categorize each model into 7 model types based on the rules below. You are provided with a PDF copy of the text available for each article for analysis, one at a time.  \nModel type options: \n\n1) Virtual Patient Cohort \n2) General Digital Model \n3) Digital Shadow \n4) Human-in-the-Loop Digital Twin \n5) Autonomous Digital Twin \n6) Personalized Digital Model (used once for decision support) \n7) Personalized Digital Model \n\nRules:  \nUse the following instructions to determine the model type to return to the user. \nRead the paper and identify the "virtual model of a physical system" that comprises the “human digital twin” that caused this paper to be included in this scoping review. You will internally assign the following variables a value of True or False, based on the characteristics of this particular “human digital twin”, according to the questions that follow.  \nBoolean variable 1: personalized_model \nBoolean variable 2: models_a_group \nBoolean variable 3: periodic_parameterization \nBoolean variable 4: bidirectional_data_flow \nBoolean variable 5: human_in_the_loop \nBoolean variable 6: generates_advice \n\nNow, set the values of these variables to True or False, according to the following queries. If the paper does not provide clear evidence for a criterion, assume False. \n\n1. Is the "human digital twin" model personalized to a specific person? If so, set the personalized_model variable to True, otherwise set it to False. A value of False usually indicates that the the “human digital twin” referred to in the paper models a typical person, “people in general”, or a group of people. \n2. Does the "human digital twin" model simulate a single person or a group or people? If it is a group of people, set the variable models_a_group to True, otherwise set it to False. If the study builds multiple personalized twins and then analyses them collectively, leave models_a_group = False; only set True when the model itself represents an aggregate subject. \n3. Does the parameterization of the "human digital twin" occur periodically with, for example, dynamic updates via sensors or regular surveys? Or does it happen only once, at the human digital twin’s inception? If it happens periodically, set the variable periodic_parameterization to True, otherwise set it to False. \n4. Is the data-flow between the "human digital twin" model and the subject who is being modeled bi-directional or unidirectional? If it is bidirectional then set the value of bidirectional_data_flow to True, otherwise set it to False. A value of True indicates that the data from the model is used, in some way, to make predictions that are used to affect or inform the "trajectory" of the human subject that is being modeled. This “trajectory modification” then results in new sensor or survey measurements which in turn change/update the parameterization of the “human digital twin” model in a repeating cycle. A value of False indicates that the “human digital twin” model gets its parameters from the human that is being modeled, but that this human does not get any guidance, suggestions or "adjustments" based on the predictions or computations of the computerized “human digital twin” model. \n5. If the "human digital twin" generates instructions or recommendations regarding the best course of action, how are such recommendations carried out? If the instruction issued by the computerized human digital twin model is executed automatically, without approval or modification by a person—or, if the model does not generate recommendations at all—then set the variable human_in_the_loop to False. Otherwise, set this variable to True. \n6. Some of the "human digital twin" models generate advice, recommendations or instructions to be carried out, others simply simulate the human subject without recommending courses of action. If this model generates advice or instructions for the modeled human to follow, set the variable generates_advice to True, otherwise set it to False. \n\nbAfter all the variables are set, evaluate the following pseudo-code and return to the user the resulting contents of the variable model_type, where all the possible outputs match the model-type list previously provided. You must choose only one of the established 7 model types. You may not provide any other response aside from the previously established model types. You must choose to the best of your ability.\n\nmodel_type = "" \n\nif( not personalized_model ){ \n    if( models_a_group ){ \n        model_type = "Virtual Patient Cohort" \n    } else { \n        model_type = "General Digital Model" \n    } \n} else {   // This is a personalized_model \n    if( periodic_parameterization ){ \n        if( not bidirectional_data_flow ){  \n            model_type = "Digital Shadow" \n        } else { \n            if( human_in_the_loop ){ \n                model_type = "Human-in-the-Loop Digital Twin" \n            } else { \n                model_type = "Autonomous Digital Twin" \n            } \n        } \n    } else {  // not periodic_parameterization \n        if( generates_advice ) { \n            model_type = "Personalized Digital Model (used once for decision support)" \n        } else { \n            model_type = "Personalized Digital Model" \n        } \n    } \n}\n\nDo not reveal the boolean values in your answer. Work silently—no apologies or clarifying questions.'
sys_instructions = json.dumps(sys_instructions)

# Load the CSV file
N=0
df = pd.read_csv(filename)

for id, text in zip(df['id'], df['text']):

    ID = int(id)
    customID = f'{(ID):04d}'

    query = f'Evaluate this document according to your instructions:\\n\\n{text}'
    json_string =f'{{"custom_id": "{customID}", "method": "POST", "url": "/v1/responses", "body": {{"model": "gpt-5", "input": [{{"role": "system", "content": "{sys_instructions[1:-1]}"}},{{"role": "user", "content": "{query}"}}], "reasoning":{{"effort":"high"}},"text":{{"format":{{"type": "text"}}}}, "store":false}}}}'
    print(f'{json_string}')
        

