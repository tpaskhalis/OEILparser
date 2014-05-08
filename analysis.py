import numpy as np
import pandas as pd
import nltk

metadata = pd.read_csv('OEIL/all_info.csv', skiprows = 1, names = range(33))
inlinfo = metadata[metadata[0].str.endswith('(INL)')]
inlinfo.to_csv('OEIL/inl_info.csv', index = False)

###############################################################################

inl = pd.read_table('OEIL/text/INL_2007-2238.tsv', names = ['num', 'par'], sep = '\t')
lpar = inl['par'].tolist()
