#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 16:39:39 2019

@author: danielbean
"""

import pandas as pd

class Scorer(object):
    """Apply generated risk score definitions to NLP output
    
    score_definition: json definition of score to calculate
    
    """
    def __init__(self, score_definition):
        # super(Scorer, self).__init__()
        self.score_definition = score_definition 


    def score(self, df, identifiers):
        """
        df: pandas dataframe with patients as rows and concepts as columns. 
            Values are processed as truthy
        identifiers: list of columns to be copied across to output table so 
            results can be joined.
            
        returns: dict of scores (dataframe, component points and total) and 
            errors (dict, concepts relevant to the score that were not detected 
            for any patients).
        
        """
        ### map umls codes from score definition to ctx concepts from semEHR
        score_df = pd.DataFrame()
        points_df = pd.DataFrame()
        
        seen_ctx = set(df.columns) #concepts detected for at least one patient
        concept_not_found = {}
        for s in self.score_definition:
           
            #extract relevant columns from df
            component_ctx = set(self.score_definition[s]['concepts'])
            seen_component_ctx = list(component_ctx.intersection(seen_ctx))
            component = df[seen_component_ctx]
            score_df[s] = component.any(axis=1)
            points_df[s] = score_df[s] * self.score_definition[s]['points']
            
            #track missing concepts
            concept_not_found[s] = component_ctx.difference(seen_ctx)

        total_score = points_df.sum(axis=1)
        points_df['total'] = total_score
        #copy across specified identifiers
        for idf in identifiers:
            points_df[idf] = df[idf]
        return {'scores' : points_df, 'not_found' : concept_not_found}
    


class AggregateScorer(object):
    """Apply generated risk score definitions to NLP output already mapped to parent concept level
    
    score_definition: json definition of score to calculate
    
    """
    def __init__(self, score_definition):
        # super(Scorer, self).__init__()
        self.score_definition = score_definition 


    def score(self, df, identifiers):
        """
        df: pandas dataframe with patients as rows and parent concepts as columns. 
            Values are processed as truthy
        identifiers: list of columns to be copied across to output table so 
            results can be joined.
            
        returns: dict of scores (dataframe, component points and total) and 
            errors (dict, concepts relevant to the score that were not detected 
            for any patients).
        
        """
        ### map umls codes from score definition to ctx concepts from semEHR
        score_df = pd.DataFrame()
        points_df = pd.DataFrame()
        
        seen_ctx = set(df.columns) #concepts detected for at least one patient
        concept_not_found = {}
        for s in self.score_definition:
           
            #extract relevant columns from df
            component = df[s]
            score_df[s] = component.astype(bool)
            points_df[s] = score_df[s] * self.score_definition[s]['points']
            
            #track missing concepts
            concept_not_found[s] = df[s].sum(axis=0) ==0

        total_score = points_df.sum(axis=1)
        points_df['total'] = total_score
        #copy across specified identifiers
        for idf in identifiers:
            points_df[idf] = df[idf]
        return {'scores' : points_df, 'not_found' : concept_not_found}