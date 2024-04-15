print("beinning to import libraries...")
import pandas as pd
import transformers
import textwrap
from transformers import LlamaTokenizer, LlamaForCausalLM
import os
import sys
from typing import List

from peft import (
    LoraConfig,
    get_peft_model,
    get_peft_model_state_dict,
    prepare_model_for_int8_training,
)

# import fire
import torch
from datasets import load_dataset
import pandas as pd

# import matplotlib.pyplot as plt
# import matplotlib as mpl
# import seaborn as sns
# from pylab import rcParams
import json

# %matplotlib inline
# sns.set(rc={'figure.figsize':(8, 6)})
# sns.set(rc={'figure.dpi':100})
# sns.set(style='white', palette='muted', font_scale=1.2)

import sys
prompts = sys.argv
print(prompts)
if (len(prompts) < 4):
    print("insufficient number of parameters, must supply at least 3 parameters: location of base model, location of lora parameters, and at least one term to be normalized")
    exit

print("done importing libraries...")
print("loading model now...")

#prompt[0] will always be the name of the file. prompt[1] should be base model. prompt[2] should be checkpoint (fine-tuned) file. prompt[3] and onwards are the concepts to be normalized. 

BASE_MODEL = prompts[1]
lora_weights = prompts[2]

model = LlamaForCausalLM.from_pretrained(
            BASE_MODEL,
            load_in_8bit=False,
            torch_dtype=torch.float16,
            device_map = "auto"
        )

from peft import PeftModel
model = PeftModel.from_pretrained(
            model,
            lora_weights,
            torch_dtype=torch.float16,
        )

tokenizer = LlamaTokenizer.from_pretrained(BASE_MODEL)

model.config.pad_token_id = tokenizer.pad_token_id = 0  # unk
model.config.bos_token_id = 1
model.config.eos_token_id = 2

from transformers import GenerationConfig
generation_config = GenerationConfig(
            temperature=0.1,
            top_p=0.5,
            do_sample=True
#             top_k=40,
#             num_beams=4,
#             **kwargs,
#             bad_words_ids = [[2]]
        )

print("inputting and testing prompts now...")

for i in range(3, len(prompts)): #loop through list of concepts to be tested
    disease_name = prompts[i] #get disease name 
    print(f"processing concept: {disease_name}")


    prompt = f"""The Human Phenotype Ontology term {disease_name} is identified by the HPO ID HP:"""

    inputs = tokenizer(prompt, return_tensors="pt")
    input_ids = inputs["input_ids"].to('cuda')

    with torch.no_grad():
        generation_output = model.generate(
            input_ids=input_ids,
            generation_config=generation_config,
            return_dict_in_generate=True,
            output_scores=True,
            max_new_tokens=20,
        )
    #generation_output #generate answer 
    s = generation_output.sequences[0]
    output = tokenizer.decode(s) #decode into string 

    print(f"\nOutput:{output}")
                                                   

