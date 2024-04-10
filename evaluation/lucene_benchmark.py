# Last updated: 04-09-2024
# whoosh is a python lucene implementation.
from whoosh import scoring
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.analysis import StemmingAnalyzer
from whoosh.index import open_dir
from whoosh.qparser import QueryParser, OrGroup, AndGroup
from tqdm import tqdm
import os
import json
import pandas as pd
import re

def load_hp_synonyms(hp_json = '../hp.json'):
    '''
    load hpo from json
    '''
    hpo_json = json.load(open(hp_json))
    synonym_dict_list = []
    nodes = hpo_json['graphs'][0]['nodes']
    for node in nodes:
        # "id" : "http://purl.obolibrary.org/obo/HP_0000016"
        try:
            id_component_list = node['id'].split('/')
            if 'HP_' in id_component_list[-1]:
                synonym_dict = {}
                synonym_dict['hp_id'] = id_component_list[-1]
                synonym_dict['name'] = node['lbl']
                synonym_dict['synonyms'] = [node['lbl']]
                if 'meta' in node:
                    if 'synonyms' in node['meta']:
                        synonyms = node['meta']['synonyms']
                        for synonym in synonyms:
                            synonym_dict['synonyms'].append(synonym['val'])
                synonym_dict_list.append(synonym_dict)
        except Exception as e:
            print(e)
            pass
    return synonym_dict_list

def create_positive_control_json(synonym_dict_list, output_json = 'positive_control.json'):
    '''
    create a positive control to monitor the accuracy
    '''
    positive_control = []
    for e in synonym_dict_list:
        # change _ to : in hp_id
        hp_id = e['hp_id'].replace('_', ':')
        positive_control.append({'input': f'The Human Phenotype Ontology term {e["name"]} is identified by the HPO ID', 'output': hp_id})
    json.dump(positive_control[:1000], open(output_json,'w'), indent=2)
    return 0

def create_index(index_dir, synonym_dict_list):
    '''
    Create an index and schema
    '''
    stem_ana = StemmingAnalyzer() # use stem analyzer to normalize word
    custom_schema = Schema(hp_id=ID(stored=True),
                hp_desc=TEXT(stored=True, analyzer=stem_ana),
    )
    # create if not exist
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)
    else:
        # delete forecely and recreate
        import shutil
        shutil.rmtree(index_dir)
        os.mkdir(index_dir)
    index = create_in(index_dir, custom_schema)

    # Open the index
    index = open_dir(index_dir)

    # Create a writer to add documents to the index
    writer = index.writer()

    # Add documents to the index
    for i in tqdm(range(len(synonym_dict_list))):
        phrase = synonym_dict_list[i]
        synonyms = phrase['synonyms']
        # synonyms.extend([phrase['name']])
        for synonym in synonyms:
            writer.add_document(hp_id=str(phrase['hp_id']),
                                hp_desc=synonym
                                )
    writer.commit()
    return 0

def jaccard_index(term1, term2):
    '''calculate j-index for two terms
        Examples: 
        "Hello world Jude" and "Hey world" will return 1/4 = 0.25;
        "Hey Jude" and "Hey world" will return 1/2 = 0.5
        "Hey World" and "Hey world" will return 2/2 = 1
    '''
    set1 = set(term1.lower().split())
    set2 = set(term2.lower().split())
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0

