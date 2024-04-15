# Llama2-Fine-tuning
Fine-tuning Llama2 for rare disease concept normalization

## Abstract
Clinical concept extraction and normalization from clinical narratives remain a significant challenge in rare disease research. We fine-tuned LLaMA 2, an open-source large language model (LLM) developed by Meta, using a domain-specific corpus for rare disease concept normalization. We used the Human Phenotype Ontology (HPO) as the data source, in which the model is fine-tuned to recognize concepts and synonyms from the HPO vocabulary. Our fine-tuned models demonstrate the ability to normalize phenotype terms unseen in the fine-tuning corpus, including misspellings, synonyms, terms from other ontologies, and laymen's terms. Our approach provides a solution for the use of LLM to identify named medical entities from the clinical narratives while successfully normalizing them to standard concepts in a controlled vocabulary.

## Instruction

Below is a brief summary of how to set up the Llama2 environment. The Juypter Notebook file contains more detailed instructions. 

```
conda create --name llama python=3.10
conda activate llama
pip install git+https://github.com/huggingface/transformers.git
pip install git+https://github.com/huggingface/peft.git
pip install git+https://github.com/huggingface/accelerate.git
pip install -q trl
pip install -U datasets
pip install -U bitsandbytes
pip install -U einops
pip install -U wandb
pip install --user ipykernel
python -m ipykernel install --user --name=llama
```

After executing the segment above, you can open Jupyter Notebook and select the "llama" kernel to run the notebook. 

Within the Jupyter Notebook, users can use the fine-tuned model by inputting the template prompt: "The Human Phenotype Ontology term [concept name] is identified by the HPO ID HP: ." For example, to normalize the term "Aneurysm," the input would be: "The Human Phenotype Ontology term Vascular Dilatation is identified by the HPO ID HP: ."

If you do not want to use Jupyter Notebook, you can use the "inference_HPO.py" script, which can be executed in the command line. An example is shown below: 
> python inference_HPO.py base_model_directory lora_parameters_directory "hearing loss" "hearing impairment"
The command line script requires three parameters at minimum:
1. The directory of the Llama2 base model (can be downloaded from Meta: https://llama.meta.com/llama-downloads)
2. The directory of the fine-tuned LoRA model (can be downloaded here: https://github.com/andywang-25/Llama2-HPO-Normalization/releases/tag/v0.0.2)
3. At least one term to be normalized into its HPO identifier 

Example output: 
> Output:\<s\> The Human Phenotype Ontology term hearing loss is identified by the HPO ID HP:0000365\</s\>

> Output:\<s\> The Human Phenotype Ontology term hearing impairment is identified by the HPO ID HP:0000365\</s\>

## Case study


![image](https://github.com/andywang-25/Llama2-HPO-Normalization/assets/112890888/3a28109e-5c54-4a37-b7a5-0a9b3ab77d16)

Below is the description of clinical phenotypes:

> Additionally, rough facial features were noted with a flat nasal bridge, a synophrys (unibrow), a long and smooth philtrum, thick lips and an enlarged mouth. He also had rib edge eversion, and it was also discovered that he was profoundly deaf and had completely lost the ability to speak. He also had loss of bladder control. The diagnosis of severe intellectual disability was made, based on Wechsler Intelligence Scale examination. Brain MRI demonstrated cortical atrophy with enlargement of the subarachnoid spaces and ventricular dilatation (Figure 2). Brainstem evoked potentials showed moderate abnormalities. Electroencephalography (EEG) showed abnormal sleep EEG.

Some clinical phenotypes are extracted from the description above and then normalized using our fine-tuned model. The extracted terms are all synonyms of HPO terms but do not necessarily exist within the database. Our fine-tuned model standardizes these terms into their respective HPO identifiers. For example, "flattened philtrum" is converted into HP:0000319, corresponding to "Smooth philtrum." Concept normalization facilitates phenotype-based disease diagnosis programs, allowing for better patient outcomes in a more timely manner. 
 

## Reference

Wang A, Yang J, Liu C, Weng C. Fine-tuning Large Language Models for Rare Disease Concept Normalization. bioRxiv 2023.12.28.573586; doi: https://doi.org/10.1101/2023.12.28.573586

Shi L, Li B, Huang Y, Ling X, Liu T, Lyon GJ, Xu A, Wang K. "Genotype-first" approaches on a curious case of idiopathic progressive cognitive decline. BMC Med Genomics. 2014 Dec 3;7:66. doi: 10.1186/s12920-014-0066-9. PMID: 25466957; PMCID: PMC4267425.
