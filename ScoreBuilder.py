#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 11:35:22 2019

@author: danielbean
"""

# risk score builder

import pandas as pd
from py2neo import Graph
import urllib2, json


class MapperTemplate:
    """
    Base class for mappers. Mappers return identifers lower than or equal to
    the start id in whatever ontology they're using. 
    conf: dict containing connection information (host, port, user, pass)
    """
    def __init__(self, conf):
        self.conf = conf
        
    def get_descendants(self, start, depth):
        descendants = []
        return descendants
    
class TestMapper(MapperTemplate):
    """
    For testing of ScoreBuilder.
    If depth == 0, the root is passed through as the child value - convenient 
    for manually-defined components.
    """
    def get_descendants(self, start, depth):
        if depth == 0:
            return set([start])
        return ["%s_to_depth_%s" % (start, depth)]
    
    
class UMLSMapper(MapperTemplate):
    def __init__(self, conf):
        MapperTemplate.__init__(self, conf)
        # #connect to Neo4j server
        print "connect to Neo4j @ %s" % conf['host']
        self.g = Graph("bolt://" + conf['host'], password=conf['pass'])

    
    def get_descendants(self, start, depth=1):
        """
        Depth is implemented in the query for UMLS because an unrestricted depth has
        an enormous overhead in the UMLS graph, so only query as deep as we need
        """
        if depth == 0:
            return set([start])
        elif depth == -1:
            depth_str = "*"
        else:
            depth_str = "*.." + str(depth)
        
        query = """
        match p = (c:Concept {CUI:{cui}})<-[r:isa%s]-(cc:Concept)
        return c.CUI as root_cui, cc.CUI as child_cui,  length(p) as distance
        """ % depth_str
        data_dict = self.g.run(query, cui = start).data()
        df = pd.DataFrame(data_dict)
        id_list = set(df['child_cui'].tolist())
        id_list.add(start)
        return id_list
    
    ## old code below
    def recordsToList(self, cursor):
    	result = []
    	for record in cursor:
			result.append(record.values()[0])
    	return result
    
    def get_child_terms(self, umls):
        q = "match (c:Concept {CUI:'%s'})<-[r:isa*]-(cc:Concept) return cc.CUI as isa_child_term" % umls
        cursor = self.g.run(q)
        children = self.recordsToList(cursor)
        return children
    
class HPOMapper(MapperTemplate):
    def __init__(self, conf):
        MapperTemplate.__init__(self, conf)
        # #connect to Neo4j server
        print "connect to Neo4j @ %s" % conf['host']
        self.g = Graph("bolt://" + conf['host'], password=conf['pass'])
        
    def get_descendants(self, start, depth):
        if depth == 0:
            return set([start])
        terms = self.get_all_child_terms(start)
        if depth > 0: #-1 means unlimited and 0 means don't map
            terms = terms[terms['distance'] <= depth]
            
        id_list = set(terms['child_hpo'].tolist())
        id_list.add(start)
        return id_list

    def get_all_child_terms(self, hpo_id):
        
        query = """
        match p = (t:Term {hpo:{hpo_id}})<-[r:IS_A*]-(a)
        return t.hpo as root_hpo, t.name as root_name, a.hpo as child_hpo, a.name as child_name, length(p) as distance
        """
        data_dict = self.g.run(query, hpo_id = hpo_id).data()
        df = pd.DataFrame(data_dict)
        return df

class HPOUMLSMapper(MapperTemplate):
    """
    Like HPOMapper but only return child terms from HPO that have a UMLS equivalent
    """
    def __init__(self, conf):
        MapperTemplate.__init__(self, conf)
        # #connect to Neo4j server
        print "connect to Neo4j @ %s" % conf['host']
        self.g = Graph("bolt://" + conf['host'], password=conf['pass'])
        
    def get_descendants(self, start, depth):
        if depth == 0:
            return set([start])
        terms = self.get_all_child_terms(start)
        if depth > 0: #-1 means unlimited and 0 means don't map
            terms = terms[terms['distance'] <= depth]
        id_list = set(terms['umls'].tolist())
        #note for this mapper we DO NOT add the start id to the output
        #because it will be HPO and we want to return UMLS
        return id_list

    def get_all_child_terms(self, hpo_id):
        
        #note this query gives distances always +1 from distance in HPO because
        #it also includes the UMLS equivalent
        query = """
        match p = (t:Term {hpo:{hpo_id}})<-[r:IS_A*]-(a)-[rr:same]->(u:UMLS)
        return t.hpo as root_hpo, t.name as root_name, a.hpo as child_hpo, a.name as child_name, u.umls as umls, length(p) as distance
        """
        data_dict = self.g.run(query, hpo_id = hpo_id).data()
        df = pd.DataFrame(data_dict)
        has_child = df.shape[0] != 0
        
        if has_child:
            df['distance'] = df['distance'] - 1
        
        #another query to map the root to UMLS
        query = """
        match p = (t:Term {hpo:{hpo_id}})<-[rr:same]->(u:UMLS)
        return t.hpo as root_hpo, t.name as root_name, '' as child_hpo, '' as child_name, u.umls as umls, length(p) as distance
        """
        data_dict = self.g.run(query, hpo_id = hpo_id).data()
        df2 = pd.DataFrame(data_dict)
        df2['distance'] = df2['distance'] - 1
        if has_child:
            out = pd.concat([df, df2], ignore_index=True)
        else:
            out = df2
        return out

class ICD10_UMLSMapper(MapperTemplate):
    """
    Use the bioontology API to map ICD10 oto UMLS CUI. Note does not do any
    navigation of the ICD10 tree i.e. only supports depth==0
    """
    def __init__(self, conf):
        MapperTemplate.__init__(self, conf)
        # #connect to Neo4j server
        self.REST_URL = "http://data.bioontology.org/ontologies/ICD10/classes/http%3A%2F%2Fpurl.bioontology.org%2Fontology%2FICD10%2F"
        self.API_KEY = conf['key']
        
        #hacky fix for a missing term
        self.manual_terms = {}
        self.manual_terms['U80'] = {'cui':['C1269757'], 'prefLabel': 'Infection resistant to penicillin'}

    def get_descendants(self, start, depth):
        if depth != 0:
            print "ICD10_UMLS mapper does not support depth limited search"
            return
        res = self.get_json(self.REST_URL, start)
        cui = set(res['cui'])
        return cui
        
        
    def get_json(self, base_url, term):
        url = base_url + term
        opener = urllib2.build_opener()
        opener.addheaders = [('Authorization', 'apikey token=' + self.API_KEY)]
        try:
            op = opener.open(url)
            res = json.loads(op.read())
            res['mapping'] = 'bioportal'
        except:
            print "not found"
            if term in self.manual_terms:
                res = self.manual_terms[term]
                res['mapping'] = 'manual'
            else:
                res = {'cui': "", "prefLabel": "NOT FOUND", 'mapping': 'NONE'}
        return res
    
    

class ScoreBuilder:
    def __init__(self, name = ""):
        self.name = name
        self.mappers = {}
        
    def add_mapper(self, name, mapper):
        """
        name: value in the ontology column of the score configuration file that
        should trigger this mapper
        mapper: instance of a class inherited from MapperTemplate
        """
        self.mappers[name] = mapper
        
    def build(self, score_config_fname, exclusion_fname=None):
        """
        score_config_fname: definition of the component parts of this score as csv
        exclusion_fname: (optional) csv of concepts to exclude in the chosen ontology
        """
        df = pd.read_csv(score_config_fname)
        exclude = set()
        if exclusion_fname != None:
            exclude_def = pd.read_csv(exclusion_fname)
            exclude = set(exclude_def['id'].tolist())
        
        score_concepts = self.do_mapping(df, exclude)
        
        score_def = self.define_score(df, score_concepts)
        return score_def
    
    def do_mapping(self, df, exclude):
        by_source = df.groupby('ontology')
        rows = []
        for name, group in by_source:
            mapper = self.mappers[name]
            for index, row in group.iterrows():
                #get descendants
                r = mapper.get_descendants(row['root'], row['depth'])
                for ch in r:
                    if ch not in exclude:
                        rows.append({'child': ch, 'root': row['root'], 'component': row['component']})
        score_concepts = pd.DataFrame(rows)
        return score_concepts
    
    def define_score(self, score_config, score_concepts):
        definition = {}
        for name, group in score_config.groupby('component'):
            #print name
            definition[name] = {}
        
            this_concept = score_concepts[score_concepts['component'] == name]
            this_concept_umls = this_concept['child'].unique()
            this_concept_umls = list(this_concept_umls)
            this_concept_points = group['points'].unique()
            definition[name]['concepts'] = this_concept_umls
            if len(this_concept_points) > 1:
                print "different points values provided for group %s" % group
                print this_concept_points
                break
            definition[name]['points'] = this_concept_points[0]
            
        return definition
            
        

if __name__ == "__main__":
    import yaml
    with open('config.yml') as f:
        conf = yaml.load(f)
    sb = ScoreBuilder('test')
    tm = TestMapper({}) #empty configuration for test mapper
    sb.add_mapper('test', tm)
    definition = sb.build('input_files/test_definition.csv')
    print definition
    
    #HPO
    hpom = HPOMapper(conf['HPO'])
    sb.add_mapper('HPO', hpom)
    hpo_umls = HPOUMLSMapper(conf['HPO'])
    sb.add_mapper('HPO_UMLS', hpo_umls)
    #terms = hpom.get_descendants("HP:0001892", 1)
    definition = sb.build('input_files/hpo_test_definition.csv')
    print definition
    for comp in definition:
        print "%s: %s concepts" % (comp, len(definition[comp]['concepts']))
        
    #UMLS
    umls = UMLSMapper(conf['UMLS'])
    sb.add_mapper('UMLS', umls)
    definition = sb.build('input_files/umls_test_definition.csv')
    print definition
    for comp in definition:
        print "%s: %s concepts" % (comp, len(definition[comp]['concepts']))
        
    #ICD10
    icd = ICD10_UMLSMapper(conf['ICD10'])
    sb.add_mapper('ICD10_UMLS', icd)
    
    #icd.get_descendants('W19', 0)
    definition = sb.build('input_files/icd10_test_definition.csv')
    print definition
    for comp in definition:
        print "%s: %s concepts" % (comp, len(definition[comp]['concepts']))
    
    
    
    