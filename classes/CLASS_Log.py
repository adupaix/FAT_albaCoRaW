#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon, 20 Jun 2022 15:30:43 GMT

Definition de la classe Log

@author: adupaix
"""

def del_after_pattern(string, pattern):
        """
        Method to keep only the part of a string before a given pattern
        """
        return string[0:string.find(pattern)]


class Log:
    """
    Class to save a log of the execution
    """
    
    def __init__(self, path, fname, seed, nreplica, environment):
        """
        Initialize an object of Log class
        
        Store 
        - the path to the cfg file
        - the name of the cfg file
        - the full name of the cfg file
        - the seed number
        """
        self.path = path
        self.fname = fname
        
        self.full_name = self.path+"/"+self.fname
        
        self.seed = seed
        self.nreplica = nreplica
        self.env = environment
        
        self.t = time.localtime()
        self.ti = time.time()
        
    
    def fill(self):
        """
        Fill in the log from the cfg file
        """
        
        self.arg_lines = list()
        with open(self.full_name, 'r') as file:
            for line in file:
                if re.search("=", line):
                    self.arg_lines.append(line)
                    
        self.arg_lines = [x for x in self.arg_lines if not x.startswith('#')]
        
        for i in range(len(self.arg_lines)):
            if re.search("#", self.arg_lines[i]):
                self.arg_lines[i] = del_after_pattern(self.arg_lines[i], " #")+"\n"
            
        
    def save(self, path_output):
        """
        Save the log
        """
        
        lines = ["Timestamp : "+str(time.strftime('%a, %d %b %Y %H:%M:%S GMT', self.t)),
                 "\nRunning time (in s): "+str(round(time.time()-self.ti)),
                 "\n--------------",
                 "\n",
                 "\nNumber of simulated tunas : "+str(self.nreplica),
                 "\nEnvironment type : "+str(self.env),
                 "\nSeed : "+str(self.seed),
                 "\n\n\nArguments :",
                 "\n------------\n"]
        lines.extend(self.arg_lines)
        
        summary = open(str(path_output)+"/Summary.txt", "w")
        summary.writelines(lines)
        summary.close()
        
    
    def __repr__(self):
        """Methode pour afficher l objet
        """
        return "Log object\n\n cfg file: {}\n Seed number: {}".format(self.full_name, self.seed)
        
        