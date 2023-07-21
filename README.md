# Technology and Use-Case Search in Patents
The "Technology and Application Search in Patents" is a tool designed to facilitate searching for technologies and their applications within patent data. It offers the flexibility to conduct searches in both directions, enabling users to explore technologies and their potential uses in various domains.

## Motivation
The primary motivation behind developing this tool is to provide domain experts with a creativity technique for their research. Patent searches can be challenging, especially for inexperienced users, due to the specialized vocabulary and deliberate obfuscation techniques used in patent documents, which often hinder the retrieval of relevant and accurate results. This tool aims to simplify the process and improve the search experience for all users.

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

**HIER WEITER SCHREIBEN**

```
├── Backend.py
├── Datenvorbereitung.py (BESCHREIBUNG....)
├── Frontend.py
├── Import_CPCFiles.py
├── config.py
├── input
├── model_data
│   └── CPCDict.pkl
├── output
│   ├── woerterbuch_metadaten_G01L.pkl
│   ├── woerterbuch_metadaten_G01L_100.pkl
│   └── woerterbuch_metadaten_random_full.pkl
├── requirements.txt
├── until_index_dict_parts.py
├── utility_Datenbearbeitung.py
├── utility_Index_und_Suche.py
├── utility_NLP_Bearbeitung.py
└── utility_Query.py
``` 


## Installing / Using
Install necessary python packages
`python3 -m pip install -r requirements.txt`

Copy the ressources in the corresponing folders stated in config.py


### Download of textual patent data 

Datenformat json lines, wie dem dem export aus "Google Patents Public Dataset" entspricht

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


### Search

## More ressources
- Link zur Masterarbeit
- Link zu Google Big Query "Google Patents Public Dataset"
- Links zu Download-Qullen für Modell, die verwendet werden
