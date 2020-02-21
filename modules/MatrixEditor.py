#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from py_pickle_handlers import *
from MatrixCreator import RelationalMatrix

matrix = read_pickle('fup_2014-2019.matrix', '.')

matrix.show_matriculas()


