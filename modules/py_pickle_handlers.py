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


import io
import os
import pickle

from modules.cli_tools import list_col_responses, dict_from_table, select_ops, branco, amarelo, vermelho


def read_pickle(obj_file, folder='.'):
	if obj_file.find(os.sep) != -1:
		obj_file_io = io.open(obj_file,'rb')
	else:
		obj_file_io = io.open(os.path.join(folder, obj_file),'rb')
	OBJ = pickle.load(obj_file_io)
	return OBJ


def write_pickle(OBJ, folder, filename='pickle.ob'):
	obj_file = io.open(os.path.join(folder, filename),'wb')
	pickle.dump(OBJ, obj_file)
	obj_file.close()



def read_data_folder(folder):
    list_of_files = os.listdir(folder)
    for f in list_of_files:
        yield read_pickle(f, folder)

def show_data_folder(folder):
    info = read_data_folder(folder)
    while True:
        try: print(next(info))
        except StopIteration: break

def return_object_location_list(folder):
	list_of_files = os.listdir(folder)
	output = []
	for f in list_of_files:
		output.append(folder+f)
	return output


def return_object_info_and_location_list(folder, only_names=False):
	info = read_data_folder(folder)
	output = []
	while True:
		try:
			current_obj = next(info)
			if only_names:
				obj_info = current_obj.dados_gerais['Nome']
				output.append(obj_info)
			else:
				obj_info = current_obj.__repr__()
				obj_location = current_obj.fullpath()
				item_string = ';'.join([obj_info, obj_location])
				output.append(item_string)
		except StopIteration:
			return output
	

def load_selected_pickle_ob(label, folder, label_color=branco, item_color=amarelo, warning_color=vermelho):
	itens = return_object_info_and_location_list(folder)
	lista_nominal_itens = list(list_col_responses(itens, col_num=0, delimitor=';'))
	localizacao_itens = dict_from_table(itens, delimitor=';')
	itens_selecionados = select_ops(lista_nominal_itens, 1, input_label=label, item_color=item_color, warning_color=warning_color)
	for item in itens_selecionados:
		caminho_para_item = localizacao_itens[item][0]
		arquivo_item = caminho_para_item.split('/')[-1]
		pasta_item = caminho_para_item.strip(arquivo_item)
		yield read_pickle(caminho_para_item)


def set_target_pickle_file(piclke_file_folder, piclke_filename, target_folder):
	cena = next(load_selected_pickle_ob("Selecione o cena: ", piclke_file_folder))
	os.system('ln -s -f "{obj_f}" "{target_folder}/{target_file}"'.format(obj_f=cena.fullpath(), target_folder=target_folder, target_file=piclke_filename))
	return cena

