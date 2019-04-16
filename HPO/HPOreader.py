#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 16:32:40 2018

@author: danielbean
"""

from edges import Directed

#read all terms into a basic dict structure
#key is HP:nnn...
#Each term is a dict, all values are lists
#some of the values in the lists are themselves key:value pairs e.g. xref

class HPOreader:
    def __init__(self):
        self.terms = {}
        self.missing = set()
        
    def parse(self, path, return_graph = True, verbose = False):
        """
        Parse HPO .obo files to a directed graph. 
        path = path to .obo file
        return_graph = whether to return the directed graph (default: True) or
        save it as self.rels (False).
        verbose = print parsing errors (default false (off))
        """
        rels = Directed()
        with open(path) as f:
            term_active = False
            term_data = {}
            line_num = 0
            term_id = "NOT_SET"
            for line in f:
                line_num += 1
                line = line.replace('\n', '')
                if line == '[Term]':
                    term_active = True
                    continue
                if line == '':
                    if term_data != {}:
                        self.terms[term_id] = term_data
                    term_data = {}
                    term_active = False
                    term_id = "NOT_SET"
                if term_active:
                    line_data = line.split(': ')
                    if len(line_data) > 2:
                        if verbose == True:                         
                            print 'too many fields in line %s:' % line_num
                            print line
                        pos = line.find(': ')
                        key = line[:pos]
                        value = line[(pos+2):]
                    key = line_data[0]
                    value = line_data[1]
                    if key not in term_data:
                        term_data[key] = []
                    term_data[key].append(value)
                    
                    if key == 'id':
                        term_id = value
        print "Loaded %s nodes" % len(self.terms)

        #build relationship edges
        
        for term in self.terms:
            if 'is_a' in self.terms[term]:
                for target in self.terms[term]['is_a']:
                    tgt_name = target.split(' ! ')[0]
                    if tgt_name not in self.terms:
                        self.missing.add(tgt_name)
                    else:
                        rels.add(term, tgt_name)
        print "Loaded %s edges" % rels.count()
        if verbose == True:
            print "%s nodes missing" % len(self.missing)
        
        if return_graph == True:
             return rels
        else:
             self.rels = rels
        
    def get_umls(self):
        for term in self.terms:
            self.terms[term]['xref_umls'] = []
            if 'xref' in self.terms[term]:
                xref_umls = [x.split(':')[1] for x in self.terms[term]['xref'] if x.startswith('UMLS:')]
                if len(xref_umls) != 0:
                    self.terms[term]['xref_umls'] = xref_umls
        
if __name__ == "__main__":
    reader = HPOreader()
    reader.parse('hp.sample.obo.txt')