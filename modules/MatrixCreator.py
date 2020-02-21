#!/usr/bin/env python
# coding: utf-8

import numpy as np
import codecs
import itertools
import asyncio
from py_pickle_handlers import *


with codecs.open('out.txt', "r", encoding="cp1252") as f:
    f_data = f.readlines()


estudantes3 = []
for line in f_data:
    estudantes3.append(eval(line.strip()))

class UniqueIdt():
    def __init__(self, lista_de_individuos):
        def check_tuple(tuple_obj, reference_to_id_dict):
            has_id = False
            for element in tuple_obj:
                if reference_to_id_dict.get(element):
                    has_id = True
                    return has_id
            return has_id

        
        def create_reference_index(tuple_obj, unique_id, reference_to_id_dict):
            for element in tuple_obj:
                reference_to_id_dict[element] = unique_id
            return reference_to_id_dict

                
        def insert_in_unique_id_dict(tuple_obj, unique_id, unique_id_dict):
            for element in tuple_obj:
                if unique_id_dict.get(unique_id):
                    unique_id_dict[unique_id].append(element)
                else:
                    unique_id_dict[unique_id] = [element]
            return unique_id_dict
        
        self.unique_hash = {}
        self.referencia = {}
        
        if not type(lista_de_individuos[0]) == tuple:
            for individuo in lista_de_individuos:
                if not self.referencia.get(individuo):
                    unique_id = "unq%s" % str(len(self.unique_hash)).zfill(7)
                    self.referencia[individuo] = unique_id
                    self.unique_hash[unique_id] = [individuo]
        else:
            
            for tuple_obj in lista_de_individuos:
                if not check_tuple(tuple_obj, self.referencia):
                    unique_id = "unq%s" % str(len(self.unique_hash)).zfill(7)
                    self.referencia = create_reference_index(tuple_obj, unique_id, self.referencia)
                    self.unique_hash = insert_in_unique_id_dict(tuple_obj, unique_id, self.unique_hash)
            
    def get_unique_id_matrix_idx(self, unique_id):
        return int(unique_id.replace('unq',''))
    
    def get_unique_id_from_int(self, integer):
        return "unq%s" % str(integer).zfill(7)
    
    def change_ref(self, old_reference_value, new_reference_value):
        if self.referencia.get(old_reference_value):
            unique_id = self.referencia.get(old_reference_value)
            self.referencia[new_reference_value] = unique_id
            self.unique_hash[unique_id].append(new_reference_value)
        
        else:
            print("Usuário ainda não cadastrado. Utilizar '.add_ref(usuario)' para adiciona-lo...")
            return None
            
    def add_ref(self, new_reference_value):
        if self.referencia.get(new_reference_value):
            print("Usuário já cadastrado. Abortando...")
            return None
        
        else:
            self.referencia[individuo] = unique_id
            self.unique_hash[unique_id] = [individuo]

    def get_refs(self, idt):
        if self.referencia.get(idt):
            return self.referencia[idt]
        
        elif self.unique_hash.get(idt):
            return self.unique_hash[idt]
        
        else:
            print('Identificador não encontrado...')
            return False
        
    def get_unique_id(self, idt):
        if self.unique_hash.get(idt):
            print("O argumento fornecido '%s' já é um 'unique_id' registrado..." % idt)
            return False
        
        elif self.referencia.get(idt):
            return self.referencia[idt]
        
        else:
            print('Identificador não encontrado...')
            return False
        
    def get_unique_id_list(self):
        return list(sorted(self.unique_hash.keys()))
            


