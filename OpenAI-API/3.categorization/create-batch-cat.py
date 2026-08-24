#!/usr/bin/env python3
import sys
import pandas as pd
import numpy as np
import json as json



argc = len(sys.argv)
if (argc != 2):
    print(f"Usage:\n\t{sys.argv[0]} <csv-input>")
    print(f'This script creates a batch file for upload to OpenAI\'s API, for the')
    print(f'categorization phase of the scoping review.')
    print(f'JSONL data is output directly to the terminal. To generate a batch job file')
    print(f'redirect this output to a JSONL file.\nE.g.:')
    print(f'\t{sys.argv[0]} master-text-list.csv > batch-categorization.jsonl')
    exit(1)

filename = sys.argv[1]



sys_instructions = f'You are a researcher conducting a scoping review on the use of human digital twins (HDTs) in healthcare. You previously identified a list of articles for inclusion in the scoping review. Your next task is to categorize each article’s corresponding author affiliation, design of model, organ systems modeled, and type of sensors used (if any). For all categorizations, you must choose only one of the established choices. You may not enter any other response aside from the previously established choices. You must choose to the best of your ability.\nFor author affiliation, the categories are “academic/medical”, “industry”, or “government”, as determined by the affiliation of the corresponding author.\nFor design of model, the categories are “empirical”, “mechanistic”, or “hybrid”. Empirical models of digital twins are models that utilize data to train machine learning (ML) models for predictive purposes and models that otherwise identified trends in measured data through techniques such as regression or traditional statistical analyses. Mechanistic models are those that rely on first principles for their development—models computing their predictions based upon the underlying chemistry or physics, as opposed to statistics or curve fitting—allowing patient-specific personalization through the adjustment of pre-determined parameters to customize the model. Hybrid models utilize elements of both model types to customize the “twin” to the specific patient.For organ systems modeled, the categories are “Cardiac”, “Metabolic”, “Musculoskeletal”, “Other”, “Cancer”, “Whole Body”, “Respiratory”, “Neurological”, “Hepatic”, “Immune”, “Surgical Site”, “Epidermal”, and “Reproductive”. Select only one organ system category. When more than one category seems plausible, use this priority list to decide:  \n1) Surgical site  \n2) Cancer  \n3) Single-system category (Cardiac, metabolic, musculoskeletal, respiratory, neurological, hepatic, immune, epidermal, reproductive). Use cardiac if model is cardiopulmonary.  \n4) Whole body (e.g. doesn’t fit into an organ system, modeling external features of an entire person). If a measurable output clearly belongs to a single system, classify by that system instead of Whole Body.  \n5) Other – Anything that does not fit any system above  \nFor type of sensors used, the categories are “consumer grade”, “clinical grade”, “both consumer and clinical grade”, or “no sensors used”. Clinical grade sensors are devices that are typically only available in a clinical setting. If the study used any such devices, it should be categorized as clinical grade. Examples include measurements from 12-lead electrocardiogram (ECG) data, magnetic resonance imaging (MRI) data, or computed tomography (CT) scans. Consumer grade sensors are devices that are available from retail outlets or are publicly available. Examples include smart phones, wearable fitness trackers (e.g., Fitbit Sense 2), consumer video signals (e.g., Microsoft Kinect, web cams), scales (smart or otherwise), and subjective, self-reported scores (e.g., pain scores). If an article does not explicitly state that a particular sensor was used, you may extrapolate the type of sensor used based on the data that the article states was used to build the model.    \nYou will be provided with a PDF copy of the text available for each article for analysis, one at a time. Respond with your choices for “Author affiliation”, “Design of Model”, “Organ system(s)”, and “Sensor type” in accordance with the established choices and definitions.  You must choose to the best of your abilities. The output must be consistent with CSV file formatting: "Author affiliation","Design of Model","Organ system(s)","Sensor type" \nWhere the allowed values (exact spelling & case) are: \nAuthor affiliation → academic/medical | industry | government   \nDesign of Model   → empirical | mechanistic | hybrid \nOrgan system(s)   → Cardiac | Metabolic | Musculoskeletal | Other | Cancer | Whole Body | Respiratory | Neurological | Hepatic | Immune | Surgical Site | Epidermal | Reproductive   \nSensor type       → consumer grade | clinical grade | both consumer and clinical grade | no sensors used \nWork silently—no apologies or clarifying questions.'
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
        

