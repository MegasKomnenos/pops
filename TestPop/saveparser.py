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

if __name__ == '__main__':
    names = ['prod_templates', 'prod_instances', 'trade_merchants', 'tech_techs', 'tech_eras', 'build_templates', 'build_slots_active', 'build_slots']
    
    with open('gamestate', encoding='utf-8-sig') as f:
        t = f.read()

        glob_vars = []
        glob_lists = []

        start = t.find('\nvariables={')
        end = t.find('\ngame_rules={', start)

        f = parse_block(t[start:end])

        for var in f[0][2][0][2]:
            glob_vars.append((var[0][2].strip('"'), var[2][2][0][2], var[2][2][1][2]))
        for lst in f[0][2][1][2]:
            foo = (lst[0][2].strip('"'), [])

            for var in lst[1:]:
                foo[1].append((var[2][0][2], var[2][1][2]))

            glob_lists.append(foo)

        chars = dict()

        i = 800000

        for lst in glob_lists:
            if lst[0] in names:
                for var in lst[1]:
                    if not var[1] in chars:
                        chars[var[1]] = (i, [], [])
                        i += 1

        start = t.find('\nliving={')
        end = t.find('\ndead_unprunable={', start)

        for char in parse_block(t[start:end])[0][2]:
            if char[0] in chars:
                lst_var = chars[char[0]][1]
                lst_lst = chars[char[0]][2]
                
                for entry in char[2]:
                    if entry[0] == 'alive_data':
                        for entry in entry[2]:
                            if entry[0] == 'variables':
                                for entry in entry[2]:
                                    if entry[0] == 'data':
                                        for var in entry[2]:
                                            if var[2][2]:
                                                if len(var[2][2]) >= 2:
                                                    lst_var.append((var[0][2].strip('"'), var[2][2][0][2], var[2][2][1][2]))
                                                else:
                                                    lst_var.append((var[0][2].strip('"'), var[2][2][0][2], 0))
                                            else:
                                                lst_var.append((var[0][2].strip('"')))
                                    elif entry[0] == 'list':
                                        for lst in entry[2]:
                                            foo = (lst[0][2].strip('"'), [])

                                            for var in lst[1:]:
                                                foo[1].append((var[2][0][2], var[2][1][2]))

                                            lst_lst.append(foo)
                                break
                        break

        with open('history\\characters\\sim_data.txt', 'w', encoding='utf-8-sig') as ff:
            template = '''%s = {
    name = "Arhat"
    religion = "theravada"
    culture = "bodpa"
    trait = character_not_1
    dynasty = character_not
    1.1.1 = {
        birth = yes
        
        if = {
            limit = {
                NOT = {
                    court_owner = character:999999
                }
            }
            set_employer = character:999999
        }
    }
}
'''
            out = []

            for data in chars.values():
                out.append(template % data[0])

            ff.write(''.join(out))

        with open('common\\scripted_effects\\00_sim_char.txt', 'w', encoding='utf-8-sig') as ff:
            out = ['sim_char = {\n']

            for data in chars.values():
                foo = []

                for var in data[1]:
                    if type(var) == type(tuple()):
                        if var[1] == 'value':
                            if int(var[2]) / 1000 > 210000:
                                foo.append('set_variable = { name = %s value = 0 } ' % var[0])
                            else:
                                foo.append('set_variable = { name = %s value = %s } ' % (var[0], round(int(var[2]) / 1000, 3)))
                        elif var[1] == 'char':
                            foo.append('set_variable = { name = %s value = character:%s } ' % (var[0], chars[var[2]][0]))
                        elif var[1] == 'prov':
                            foo.append('set_variable = { name = %s value = province:%s } ' % (var[0], var[2]))
                        elif var[1] == 'boolean':
                            foo.append('set_variable = { name = %s } ' % var[0])
                        elif var[1] == 'lt':
                            foo.append('set_variable = { name = %s value = title:%s } ' % (var[0], var[2]))
                    else:
                        foo.append('set_variable = { name = %s } ' % var)
                for lst in data[2]:
                    for var in lst[1]:
                        if var[0] == 'char':
                            foo.append('add_to_variable_list = { name = %s target = character:%s } ' % (lst[0], chars[var[1]][0]))
                        elif var[0] == 'prov':
                            foo.append('add_to_variable_list = { name = %s target = province:%s } ' % (lst[0], var[1]))
                        elif var[0] == 'lt':
                            foo.append('add_to_variable_list = { name = %s target = title:%s } ' % (lst[0], var[1]))

                out.append('\tcharacter:%s = { %s}\n' % (data[0], ''.join(foo)))

            out.append('}')
            
            ff.write(''.join(out))

        with open('common\\scripted_effects\\00_sim_glob.txt', 'w', encoding='utf-8-sig') as ff:
            out = ['sim_glob = {\n']

            for var in glob_vars:
                if type(var) == type(tuple()):
                    if var[1] == 'value':
                        if int(var[2]) / 1000 > 210000:
                            out.append('\tset_global_variable = { name = %s value = 0 }\n' % var[0])
                        else:
                            out.append('\tset_global_variable = { name = %s value = %s }\n' % (var[0], round(int(var[2]) / 1000, 3)))
                    elif var[1] == 'char' and var[2] in chars:
                        out.append('\tset_global_variable = { name = %s value = character:%s }\n' % (var[0], chars[var[2]][0]))
                    elif var[1] == 'prov':
                        out.append('\tset_global_variable = { name = %s value = province:%s }\n' % (var[0], var[2]))
                    elif var[1] == 'boolean':
                        out.append('\tset_global_variable = { name = %s }\n' % var[0])
                    elif var[1] == 'lt':
                        out.append('\tset_global_variable = { name = %s value = title:%s }\n' % (var[0], var[2]))
                else:
                    out.append('\t\tset_global_variable = { name = %s }\n' % var)
            for lst in glob_lists:
                for var in lst[1]:
                    if var[0] == 'char':
                        out.append('\tadd_to_global_variable_list = { name = %s target = character:%s }\n' % (lst[0], chars[var[1]][0]))
                    elif var[0] == 'prov':
                        out.append('\tadd_to_global_variable_list = { name = %s target = province:%s }\n' % (lst[0], var[1]))
                    elif var[0] == 'lt':
                        out.append('\tadd_to_global_variable_list = { name = %s target = title:%s }\n' % (lst[0], var[1]))

            out.append('}')

            ff.write(''.join(out))

        provs = []
        
        start = t.find('\nprovinces={')
        end = t.find('\nlanded_titles={', start)

        for province in parse_block(t[start:end])[0][2]:
            foo = (province[0], [], [])

            for entry in province[2]:
                if entry[0] == 'variables':
                    for entry in entry[2]:
                        if entry[0] == 'data':
                            for var in entry[2]:
                                if var[2][2]:
                                    if len(var[2][2]) >= 2:
                                        foo[1].append((var[0][2].strip('"'), var[2][2][0][2], var[2][2][1][2]))
                                    else:
                                        foo[1].append((var[0][2].strip('"'), var[2][2][0][2], 0))
                                else:
                                    foo[1].append((var[0][2].strip('"')))
                        elif entry[0] == 'list':
                            for lst in entry[2]:
                                foofoo = (lst[0][2].strip('"'), [])

                                for var in lst[1:]:
                                    foofoo[1].append((var[2][0][2], var[2][1][2]))

                                foo[2].append(foofoo)
                    break

            provs.append(foo)

        with open('common\\scripted_effects\\00_sim_prov.txt', 'w', encoding='utf-8-sig') as ff:
            out = ['sim_prov = {\n']

            for data in provs:
                foo = []

                for var in data[1]:
                    if type(var) == type(tuple()):
                        if var[1] == 'value':
                            if int(var[2]) / 1000 > 210000:
                                foo.append('set_variable = { name = %s value = 0 } ' % var[0])
                            else:
                                foo.append('set_variable = { name = %s value = %s } ' % (var[0], round(int(var[2]) / 1000, 3)))
                        elif var[1] == 'char':
                            foo.append('set_variable = { name = %s value = character:%s } ' % (var[0], chars[var[2]][0]))
                        elif var[1] == 'prov':
                            foo.append('set_variable = { name = %s value = province:%s } ' % (var[0], var[2]))
                        elif var[1] == 'boolean':
                            foo.append('set_variable = { name = %s } ' % var[0])
                        elif var[1] == 'lt':
                            foo.append('set_variable = { name = %s value = title:%s } ' % (var[0], var[2]))
                    else:
                        foo.append('set_variable = { name = %s } ' % var)
                for lst in data[2]:
                    for var in lst[1]:
                        if var[0] == 'char':
                            foo.append('add_to_variable_list = { name = %s target = character:%s } ' % (lst[0], chars[var[1]][0]))
                        elif var[0] == 'prov':
                            foo.append('add_to_variable_list = { name = %s target = province:%s } ' % (lst[0], var[1]))
                        elif var[0] == 'lt':
                            foo.append('add_to_variable_list = { name = %s target = title:%s } ' % (lst[0], var[1]))

                out.append('\tprovince:%s = { %s}\n' % (data[0], ''.join(foo)))

            out.append('}')
            
            ff.write(''.join(out))

        titles = []
        
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

            foo = (name, [], [])

            for entry in title[2]:
                if entry[0] == 'variables':
                    for entry in entry[2]:
                        if entry[0] == 'data':
                            for var in entry[2]:
                                if var[2][2]:
                                    if len(var[2][2]) >= 2:
                                        foo[1].append((var[0][2].strip('"'), var[2][2][0][2], var[2][2][1][2]))
                                    else:
                                        foo[1].append((var[0][2].strip('"'), var[2][2][0][2], 0))
                                else:
                                    foo[1].append((var[0][2].strip('"')))
                        elif entry[0] == 'list':
                            for lst in entry[2]:
                                foofoo = (lst[0][2].strip('"'), [])

                                for var in lst[1:]:
                                    foofoo[1].append((var[2][0][2], var[2][1][2]))

                                foo[2].append(foofoo)
                    break

            titles.append(foo)

        with open('common\\scripted_effects\\00_sim_titles.txt', 'w', encoding='utf-8-sig') as ff:
            out = ['sim_titles = {\n']

            for data in titles:
                foo = []

                for var in data[1]:
                    if type(var) == type(tuple()):
                        if var[1] == 'value':
                            if int(var[2]) / 1000 > 210000:
                                foo.append('set_variable = { name = %s value = 0 } ' % var[0])
                            else:
                                foo.append('set_variable = { name = %s value = %s } ' % (var[0], round(int(var[2]) / 1000, 3)))
                        elif var[1] == 'char':
                            foo.append('set_variable = { name = %s value = character:%s } ' % (var[0], chars[var[2]][0]))
                        elif var[1] == 'prov':
                            foo.append('set_variable = { name = %s value = province:%s } ' % (var[0], var[2]))
                        elif var[1] == 'boolean':
                            foo.append('set_variable = { name = %s } ' % var[0])
                        elif var[1] == 'lt':
                            foo.append('set_variable = { name = %s value = title:%s } ' % (var[0], var[2]))
                    else:
                        foo.append('set_variable = { name = %s } ' % var)
                for lst in data[2]:
                    for var in lst[1]:
                        if var[0] == 'char':
                            foo.append('add_to_variable_list = { name = %s target = character:%s } ' % (lst[0], chars[var[1]][0]))
                        elif var[0] == 'prov':
                            foo.append('add_to_variable_list = { name = %s target = province:%s } ' % (lst[0], var[1]))
                        elif var[0] == 'lt':
                            foo.append('add_to_variable_list = { name = %s target = title:%s } ' % (lst[0], var[1]))

                out.append('\ttitle:%s = { %s}\n' % (data[0], ''.join(foo)))

            out.append('}')
            
            ff.write(''.join(out))
