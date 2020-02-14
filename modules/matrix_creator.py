
import numpy as np
import codecs
import itertools
import asyncio
import py_pickle_handlers as pk
import os

from collections import OrderedDict
from cli_tools import strip_simbols, strip_spaces, verde, amarelo
from py_obj_data_tools import PickleDataType, Extended_UniqueItem_List, ExtendedDict

estudantes1 = ['Daniel', 'Hamilton', 'Joana', 'Dara', 'Silvana', 'Mara', 'Luisa']
estudantes2 = [('Daniel', '726.669.861-87', '12/009867'), ('THAYS SANTANA ALVES', '11/0041739'), ('Hamilton','889.654.159-88', '12/009869'), ('Eliot', '736.669.861-89', '13/009867'), ('Hilda','119.654.159-11', '12/009847')]

try:
    with codecs.open('out.txt', "r", encoding="cp1252") as f:
        f_data = f.readlines()

    estudantes3 = []
    for line in f_data:
        estudantes3.append(eval(line.strip()))
except:
    print("Não será possível criar a matriz...")


class IndexcedDataType():
    def __init__(self, lista_de_individuos):
        self.reference = UniqueIdt(lista_de_individuos)
        self.target_folder = False
        self.filename = False

    def persist(self):
        if not self.filename:
            self.filename = input('Defina o nome para o arquivo de saída: ')
        if not self.target_folder:
            self.target_folder = input('Defina a pasta de destino [pasta corrente: {}]: '.format(os.getcwd()))
        pk.write_pickle(self, self.target_folder, self.filename)
  
class UniqueIdt():
    def __init__(self, lista_de_individuos):
        self.unique_id_dict = ExtendedDict()
        self.incomming_keys = Extended_UniqueItem_List()
        self.incomming_keys_array = np.array([], dtype='uint32')
        self.indexed_rows = ExtendedDict()
        self.indexed_cols = ExtendedDict()
        self._build_index(lista_de_individuos)

    def _analise_lista_de_individuos(self, lista_de_individuos):
        if type(lista_de_individuos[0]) == tuple:
            index = itertools.count()
            for element in lista_de_individuos[0]:
                index = next(index)
                if not self._may_element_be_converted_into_an_integer(element):
                    sort_by_selected_element = lambda x: x[index]
                    lista_de_individuos.sort(key=sort_by_selected_element)
                    break
            return (lista_de_individuos, 'MultiKey', index)

        elif type(lista_de_individuos[0]) == str:
            lista_de_individuos.sort()
            return (lista_de_individuos, 'SingleKey')


    def _create_incomming_values_matrix(self, list_of_numbers):
        a = np.arange(0,len(list_of_numbers)).reshape((len(list_of_numbers),1))
        b = np.array(list_of_numbers).reshape((len(list_of_numbers),1))
        incomming_values = np.hstack((a,b))
        return incomming_values 


    def _seek_for_correlate_in_numpy_two_columns_matrix(self, value, matrix, col_to_seek):
        if col_to_seek > 1 or col_to_seek < 0:
            print("The 'col_to_seek' argument must be either 0 or 1")
            return
        elif col_to_seek == 1:
            other_col = 0
        else:
            other_col = 1
        local = value == matrix[:,col_to_seek]
        return matrix[:,other_col][local]


    def _create_ranged_equivalent_columns_matrix(self, range_value, num_of_cols):
        arr = np.arange(0,range_value, dtype='uint16').reshape((range_value, 1))
        output = arr.copy()
        counter = itertools.count(start=1)
        n = next(counter)
        while n != num_of_cols:
            output = np.hstack((output,arr))
            n = next(counter)
        return output


    def _build_index(self, lista_de_individuos):
        analisis = self._analise_lista_de_individuos(lista_de_individuos)
        lista_de_individuos_mod = analisis[0]
 
        add_to_incomming_keys_array = []    
        add_to_incomming_keys_controler = {}
        grouped_values_controler = {}
        incomming_keys_controler = {}


        counter = itertools.count()
        if analisis[1] == 'SingleKey':
            for individuo in lista_de_individuos_mod:
                if not self.incomming_keys.get(individuo):
                    n = next(counter)
                    unique_id = n
                    self.unique_id_dict[unique_id] = [individuo]
                    self.incomming_keys.append(individuo)
                    self.indexed_rows[unique_id] = n
                    self.indexed_cols[unique_id] = n

        elif analisis[1] == 'MultiKey':
            index = analisis[2] 
            for grouped_values in lista_de_individuos_mod:
                grouped_values_repr = str(grouped_values)
                if not grouped_values_controler.get(grouped_values_repr):
                    grouped_values_controler[grouped_values_repr] = True

                    trigger_conter = True
                    for element in grouped_values:
                        if trigger_conter:
                            n = next(counter)
                            trigger_conter = False

                        if index == grouped_values.index(element):
                            if not incomming_keys_controler.get(element):
                                incomming_keys_controler[element] = True
                                self.incomming_keys.append(element)
                        else:
                            if len(element) > 1:
                                is_int = self._may_element_be_converted_into_an_integer(element)
                                if is_int:
                                    if not add_to_incomming_keys_controler.get(is_int):
                                        add_to_incomming_keys_array.append((is_int, n))
                                        add_to_incomming_keys_controler[is_int] = True

                        unique_id = n
                        self.unique_id_dict = self._insert_in_unique_id_dict(grouped_values, unique_id, self.unique_id_dict)

        sort_by_ref = lambda x: x[0]
        add_to_incomming_keys_array.sort(key=sort_by_ref)
        range_value = len(self.incomming_keys)

        self.incomming_keys_array = np.array(add_to_incomming_keys_array, dtype='uint32')
        self.indexed_rows = self._create_ranged_equivalent_columns_matrix(range_value, 2)
        self.indexed_cols = self._create_ranged_equivalent_columns_matrix(range_value, 2)

        del(add_to_incomming_keys_array)
        del(add_to_incomming_keys_controler)
        del(grouped_values_controler)
        del(incomming_keys_controler)


    def _may_element_be_converted_into_an_integer(self, element):
        s = strip_simbols(element)
        s = strip_spaces(s)
        try:
            return int(s)
        except ValueError:
            return False


    def _insert_in_unique_id_dict(self, grouped_values, unique_id, unique_id_dict):
        for element in grouped_values:
            if unique_id_dict.get(unique_id):
                if not element in unique_id_dict[unique_id]:
                    unique_id_dict[unique_id].append(element)
            else:
                unique_id_dict[unique_id] = [element]
        return unique_id_dict


    def _rebuild_indexed_rows_reference(self):
        rebuilted_index = ExtendedDict()
        counter = itertools.count()
        
        for row in self.indexed_rows:
            rebuilted_index[row[0]] = next(counter)
        
        self.indexed_rows = np.array(list(rebuilted_index.items()), dtype='uint16')
        
            
    def find_correlate_reference(self, idt):
        try:
            return self.incomming_keys.index(idt)
        except ValueError:
            output = self._seek_for_correlate_in_numpy_two_columns_matrix(idt, self.incomming_keys_array, 0)
            if output.size == 0:
                output = self._seek_for_correlate_in_numpy_two_columns_matrix(idt, self.incomming_keys_array, 1)
            return output
        


