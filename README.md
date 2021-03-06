# Risk score builder
A pipeline to generate definitions of clinical risk scores as UMLS CUIs. A score definition can have a combination of manual and automatic components.

This risk scoring and prescribing trend analysis pipeline was developed and used in Bean et al. (2019 submitted) "Semantic Computational Analysis of Anticoagulation Use in Atrial Fibrillation from Real World Data".

# Overview
The Objective is to end up with both patient record data and clinical risk score definitions described using the same common set of identifiers for concepts, e.g. HPO, UMLS, SNOMED, ICD. With that we can apply the score definition to patient data and calculate clinical risk scores automatically. In many cases there are many (10s, 100s) of different possible identifiers for a given clinical concept relevant to a risk score. The main point of this code is to automate collecting those different identifiers automatically, converting a human-readable definition of clinical risk into a machine-readable one.

This library starts from the point where you have those concepts for clinical data, it does not handle doing the annotation.

# Usage
## Create input files describing the risk score
There are 3 inputs to prepare:
1. manual definition file - these are high-level concepts that will be mapped to all descendent terms in the ontology
2. manual exclusion list (optional)
3. the ontology you want to use accessible e.g. locally or via a public API

### 1. Manual definition file
A csv file with these headings:

component |	name (optional) |	root |	ontology |	depth |	points | sty filter (optional) |	notes (optional)
------------ | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | -------------
Name of the component of the risk score that this row relates to | name in the ontology | parent node identifier in the ontology | which mapper to use | number of levels of  child nodes to return | points assigned in the risk score | for UMLS, the semantic types to include (note that since this requires UMLS source files, filtering by sty is currently disabled) | any notes

For depth, -1 = unlimited, 0 = don't map (pass through root id), >0 = map to depth (inclusive). Depth = 0 is useful for concepts you add manually on top of NLP features, for example "Age 65-74" which has no ontology concept. The example scripts to calculate risk scores demonstrate using this to use the feature "Age 65-74" which has no ontology concept but is defined in the input and passed through.

### 2. Manual exclusion list
A csv file with these headings:

name (optional) | id
------------- | -------------
Name of the concept | identifier in the ontology you're using

### 3. The ontology
You need the ontology/ontologies you're using for the NLP and score definitions somewhere and a mapper class (subclass of MapperTemplate) that can use the ontology to go from a root node to all child nodes at a given depth. Most current mappers work with neo4j databases or the bioontology API. There is also an HPO mapper HPOLocalMapper that parses the HPO.obo file into a graph in memory, so it can run locally with no external dependencies.

Create a config.yaml file with the connection information for any ontologies you're using in the format of config.example.yaml.

The ontologies are needed to generate the score definitions but not to calculate the scores or do any other downstream analysis. Examples working with definition files that are already generated will work without the ontology.

## Generate score definition
The intended use is to combine these generated definitions with some NLP results for clinical data to calculate risk scores. This code is only for the creation of the score definition, not the use of the definition.

The ScoreBuilder class in ScoreBuilder.py handles the generation of score definitions from the manual input files. The bulk of the work is done by the mapper classes e.g. UMLSMapper, HPOMapper. ScoreBuilder uses the input definition file to dispatch the necessary mapper to find child concepts. Most mappers implemented so far work with an ontology stored in Neo4j. Due to UMLS licensing, the files needed to generate the Neo4j database cannot be distributed here. The HPOLocalMapper and HPO/hpo_2019-04-15.obo.txt are included so the full pipeline can run locally for a demo definition file (input_files/hpo_demo_definition.csv).

## Apply score to patient data
The exact details of calculating scores will depend on the NLP process used to associate ontology concepts with patients. In Bean et al. (2019) we use SemEHR for NLP and aggregate document-level concept annotations to patient-level - each patient is represented by the sum of annotation counts across all of their documents. Per patient, any concept with <2 annotations is ignored.

Frailty, CHADS-VASc and HAS-BLED definitions are provided with input data (generated data NOT patient data) and code to calculate scores in the examples directory and described below.

# Examples
## Full demo for HPO
The script hpo_demo.py runs the entire pipeline locally, using the HPO.obo file to build the HPO ontology in memory as a graph. In this script we parse HPO, use it to map our definition file to a full list of concepts, then apply the score definition to some generated "patient" data. 

## Generate risk score
Run build_risk_scores.py to generate definitions for chads-vasc, has-bled and HFRS using a combination of UMLS, HPO and ICD10 ontologies, as well as concepts we manually define for gender and age range. The resulting definition is in UMLS CUI.

Note in this example we generate data at the level of CUI, but in Bean et al. the context for the concept (from SemEHR) is used. The process is identical to this example except that to use context there is an additional mapping step from CUI to the set of CUI+context identifiers from SemEHR. The definition files from Bean et al. 2019 as CUI are in the bean2019 folder.

## Calculate risk score
Run examples/calculate_risk_score.py to apply the generated definitions from build_risk_scores.py to some generated example data.

## Plot prescribing trend
Plot prescribing patterns over time and stratified by risk score. The example_data folder contains prescribing data in a convenient format generated using examples/generate_prescribing_data.py (i.e. it has the same structure as the data used in Bean et al. but it is NOT real patient data).

To generate the plots, run examples/prescribing_trend.py

# Frailty risk score
Hospital frailty risk score as defined in Gilbert et al. (2018) "Development and validation of a Hospital Frailty Risk Score focusing on older people in acute care settings using electronic hospital records: an observational study", The Lancet, VOLUME 391, ISSUE 10132, P1775-1782, MAY 05, 2018
https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(18)30668-8/fulltext
DOI:https://doi.org/10.1016/S0140-6736(18)30668-8

# Dependencies
Building the CH2DS2-VASc, HAS-BLED and HFRS scores defined in /input_files (as used in Bean et al.) needs UMLS and HPO graphs available in neo4j.

# UMLS
Use of UMLS is subject to license terms and as such it cannot be distributed here.

#HPO
The Human Phenotype Ontology is available here https://hpo.jax.org/app/ and described in the paper:
Sebastian Köhler, Leigh Carmody, Nicole Vasilevsky, Julius O B Jacobsen, et al. Expansion of the Human Phenotype Ontology (HPO) knowledge base and resources. Nucleic Acids Research. (2018) doi: 10.1093/nar/gky1105


# Bioontology
You need to register and API key for bioontology to use their API for ICD10 mapping (used for frailty score)


# Funding
Dan Bean is funded by Health Data Research UK

# Contact
Developed by Dan Bean at King's College London - daniel.bean@kcl.ac.uk
