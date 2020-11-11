import re

def parse_block(block):
    block = re.sub('\#.*\".*?\".*', '', block)
    strings = re.findall('\".*?\"', block)
    block = re.sub('\".*?\"', ' %s ', block)
    block = re.sub('#.*', '\n', block)
    block = re.sub('(\[\[[\w&$]*\]|\^\^[\w&$]*\^|[\>\<\!\=]+|[\{\}\]^])', r' \1 ', block)
    block = block.strip()
    block = re.split('\s+', block)

    if strings:
        i = 0

        for ii in range(len(block)):
            if block[ii] == '%s':
                block[ii] = strings[i]

                i += 1
                
    file = list()
    stack = [file]
    rhs = False
    
    for token in block:
        if token == '=' or token == '>' or token == '<' or token == '>=' or token == '<=' or token == '==' or token == '!=':
            rhs = True

            stack[-1][-1] = [stack[-1][-1], token]
            stack.append(stack[-1][-1])
        elif token == '{':
            stack[-1].append(list())

            if rhs:
                rhs = False
                
                stack.append(stack.pop()[-1])
            else:
                stack.append(stack[-1][-1])
        elif token == '}' or token == ']' or token == '^':
            stack.pop()
        elif '[[' in token or '^^' in token:
            stack[-1].append([token[1:], list()])
            stack.append(stack[-1][-1][1])
        else:
            stack[-1].append(token)

            if rhs:
                rhs = False

                stack.pop()

    return file

def reconstruct(file, t=''):
    txt = ''

    for f in file:
        if f:
            if len(f) == 3 and type(f[0]) != type(list()) and type(f[1]) != type(list()):
                if type(f[2]) == type(list()):
                    tail = ''
                        
                    if f[2]:
                        if type(f[2][0]) != type(list()):
                            tail = ' '.join(f[2])
                        else:
                            tail = '\n%s%s' % (reconstruct(f[2], t + '\t'), t)

                    txt += '%s%s %s { %s}\n' % (t, f[0], f[1], tail)
                else:
                    txt += '%s%s %s %s\n' % (t, f[0], f[1], f[2])
            elif len(f) == 2 and type(f[0]) != type(list()):
                txt += '%s[%s\n%s%s]\n' % (t, f[0], reconstruct(f[1], t + '\t'), t)

    return txt

