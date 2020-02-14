
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
#  Copyright 2017 Daniel Cruz <bwb0de@bwb0dePC>
#  Version 0.1
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

import itertools
import re
import os

from collections import OrderedDict
from modules.cli_tools import strip_simbols, strip_spaces, verde, amarelo, select_op, limpar_tela, branco, amarelo, vermelho
import modules.py_pickle_handlers as pk


class PickleDataType():
    def __init__(self):
        self.target_folder = False
        self.filename = False

    def persist(self, file_ext=False, fname=False):
        if fname:
            self.filename = fname

        if not self.filename:
            self.filename = input('Defina o nome para o arquivo de saída: ')

        if file_ext:
            self.filename = self.filename.strip() + file_ext
            
        if not self.target_folder:
            input_value = input('Defina a pasta de destino [{}]: '.format(amarelo("aperte ENTER para pasta corrente")))
            if not input_value:
                self.target_folder = '.'

        pk.write_pickle(self, self.target_folder, self.filename)

    def fullpath(self):
        return '{folder}{os_sep}{filename}'.format(folder=self.target_folder, os_sep=os.sep, filename=self.filename)



class Form(PickleDataType):
    def __init__(self, titulo, folder):
        def definir_questoes():
            output = OrderedDict()
            q_num = itertools.count()
            
            while True:
                limpar_tela()
                n = next(q_num)
                output[n] = OrderedDict()
                output[n]['regex'] = False
                output[n]['enunciado'] = self.read_input(input_label="Qual o enunciado da questão?")
                output[n]['tipo_dado'] = select_op(['string', 'int', 'float', 'list'], 1, input_label="Selecione o tipo de dado")[0]
                output[n]['tipo_questão'] = select_op(['text', 'radio', 'checkbox'], 1, input_label="Selecione o tipo de questão")[0]
                
                if output[n]['tipo_dado'] == 'string':
                    op = self.read_input(input_label='Necessário validar a informação?', data_pattern='[sn]', waring_msg='Responda ["s" ou "n"]...')
                    if op == 's':
                        output[n]['regex'] = self.read_input(input_label="Qual a expressão regular de validação da informação?")
                
                output[n]['warning_msg'] = self.read_input(input_label="Qual a mensagem de alerta em caso de erro?")
                output[n]['warning_color'] = amarelo

                op = self.read_input(input_label='Inserir outra questão?', data_pattern='[sn]', waring_msg='Responda ["s" ou "n"]...')
                if op == 'n': break
            
            return output


        super(Form, self).__init__()
        self.target_folder = folder
        self.titulo = titulo
        self.q = definir_questoes()
        self.persist()

    def __repr__(self):
        return self.filename

    def executar_formulario(self):
        respostas = OrderedDict()
        for n in self.q.keys():
            respostas[self.q[n]['enunciado']] = self.read_input(\
                input_label=self.q[n]['enunciado'],\
                dada_type=self.q[n]['tipo_dado'],\
                data_pattern=self.q[n]['regex'],\
                waring_msg=self.q[n]['warning_msg'],\
                warning_color=self.q[n]['warning_color'])
        return respostas


    def split_and_strip(self, string, list_item_delimitor=','):
        output = string.split(list_item_delimitor)
        idx = itertools.count()
        for i in output: output[next(idx)] = i.strip()
        return output


    def read_input(self, input_label=False, dada_type='string', data_pattern=False, prompt="$: ", list_item_delimitor=',', waring_msg="Resposta inválida ou em formato inadequado...", clear_screen=False, label_color=branco, prompt_color=branco, warning_color=vermelho, callback=False):
        if clear_screen:
            limpar_tela()
         
        if input_label:
            print(input_label)

        while True:

            response = input(prompt_color(prompt))
            all_ok = False

            if not data_pattern:
                if dada_type == 'string':
                    print(response)
                    break
                
                elif dada_type == 'int':
                    try:
                        response = int(response)
                        all_ok = True
                    
                    except ValueError: print(warning_color(waring_msg))
                
                elif dada_type == 'float':
                    try: 
                        response = float(response)
                        all_ok = True
                    
                    except ValueError: print(warning_color(waring_msg))

                elif dada_type == 'list':
                    try: 
                        response = self.split_and_strip(response, list_item_delimitor)
                        all_ok = True
                    
                    except ValueError: print(warning_color(waring_msg))
            
                if all_ok:
                    break
                
            else:
                try:
                    re.search(data_pattern, response).string
                    break

                except AttributeError:
                    print(warning_color(waring_msg))
        
        return response



class Extended_UniqueItem_List(list):
    def __init__(self, iterator=()):
        super(Extended_UniqueItem_List, self).__init__(iterator)
        self.sorted = False

    def __sub__(self, other):
        for element in other:
            self.remove(element)
        return self

    def __str__(self):
        output = ""
        for element in self:
            output += ' -' + element + '\n'
        return output

    def append(self, element):
        if self.index(element):
            return

        try:
            if element > self[-1]:
                self.sorted = True
            else:
                self.sorted = False
        except IndexError:
            self.sorted = True
        
        super(Extended_UniqueItem_List, self).append(element)

        if not self.sorted:
            self.sort()

    def index(self, element, self_list_nfo=False): # Bisection search
        if not self_list_nfo:
            self_list_nfo = self

        if len(self_list_nfo) == 0:
            return False
        
        elif len(self_list_nfo) == 1:
            if element == self_list_nfo[0]:
                return True
            else:
                return False

        slice_init = 0
        slice_end = len(self_list_nfo)
        section_mid_point_ref = slice_end - slice_init
        mid = (section_mid_point_ref // 2)
        position_fixer = slice_init
        

        while section_mid_point_ref != 0:
            section = self_list_nfo[slice_init:slice_end]

            if len(section) == 1:
                if section[0] == element:
                    return position_fixer + mid
                else:
                    return False

            if section[mid] == element:
                return position_fixer + mid
            
            elif element > section[mid]:
                slice_init = slice_init + mid
                fixer_pass = False
                
            elif element < section[mid]:
                slice_end = mid + position_fixer
                fixer_pass = True
            
            if not fixer_pass:
                position_fixer += mid
                
            section_mid_point_ref = slice_end - slice_init
            mid = (section_mid_point_ref // 2)
        
        return False
            


class ExtendedDict(OrderedDict):
    def __add__(self, other):
        if len(self) > len(other):
            iterated_dict = other.items()
            copied_dict = self.copy()
        else:
            iterated_dict = self.items()
            copied_dict = other.copy()

        for item in iterated_dict:
            if copied_dict.get(item[0]):
                if type(copied_dict[item[0]]) == list:
                    copied_dict[item[0]].append(item[1])
                else:
                    copied_dict[item[0]] = [copied_dict[item[0]], item[1]]
            else:
                copied_dict[item[0]] = item[1]
        return copied_dict
    
    def append(self, key, value):
        if not self.get(key):
            self[key] = [value]
        else:
            self[key].append(value)


class FileIndexDict(ExtendedDict, PickleDataType):
    def __init__(self):
        super(FileIndexDict, self).__init__()
        self.target_folder = False
        self.filename = False


