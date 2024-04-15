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