class RelationalMatrix(IndexcedDataType):
    def __init__(self, lista_de_individuos):
        super(RelationalMatrix, self).__init__(lista_de_individuos)
        #self.matrix = np.zeros((len(set(lista_de_individuos)), len(set(lista_de_individuos))),dtype='uint8')
        self.populated = False


    def _delete_matrix_rows(self, rows_to_delete):
        rows_indexes = []
        for row_name in sorted(rows_to_delete):
            index_num = self.reference.find_correlate_reference(row_name)
            rows_indexes.append(index_num)
        
        print(rows_indexes)

        self.reference.indexed_rows = np.delete(self.reference.indexed_rows, rows_indexes, axis=0)
        self.matrix = np.delete(self.matrix, rows_indexes, axis=0)

        self.reference._rebuild_indexed_rows_reference()


    def _populate_matrix(self, txt_file, encoding='utf8'):
        with codecs.open(txt_file, 'r', encoding=encoding) as f:
            f_data = eval(f.read())
        
        # Lines in f_data are grouped values of type tuple...

        for group in f_data:
            grab_creditos = True
            update_group = []
            creditos = 1
            for element in group:
                if type(element) == tuple:

                    # Seek for the amount of credits of currente disciplin if 'grab_creditos'...

                    if grab_creditos:
                        grab_creditos = False
                        for item in element:
                            if len(item) == 1:
                                if int(item) == 0:
                                    creditos = 1
                                    break
                                creditos = int(item)
                                break
                    update_group.append(element[0])
                else:
                    update_group.append(element)
            
            combinations = itertools.combinations(update_group, 2)
            for pair in combinations:
                self._update_matrix(pair, creditos)


    def _update_matrix(self, lista_de_individuos, peso):
        
        if len(lista_de_individuos) < 2:
            print("A lista de elementos fornecida deve possuir uma quantidade de dois ou mais elementos.")
        
        elif len(lista_de_individuos) > 2:
            combinations = itertools.combinations(lista_de_individuos, 2)
            for pair in combinations:
                self._update_matrix(pair, peso)
        
        else:

            unique_id_1 = self.reference.find_correlate_reference(lista_de_individuos[0])
            unique_id_2 = self.reference.find_correlate_reference(lista_de_individuos[1])

            unique_id_1_idx = unique_id_1
            unique_id_2_idx = unique_id_2

            self.matrix[unique_id_1_idx, unique_id_2_idx] += peso
            self.matrix[unique_id_2_idx, unique_id_1_idx] += peso
            

    def _show_connections_sorted(self, identificador):
        if not self.reference.unique_id_dict.get(identificador):
            idt = self.reference.find_correlate_reference(identificador)
            try:
                identificador = idt[0]
            except TypeError:
                identificador = idt

        matrix_index = self.reference.indexed_cols[identificador][0]

        output = []
        
        selected_row = self.matrix[matrix_index]
        selected_row_bool_array = selected_row > 0
        selected_values_indexes = np.where(selected_row_bool_array)[0]

        for value in selected_values_indexes:
            info = [self.reference.incomming_keys[value], self.reference.incomming_keys_array[value][0]]
            score = selected_row[value]
            output.append((value, info, score))
        
        score_values = lambda popul: popul[2]
        output.sort(key=score_values, reverse=True)
        return output


    def start_matrix_population(self, target_folder):
        if self.populated:
            print("Matrix populated...")
            return

        init_folder = os.getcwd()
        os.chdir(target_folder)

        def populate_single_matrix(filename, matrix_ob):
            matrix_ob._populate_matrix(filename, 'cp1252')
            
        async def populate_with_fileinfo(filename, matrix_ob):
            return populate_single_matrix(filename, matrix_ob)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(
            populate_with_fileinfo('2014-2-Disciplinas_out_grps.txt', self),
            populate_with_fileinfo('2015-1-Disciplinas_out_grps.txt', self),
            populate_with_fileinfo('2015-2-Disciplinas_out_grps.txt', self),
            populate_with_fileinfo('2016-1-Disciplinas_out_grps.txt', self),
            populate_with_fileinfo('2016-2-Disciplinas_out_grps.txt', self),
            populate_with_fileinfo('2017-1-Disciplinas_out_grps.txt', self),
            populate_with_fileinfo('2017-2-Disciplinas_out_grps.txt', self),
            populate_with_fileinfo('2018-1-Disciplinas_out_grps.txt', self),
            populate_with_fileinfo('2018-2-Disciplinas_out_grps.txt', self),
            populate_with_fileinfo('2019-1-Disciplinas_out_grps.txt', self),
        ))

        os.chdir(init_folder)
        self.populated = True


    def delete_lines(self, substring):
        if self.reference._may_element_be_converted_into_an_integer(substring):
            pass
        else:
            list_of_rows = []
            
            for key in self.reference.incomming_keys:
                if key.find(substring) != -1:
                    list_of_rows.append(key)
            self._delete_matrix_rows(list(set(list_of_rows)))


    def list_users(self, substring):
        print('Listando usuários...')
        for key in self.reference.incomming_keys:
            if key.find(substring) != -1:
                print('» '+key)


    def show_most_common_connections(self, identificador, num_entries):
        return self._show_connections_sorted(identificador)[:num_entries]


    def show_info(self, identificador):
        if type(identificador) == str: 
            unique_id = [self.reference.incomming_keys.get(identificador)]
        elif type(identificador) == int: 
            unique_id = [self.reference.find_correlate_reference(identificador)[0]]
        else: 
            print("Identificador em formato inadequado...")
            return
        
        if not unique_id:
            unique_id = self.reference.find_correlate_reference(identificador)
            if not np.any(self.reference.indexed_rows[:,0] == unique_id):
                print("Linha referente ao valor '%s' foi excluída..." % identificador)
                return
        
        print('Unique ID:', unique_id)
        print('')

        print('Informações do/a estudante:')
        array_do_estudante = self.matrix[unique_id[0]]
        print('')
        
        print(unique_id[0], self.reference.find_correlate_reference(unique_id[0]), self.reference.incomming_keys[unique_id[0]])
        print('Sum:', array_do_estudante.sum())
        not_null = array_do_estudante != 0
        print('Mean:', array_do_estudante[not_null].mean())
        print('Maximum:', array_do_estudante.max())

        print('Pessoas que cursaram uma maior quantidade de créditos com o/a estudante:')
        for pessoa in self.show_most_common_connections(identificador, 10):
            print(pessoa)