if __name__ == '__main__':
    with open('gamestate', encoding='utf-8-sig') as f:
        t = f.read()

        glob_vars = dict()
        glob_lsts = dict()

        print('Parsing Globals')

        start = t.find('\nvariables={')
        end = t.find('\ngame_rules={', start)

        f = parse_block(t[start:end])

        for var in f[0][2][0][2]:
            if not 'trade_do_trade_t' in var[0][2].strip('"'):
                glob_vars[var[0][2].strip('"')] = (var[2][2][0][2], var[2][2][1][2])
        for lst in f[0][2][1][2]:
            glob_lsts[lst[0][2].strip('"')] = [(var[2][0][2], var[2][1][2]) for var in lst[1:]]

        chars = dict()

        for name in ['prod_templates', 'prod_instances', 'trade_merchants', 'tech_techs', 'tech_eras', 'build_templates', 'build_slots_active']:
            for var in glob_lsts[name]:
                if not var[1] in chars:
                    chars[var[1]] = (dict(), dict())

        print('Parsing Chars')
        
        start = t.find('\nliving={')
        end = t.find('\ndead_unprunable={', start)

        for char in parse_block(t[start:end])[0][2]:
            if char[0] in chars:
                lst_var = chars[char[0]][0]
                lst_lst = chars[char[0]][1]
                
                for entry in char[2]:
                    if entry[0] == 'alive_data':
                        for entry in entry[2]:
                            if entry[0] == 'variables':
                                for entry in entry[2]:
                                    if entry[0] == 'data':
                                        for var in entry[2]:
                                            if var[2][2]:
                                                if len(var[2][2]) >= 2:
                                                    lst_var[var[0][2].strip('"')] = (var[2][2][0][2], var[2][2][1][2])
                                                else:
                                                    lst_var[var[0][2].strip('"')] = (var[2][2][0][2], 0)
                                            else:
                                                lst_var[var[0][2].strip('"')] = ()
                                    elif entry[0] == 'list':
                                        for lst in entry[2]:
                                            lst_lst[lst[0][2].strip('"')] = list()

                                            for var in lst[1:]:
                                                if len(var[2]) == 1:
                                                    lst_lst[lst[0][2].strip('"')].append((var[2][0][2], 0))
                                                else:
                                                    lst_lst[lst[0][2].strip('"')].append((var[2][0][2], var[2][1][2]))
                                break
                        break

        print('Parsing Provs')
        
        provs = dict()
        
        start = t.find('\nprovinces={')
        end = t.find('\nlanded_titles={', start)

        for province in parse_block(t[start:end])[0][2]:
            provs[province[0]] = (dict(), dict())

            lst_var = provs[province[0]][0]
            lst_lst = provs[province[0]][1]

            for entry in province[2]:
                if entry[0] == 'variables':
                    for entry in entry[2]:
                        if entry[0] == 'data':
                            for var in entry[2]:
                                if var[2][2]:
                                    if len(var[2][2]) >= 2:
                                        lst_var[var[0][2].strip('"')] = (var[2][2][0][2], var[2][2][1][2])
                                    else:
                                        lst_var[var[0][2].strip('"')] = (var[2][2][0][2], 0)
                                else:
                                    lst_var[var[0][2].strip('"')] = ()
                        elif entry[0] == 'list':
                            for lst in entry[2]:
                                lst_lst[lst[0][2].strip('"')] = [(var[2][0][2], var[2][1][2]) for var in lst[1:]]
                    break

        print('Parsing Titles')
        
        titles = dict()
        id_to_title = dict()
        
        start = t.find('\nlanded_titles={')
        end = t.find('\ndynasties={', start)

        for title in parse_block(t[start:end])[0][2][1][2]:
            name = ''
            
            for entry in title[2]:
                if entry[0] == 'key':
                    name = entry[2].strip('"')
                    
                    break

            if name[:2] != 'c_':
                continue

            id_to_title[title[0]] = name

            titles[name] = (dict(), dict())

            lst_var = titles[name][0]
            lst_lst = titles[name][1]

            for entry in title[2]:
                if entry[0] == 'variables':
                    for entry in entry[2]:
                        if entry[0] == 'data':
                            for var in entry[2]:
                                if var[2][2]:
                                    if len(var[2][2]) >= 2:
                                        lst_var[var[0][2].strip('"')] = (var[2][2][0][2], var[2][2][1][2])
                                    else:
                                        lst_var[var[0][2].strip('"')] = (var[2][2][0][2], 0)
                                else:
                                    lst_var[var[0][2].strip('"')] = ()
                        elif entry[0] == 'list':
                            for lst in entry[2]:
                                lst_lst[lst[0][2].strip('"')] = list()

                                for var in lst[1:]:
                                    if len(var[2]) == 1:
                                        lst_lst[lst[0][2].strip('"')].append((var[2][0][2], 0))
                                    else:
                                        lst_lst[lst[0][2].strip('"')].append((var[2][0][2], var[2][1][2]))
                    break

        print('Writing Events')

        templates = dict()
        names = dict()

        with open('common\\scripted_effects\\00_init_industry.txt', encoding='utf-8-sig') as ff:
            for scripts in parse_block(ff.read()):
                if scripts[0] == 'init_industry_templates':
                    for template in scripts[2]:
                        if template[0] == 'prod_new_template':
                            for entry in template[2]:
                                if entry[0] == 'name':
                                    templates[glob_vars[entry[2]][1]] = entry[2]
                                    
                                    break
                    break
        with open('common\\scripted_effects\\00_init_build.txt', encoding='utf-8-sig') as ff:
            for scripts in parse_block(ff.read()):
                if scripts[0] == 'init_buildings':
                    for template in scripts[2]:
                        if template[0] == 'build_new_template':
                            for entry in template[2]:
                                if entry[0] == 'name':
                                    names[glob_vars[entry[2]][1]] = entry[2]
                                    
                                    break
                    break
        
        event = '''save_data.0%s = {
	type = empty
	hidden = yes
	
	immediate = { 
%s
	}
	
	option = {%s
	}
}
'''
        nxt = '''
            trigger_event = {
                id = save_data.0%s
            }'''
        
        arhat = '\t\tcharacter:999999 = { set_global_variable = { name = arhat value = this } every_courtier_or_guest = { limit = { is_character = yes } death = natural } every_councillor = { limit = { is_character = yes } death = natural } }'
        create_character = '\t\tcreate_character = { save_temporary_scope_as = save_data_t gender = male trait = character_not_1 employer = global_var:arhat faith = global_var:arhat.faith culture = global_var:arhat.culture dynasty = none }\n'
        character_data = '\t\tscope:save_data_t = {\n%s\n\t\t}\n'
        
        def helper(form, name, data, id_to_title):
            if data:
                if data[0] == 'value':
                    if int(data[1]) / 1000 > 210000:
                        return '%s = { name = %s %s = %s }\n' % (form[0], name, form[1], round((int(data[1]) - 18446744073709551616) / 1000, 3))
                    else:
                        return '%s = { name = %s %s = %s }\n' % (form[0], name, form[1], round(int(data[1]) / 1000, 3))
                elif data[0] == 'prov':
                    return '%s = { name = %s %s = province:%s }\n' % (form[0], name, form[1], data[1])
                elif data[0] == 'boolean':
                    return '%s = { name = %s }\n' % (form[0], name)
                elif data[0] == 'lt':
                    return '%s = { name = %s %s = title:%s }\n' % (form[0], name, form[1], id_to_title[data[1]])
                else:
                    return ''
            else:
                return '%s = { name = %s %s = 0 }\n' % (form[0], name, form[1])
        
        with open('events\\save_data.txt', 'w', encoding='utf-8-sig') as ff:
            out = ['namespace = save_data\n\n']
            
            outout = [arhat]

            print('Writing Global Event')

            for name, data in glob_vars.items():
                if data[0] == 'char' and data[1] in chars:
                    outout.append(create_character)
                    outout.append(character_data % ''.join([helper(('\t\t\tset_variable', 'value'), n, d, id_to_title) for n, d in chars[data[1]][0].items()]))
                    outout.append('\t\tset_global_variable = { name = %s value = scope:save_data_t }\n' % name)

                    if ('char', data[1]) in glob_lsts['prod_templates']:
                        outout.append('\t\tadd_to_global_variable_list = { name = prod_templates target = scope:save_data_t }\n')
                    elif ('char', data[1]) in glob_lsts['tech_techs']:
                        outout.append('\t\tadd_to_global_variable_list = { name = tech_techs target = scope:save_data_t }\n')
                    elif ('char', data[1]) in glob_lsts['tech_eras']:
                        outout.append('\t\tadd_to_global_variable_list = { name = tech_eras target = scope:save_data_t }\n')
                    elif ('char', data[1]) in glob_lsts['build_templates']:
                        outout.append('\t\tadd_to_global_variable_list = { name = build_templates target = scope:save_data_t }\n')
                else:
                    outout.append(helper(('\t\tset_global_variable', 'value'), name, data, id_to_title))

            out.append(event % (1, ''.join(outout), nxt % 2))

            i = 1
            ii = 500
            iii = 2
            
            loop = True

            while loop:
                outout = []
                
                print(f'Writing Provinces {i}~{ii}')

                for iiii in range(i, ii + 1):
                    iiii = str(iiii)

                    if not iiii in provs:
                        loop = False

                        break

                    prov = provs[iiii]

                    outout.append('\t\tprovince:%s = {\n' % iiii)

                    for name, data in prov[0].items():
                        if data[0] == 'char' and data[1] in chars:
                            outout.append('\t')
                            outout.append(create_character)
                            outout.append('\t')
                            outout.append(character_data % ''.join([helper(('\t\t\t\tset_variable', 'value'), n, d, id_to_title) for n, d in chars[data[1]][0].items()]))

                            if 'prod_slot' in name:
                                outout.append('\t\t\tadd_to_global_variable_list = { name = prod_instances target = scope:save_data_t }\n')
                                outout.append('\t\t\tglobal_var:%s = { add_to_variable_list = { name = prod_instances target = scope:save_data_t } scope:save_data_t = { set_variable = { name = prod_template value = prev } } }\n' % templates[chars[data[1]][0]['prod_template'][1]])
                                outout.append('\t\t\tadd_to_variable_list = { name = prod_instances target = scope:save_data_t }\n')
                                outout.append('\t\t\tcounty = { add_to_variable_list = { name = prod_instances target = scope:save_data_t } }\n')
                                outout.append('\t\t\tset_variable = { name = %s value = scope:save_data_t }\n' % name)
                            elif 'build_slot' in name:
                                outout.append('\t\t\tscope:save_data_t = { set_variable = { name = build_name value = global_var:%s } }\n' % names[chars[data[1]][0]['build_name'][1]])
                                outout.append('\t\t\tadd_to_global_variable_list = { name = build_slots_active target = scope:save_data_t }\n')
                                outout.append('\t\t\tadd_to_variable_list = { name = build_slots target = scope:save_data_t }\n')
                                outout.append('\t\t\tset_variable = { name = %s value = scope:save_data_t }\n' % name)
                            else:
                                outout.append('\t\t\tadd_to_global_variable_list = { name = trade_merchants target = scope:save_data_t }\n')
                                outout.append('\t\t\tset_variable = { name = trade_merchant value = scope:save_data_t }\n')
                                outout.append('\t\t\tscope:save_data_t = {\n')

                                for n, vs in chars[data[1]][1].items():
                                    for v in vs:
                                        outout.append(helper(('\t\t\t\tadd_to_variable_list', 'target'), n, v, id_to_title))
                                        
                                outout.append('\t\t\t}\n')
                        else:
                            if 'trade_' in name:
                                outout.append('\t\t\tprovince_owner = {\n')
                                outout.append(helper(('\t\t\t\tset_variable', 'value'), name, data, id_to_title))
                                outout.append('\t\t\t}\n')
                            else:
                                outout.append(helper(('\t\t\tset_variable', 'value'), name, data, id_to_title))
                    for name, data in prov[1].items():
                        if 'trade_dat' in name:
                            outout.append('\t\t\tprovince_owner = {\n')

                            for var in data:
                                outout.append(helper(('\t\t\t\tadd_to_variable_list', 'target'), name, var, id_to_title))

                            outout.append('\t\t\t}\n')
                        elif name != 'prod_instances' and name != 'build_slots':
                            for var in data:
                                outout.append(helper(('\t\t\tadd_to_variable_list', 'target'), name, var, id_to_title))

                    outout.append('\t\t}\n')
                    
                out.append(event % (str(iii), ''.join(outout), nxt % str(iii + 1)))
                
                i += 500
                ii += 500
                iii += 1

            print('Writing Title Data Event')

            outout = []

            for name, data in titles.items():
                outout.append('\t\ttitle:%s = {\n' % name)

                for n, d in data[0].items():
                    outout.append(helper(('\t\t\tset_variable', 'value'), n, d, id_to_title))
                for n, vs in data[1].items():
                    if '_dat_' in n:
                        for v in vs:
                            outout.append(helper(('\t\t\tadd_to_variable_list', 'target'), n, v, id_to_title))

                outout.append('\t\t}\n')

            out.append(event % (iii, ''.join([item for item in outout if item]), iii + 1))
            out.append(event % (iii + 1, '''		init_task_templates = yes
		init_rulers = yes	
		task_main = yes''', ''))

            print('Parsing and Reconstructing the Events')

            out[1] = reconstruct(parse_block(out[1]))

            print('Joining the Events')
            
            ff.write(''.join(out))