def query_single_term(index_dir, query_name, top_k):
    '''
    query a term and get best matched hp_id
    '''
    index = open_dir(index_dir)
    # Use OrGroup instead. if AndGroup is used, very few hits will be returned.
    query_parser = QueryParser('hp_desc', schema=index.schema, group=OrGroup)
    searcher = index.searcher(weighting=scoring.BM25F(B=10, K1=0.1))
    query = query_parser.parse('{}'.format(query_name))
    # calculate # of match first 
    # without score, it can be very fast, o/w, it will be very slow.
    results = searcher.search(query,limit=10,scored=False)
    length_of_matched_hits = len(results)
    if length_of_matched_hits > 100:
        # if too many hits, return top_k (in a random order) and use j-index to find best matches
        results = searcher.search(query, limit=top_k, scored=False)
        j_index = 0
        output = ''
        if len(results) > 0:
            results = results[:top_k]
            for i, result in enumerate(results):
                output_update = result['hp_id']
                output_term = result['hp_desc']
                j_index_update = jaccard_index(query_name, output_term)
                output = output_update if j_index_update > j_index else output
                j_index = j_index_update if j_index_update > j_index else j_index
        else:
            output = ''
    else:
        # if less than 100 hits, return all and use BM25 score to find best matches
        results = searcher.search(query,scored=True)
        if len(results) > 0:
            result = results[:1] # best match
            output = result[0]['hp_id']
        else:
            output = ''    
    searcher.close()
    return output

def evaluation_lucene(input_json, output_json):
    '''
    calculate lucene based query accuracy rate
    '''
    # Convert to DataFrame
    df_true = pd.DataFrame(input_json)
    # rename output as true_hp
    df_true.rename(columns={'output': 'true_hp'}, inplace=True)
    df_test = pd.DataFrame(output_json)
    df_test.rename(columns={'output': 'test_hp'}, inplace=True)
    # replace ":" as "-" in the output
    df_test['test_hp'] = df_test['test_hp'].apply(lambda x: re.sub('_', ':', x))
    compare_df = df_true.merge(df_test, on='input',how='left').fillna('')
    compare_df['accurate'] = compare_df.apply(lambda x: 1 if x['true_hp'] == x['test_hp'] else 0, axis=1)
    # calculate accuracy rate
    accuracy_rate = compare_df['accurate'].sum() / len(compare_df)
    return accuracy_rate


def remove_numbers_and_decimal(input_string):
    # Use regular expression to remove all numbers and decimal points
    return re.sub(r'[\d\.]+', '', input_string)

def execute_pipeline(input_json, output_json):
    '''
    pipeline for lucene benchmark
    '''
    # In general, the performance will increase as top_k increased.
    # however, the speed can be extremely slow (possible due to python lucene implementatio) if top_k is too large.
    top_k = 1000
    input_json_list = json.load(open(input_json,'r'))
    lucene_list = []
    for e in tqdm(input_json_list):
        input = e['input']
        m = re.match('The Human Phenotype Ontology term (.+?) is identified by the HPO ID', input)
        term = m.group(1)
        # in complex typo. From index 10900 to 11000, there are some terms with numbers and decimal points.
        # remove numbers and decimal points, which can cause lucene stucked.
        term = remove_numbers_and_decimal(term)
        if term == 'Pinhole visualbacuityc LogMAR':
            # Unknown bug. But lucene stucked with this term.
            # Also very strange, it works well on the server (ubuntu 20.04) but not on my local machine (MacOS 13.0)
            output = ''
        else:
            output = query_single_term(index_dir,term, top_k)
        lucene_list.append({'input': input, 'output': output})
       
    json.dump(lucene_list, open(output_json,'w'), indent=2)
    acc = evaluation_lucene(input_json_list, lucene_list)
    print(f'accuracy of {input_json} is: {acc}')
    return 0     

# create index.
synonym_dict_list = load_hp_synonyms()
index_dir = './hpo_index'
create_index(index_dir, synonym_dict_list)
create_positive_control_json(synonym_dict_list)
# execute_pipeline('./positive_control.json', 'positive_control_lucene.json')
# execute_pipeline('./gpt_test.json', 'gpt_test_lucene.json')
# execute_pipeline('./typo_part6.json', 'single_typo_lucene.json')
execute_pipeline('./complextypo_part6.json', 'complex_typo_lucene.json')
# execute_pipeline('./snomed_comparison.json', 'snomed_comparison_lucene.json')

