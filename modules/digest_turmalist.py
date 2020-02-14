import os
import codecs
import re


def process_line(linha):
    linha = linha.replace('  ',';')
    linha = linha.replace(' ','=')
    while True:
        if linha.find(';;') != -1:
            linha = linha.replace(';;',';')
        else:
            break
    linha = linha.split(';')
    return linha


def clean_cell(cell):
    if cell[0] == '=':
        return cell[1:].replace('=', ' ').replace('\r\n','')
    else:
        return cell.replace('=', ' ').replace('\r\n','')


def clean_all_cells(list_of_columns):
    output = []
    for cell in list_of_columns:
        if not cell == '':
            output.append(clean_cell(cell))
    return output


def get_list_head(linha):
    linha = process_line(linha)
    nome_disciplina = clean_cell(linha[1])
    codigo = clean_cell(linha[2])
    turma = clean_cell(linha[3])
    periodo = clean_cell(linha[4])
    return [nome_disciplina, codigo, turma, periodo]


def add_to_index_dict(key, value, index_dict):
    keyword = clean_cell(key)
    value_nfo = clean_cell(value)
    if index_dict.get(keyword):
        if not value_nfo in index_dict[keyword]:
            index_dict[keyword].append(value_nfo)
    else:
        index_dict[keyword] = [value_nfo]
    return index_dict


def make_lists_of_tuples_from_kvl_dict(dictionary):
    output = []
    for key in dictionary.keys():
        inner_list = []
        inner_list.append(key)
        for value in dictionary[key]:
            inner_list.append(value)
        output.append(tuple(inner_list))
    return output


def make_list_of_tuples_from_all_kvl_dicts(dictionary):
    output = []
    for idt_dict_obj in dictionary:
        output += make_lists_of_tuples_from_kvl_dict(idt_dict_obj)
    return list(set(output))


def join_lists(lists_to_join):
    output = []
    for list_obj in lists_to_join:
        output += list_obj
    return list(set(output))


def process_file(filename):
    with codecs.open(filename, "r", encoding="cp1252") as f:
        fdata = f.readlines()

    idt_dict = {}
    idt_dicts = []
    past_grabbed_disciplin_name = ''
    current_idx = 0
    n_print = 0
    print_next_line = False
    columns_tmp = []
    current_grabbed_disciplin_cred = 0
    get_cred_num = False
    info_disciplin = []
    info_disciplin_to_save = []

    for linha in fdata:
        if get_cred_num:
            cred_line = clean_all_cells(process_line(linha))
            current_grabbed_disciplin_cred = int(cred_line[1].split(' - ')[0])
            if not type(info_disciplin[-1]) == int:
                    info_disciplin.append(current_grabbed_disciplin_cred)
                    info_disciplin_to_save.append((info_disciplin[1], info_disciplin[-1]))
                    #if info_disciplin[-1] == 0:
                        #print(info_disciplin)
                        #input()
            get_cred_num = False

        if linha.find(u'Código') != -1:
            n_print = current_idx + 1
            #input('opa')

        if linha.find(u'Créditos / Horas') != -1:
            get_cred_num = True

        try:
            if current_idx == n_print:
                head_nfo = get_list_head(linha)
                #print(head_nfo)
                #input()
                current_grabbed_disciplin_name = head_nfo[0] + ' ' + head_nfo[2]
                #print(current_grabbed_disciplin_name)
                if not current_grabbed_disciplin_name == past_grabbed_disciplin_name:
                    past_grabbed_disciplin_name = current_grabbed_disciplin_name
                    info_disciplin = get_list_head(linha)
                    #info_disciplin.append(current_grabbed_disciplin_cred)
                    #print('informações: ', info_disciplin)
                    #input()
                    idt_dicts.append(idt_dict.copy())
                    idt_dict = {}

            if print_next_line:
                columns = process_line(linha)
                columns = clean_all_cells(columns_tmp + columns)
                #print('informações da disciplina:',columns)
                #input()

                try:
                    if columns[3] == 'TR' or columns[3] == 'SR' or columns[3] == 'CC':
                        pass
                    elif int(columns[4]) > 50:
                        pass
                    else:
                        key = columns[2]
                        value = columns[1]
                        idt_dict = add_to_index_dict(key, value, idt_dict)
                        idt_dict = add_to_index_dict(key, str(info_disciplin[-1]), idt_dict)

                except ValueError:
                    pass

                print_next_line = False


            if re.search(r"^\s*\d*\s*\d\d/\d*\s*", linha) != None:
                columns = process_line(linha)
                columns_tmp = columns
                print_next_line = True

        except IndexError:
            pass

        current_idx += 1

    #print(info_disciplin_to_save)

    with codecs.open(filename.replace('.txt', '_')+'out_turma_info.txt', "w", encoding="cp1252") as f:
        for l in info_disciplin_to_save:
            f.write(str(l)+'\n')

    with codecs.open(filename.replace('.txt', '_')+'out_grps.txt', "w", encoding="cp1252") as f:
        out_file = []
        for idt_dict_ob in idt_dicts:
            out_file.append(make_lists_of_tuples_from_kvl_dict(idt_dict_ob))
        f.write(str(out_file))
    
    lines_out = make_list_of_tuples_from_all_kvl_dicts(idt_dicts)
    with codecs.open(filename.replace('.txt', '_')+'out.txt', "w", encoding="cp1252") as f:
        for l in lines_out:
            f.write(str(l)+'\n') 


def process_all_files(folder):
    init_folder = os.getcwd()
    files_in_folder = os.listdir(folder)
    os.chdir(folder)
    for filename in files_in_folder:
        if filename.find('Disciplinas.txt') != -1:
            process_file(filename)
    os.chdir(init_folder)
