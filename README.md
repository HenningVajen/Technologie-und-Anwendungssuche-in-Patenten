# Technology and Use-Case Search in Patents
The "Technology and Application Search in Patents" is a tool designed to facilitate searching for technologies and their applications within patent data. It offers the flexibility to conduct searches in both directions, enabling users to explore technologies and their potential uses in various domains.

## Motivation
The primary motivation behind developing this tool is to provide domain experts with a creativity technique for their research. Patent searches can be challenging, especially for inexperienced users, due to the specialized vocabulary and deliberate obfuscation techniques used in patent documents, which often hinder the retrieval of relevant and accurate results. This tool aims to simplify the process and improve the search experience for all users.
To generate relevant synonyms three different models are used and the results are combined
- FastText
- WordNet
- JoBimText

## Features
### Pre-Processing of Patent Data
Before conducting searches, the tool performs pre-processing of large volumes of textual patent data. This involves several essential steps:
- Indexing: The tool organizes the patent data into easily searchable indices
- NLP Methods: Natural Language Processing (NLP) techniques are applied to enhance the understanding of patent text and improve search accuracy.

### Search
The tool supports two different search approaches, each serving a distinct purpose:
1) **Use-Case Search** The two search types differ in their search path and output. For the search for applications, the tool presents the frequencies of patent classes and applicants to make groups visible.
2) **Technology Search** For the search for technical solutions, the search is additionally performed for all combinations of subsets of terms. The usually extensive results of this overlap search are then clearly presented in the form of a matrix. The procedure aims at finding as many matching technologies as possible.


## Repository and overview
```
├── Backend.py
├── Datenvorbereitung.py <= add new documents to existing index or create new indices
├── Frontend.py <=to be executed with Streamlit
├── Import_CPCFiles.py <=needed only once to create a dictionary of CPC class descriptions
├── config.py <=specify parameters like process flow though pre-processing, names of indices, folders and files
├── input <=folder to place input date like .json with textual patent date; can be changed in config.py
├── model_data <=folder to models and dictionaries; CPC-Dictionary, FastText Vector files, Patent-Metadata dictionary; can be changed in config.py
│   └── CPCDict.pkl
├── output <=output of the data pre-processing; created dictionary will be placed here; can be changed in config.py
├── requirements.txt
├── until_index_dict_parts.py <=this and following files contain functions to be called of other parts, esp. from the backend
├── utility_Datenbearbeitung.py
├── utility_Index_und_Suche.py
├── utility_NLP_Bearbeitung.py
└── utility_Query.py
``` 

## Installing
Install necessary python packages
`python3 -m pip install -r requirements.txt`

Copy the resources in the corresponding folders stated in config.py-
Necessary ressources in default configuration are
- CPCDict.pkl (Dictionary of CPC Class descriptions)
- patent-100.bin (Binary of the FastText Model)
- woerterbuch_metadaten.pkl (Dictionary of metadata of all indexed patents)
- Indexes on Elasticsearch Server

See the following steps to create eventually missing resources.

### Download of textual patent data 
The input for the pre-processing are json-lines files as they can exported form the Google Patents Public Dataset.
The files must contain the following fields:

|Field Name |  Data Type  | Description |
 |---------- |  ---------- | ------------|
publication_number |	STRING |	Patent publication number (DOCDB compatible), eg: 'US-7650331-B1' 
title_localized |	RECORD |	The publication titles in different languages 
abstract_localized |	RECORD |	The publication abstracts in different languages 
claims_localized |	RECORD |	For US publications only, the claims in plain text 
description_lo calized |	RECORD |	For US publications only, the description in plain text, limited to the first 9 megabytes 
publication_da te |	INTEGER |	The publication date. 
assignee |	STRING |	The assignees/applicants. 
cpc |	RECORD |	The Cooperative Patent Classification (CPC) codes. 

### Pre-Processing

If not done, download and install Elasticsearch, see links section.

1. Start of Elasticsearch Server
navigate to the installation folder and run the application, e.g.:

`/Library/elasticsearch-8.5.0/bin/elasticsearch`

2. Settings and place files
Check config.py for the correct name of indices to be used
Check Datenvorbereitung for the run mode (lines 25 to 29)
Place files in foldes, see section repository

3. Run skript "Datenvorbereitung.py"
`python3 Datenvorbereitung.py`

## Using the tool / search
1. Start of Elasticsearch Server
navigate to the installation folder and run the application, e.g.:

`/Library/elasticsearch-8.5.0/bin/elasticsearch`

2. Optional: Check of used indices in Kibana
navigate to the installation folder and run the application, e.g.:

`/Library/kibana-8.5.0/bin/kibana `

Run in browser
http://localhost:5601

Abfrage aller Indizes in Kibana Console
GET /_cat/indices

3. Start of Frontend
`streamlit run Frontend.py`

Run in browser
http://localhost:8501


## Links

- Google Big Query "Google Patents Public Dataset"
https://console.cloud.google.com/marketplace/product/google_patents_public_datasets/google-patents-public-data

-Elasticsearch
https://www.elastic.co/de/downloads/elasticsearch
Version 8.5.0

-Kibana
https://www.elastic.co/de/downloads/kibana
Version 8.5.0