class RelationalMatrix():
    def __init__(self, lista_de_individuos):
        self.referencia = UniqueIdt(lista_de_individuos)
        self.matrix = np.zeros((len(lista_de_individuos), len(lista_de_individuos)),dtype='uint8')
        self.get_diagonal = range(0,len(lista_de_individuos))
        self.pow2_matrix = None
        self.popularity_list = None
        

    def populate_matrix(self, txt_file, encoding='utf8'):
        with codecs.open(txt_file, 'r', encoding=encoding) as f:
            f_data = eval(f.read())
        
        for group in f_data:
            update_group = []
            for element in group:
                if type(element) == tuple:
                    update_group.append(element[0])
                else:
                    update_group.append(element)
            
            combinations = itertools.combinations(update_group, 2)
            for pair in combinations:
                self.update_matrix(pair)

        
    def update_matrix(self, lista_de_individuos):
        
        if len(lista_de_individuos) < 2:
            print("A lista de elementos fornecida deve possuir uma quantidade de elementos superior a dois")
        
        elif len(lista_de_individuos) > 2:
            combinations = itertools.combinations(lista_de_individuos, 2)
            for pair in combinations:
                self.update_matrix(pair)
        
        else:
            unique_id_1 = self.referencia.get_unique_id(lista_de_individuos[0])
            unique_id_2 = self.referencia.get_unique_id(lista_de_individuos[1])

            unique_id_1_idx = self.referencia.get_unique_id_matrix_idx(unique_id_1)
            unique_id_2_idx = self.referencia.get_unique_id_matrix_idx(unique_id_2)

            self.matrix[unique_id_1_idx, unique_id_2_idx] += 1
            self.matrix[unique_id_2_idx, unique_id_1_idx] += 1
            
        
    def show_popularity_matrix(self):
        pow2_matrix = np.matmul(self.matrix, self.matrix)
        pow2_matrix = pow2_matrix - pow2_matrix.min()
        return pow2_matrix
        
    def show_popularity_list(self):
        points = self.show_popularity_matrix()[list(self.get_diagonal),list(self.get_diagonal)]
        popularity_list = list(zip(self.referencia.get_unique_id_list(), points))
        popularity = lambda popul: popul[1]
        popularity_list.sort(key=popularity, reverse=True)
        return popularity_list
    
    def show_matriculas(self):
        r = []
        for line in self.show_popularity_list():
            r.append(self.referencia.get_refs(line[0])[1])
        print(r)
    
    def calc_poularity_idx(self):
        r = []
        for line in self.show_popularity_list():
            ano_mat = 20-int(self.referencia.get_refs(line[0])[1].split('/')[0])
            score = int(line[1])
            idx = score / ano_mat
            tp = []
            tp.append(self.referencia.get_refs(line[0])[1])
            tp.append(idx)
            r.append(tp)
        return r
        
    def show_singular_info(self, identificador):
        
        if not self.referencia.unique_hash.get(identificador):
            identificador = self.referencia.get_unique_id(identificador)
        
        print('Informações gerais da matriz de tempo de contato:')
        not_null = etd_mat3.matrix != 0

        print('Mean:', etd_mat3.matrix[not_null].mean())
        print('Maximum:', etd_mat3.matrix.max())
        print('')

        print('Informações do/a estudante:')
        array_do_estudante = etd_mat3.matrix[etd_mat3.referencia.get_unique_id_matrix_idx(identificador)]
        print(etd_mat3.referencia.get_refs(identificador))
        print('Sum:', array_do_estudante.sum())
        not_null = array_do_estudante != 0
        print('Etd Mean:', array_do_estudante[not_null].mean())
        print('Etd Max:', array_do_estudante.max())

        outros_com_mais_tempo_de_contato_presumido = array_do_estudante == array_do_estudante.max()

        counter = itertools.count()
        for i in outros_com_mais_tempo_de_contato_presumido:
            if i:
                unique_id = etd_mat3.referencia.get_unique_id_from_int(next(counter))
                print(unique_id, etd_mat3.referencia.get_refs(unique_id))        

'''

etd_mat3 = RelationalMatrix(estudantes3)

def populate_single_matrix(arquivo, matrix_ob):
    matrix_ob.populate_matrix(arquivo, 'cp1252')
    

async def populate_matrix(arquivo, matrix_ob):
    return populate_single_matrix(arquivo, matrix_ob)

loop = asyncio.get_event_loop()
dados = loop.run_until_complete(asyncio.gather(
    populate_matrix('2014-2-Disciplinas_out_grps.txt', etd_mat3),
    populate_matrix('2015-1-Disciplinas_out_grps.txt', etd_mat3),
    populate_matrix('2015-2-Disciplinas_out_grps.txt', etd_mat3),
    populate_matrix('2016-1-Disciplinas_out_grps.txt', etd_mat3),
    populate_matrix('2016-2-Disciplinas_out_grps.txt', etd_mat3),
    populate_matrix('2017-1-Disciplinas_out_grps.txt', etd_mat3),
    populate_matrix('2017-2-Disciplinas_out_grps.txt', etd_mat3),
    populate_matrix('2018-1-Disciplinas_out_grps.txt', etd_mat3),
    populate_matrix('2018-2-Disciplinas_out_grps.txt', etd_mat3),
    populate_matrix('2019-1-Disciplinas_out_grps.txt', etd_mat3),
))

print(etd_mat3.matrix.sum())
print(etd_mat3.matrix.size)

'''
