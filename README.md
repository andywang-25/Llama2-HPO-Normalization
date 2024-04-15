# LLaMA2-Fine-tuning
Fine-tuning LLaMA 2 for rare disease concept normalization

## Abstract
Clinical concept extraction and normalization from clinical narratives remain a significant challenge in rare disease research. We fine-tuned LLaMA 2, an open-source large language model (LLM) developed by Meta, using a domain-specific corpus for rare disease concept normalization. The fine-tuned model recognizes diverse sentence contexts and normalizes several types of concepts, including Human Phenotype Ontology (HPO), Online Mendelian Inheritance in Man (OMIM), and Orphanet. The HPO model (50 epochs) achieved an accuracy of 99.55% in identifying a term’s HPO ID when prompted with the original training sentences. Similarly, the OMIM and Orphanet model (30 epochs) achieved an accuracy of 98.03%. Our models exhibit robustness to minor types, can efficiently handle inputs it was not trained on, and significantly outperformed ChatGPT in a benchmark test for clinical concept normalization. Our results suggest that domain-specific LLMs enable accurate and generalizable clinical concept normalization. 

## Instruction




## Case study


![image](https://github.com/andywang-25/Llama2-HPO-Normalization/assets/112890888/3a28109e-5c54-4a37-b7a5-0a9b3ab77d16)

Below is the description of clinical phenotypes

```
Additionally, rough facial features were noted with a flat nasal bridge, a synophrys (unibrow), a long and smooth philtrum, thick lips and an enlarged mouth. He also had rib edge eversion, and it was also discovered that he was profoundly deaf and had completely lost the ability to speak. He also had loss of bladder control. The diagnosis of severe intellectual disability was made, based on Wechsler Intelligence Scale examination. Brain MRI demonstrated cortical atrophy with enlargement of the subarachnoid spaces and ventricular dilatation (Figure 2). Brainstem evoked potentials showed moderate abnormalities. Electroencephalography (EEG) showed abnormal sleep EEG.
```



## Reference

Wang A, Yang J, Liu C, Weng C. Fine-tuning Large Language Models for Rare Disease Concept Normalization. bioRxiv 2023.12.28.573586; doi: https://doi.org/10.1101/2023.12.28.573586
