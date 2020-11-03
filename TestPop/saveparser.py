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
    names = ['prod_templates', 'prod_instances', 'trade_merchants', 'tech_techs', 'tech_eras', 'build_templates', 'build_slots_active', 'build_slots']
    
    with open('gamestate', encoding='utf-8-sig') as f:
        t = f.read()

        glob_vars = []
        glob_lists = []

        print('Parsing Globals')

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

        i = 100000

        for lst in glob_lists:
            if lst[0] in names:
                for var in lst[1]:
                    if not var[1] in chars:
                        chars[var[1]] = (i, [], [], [])
                        i += 1

        print('Parsing Chars')
        
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

        print('Parsing Provs')
        
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

        print('Parsing Titles')
        
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

        print('Writing Events')
        
        event = '''save_data.0%s = {
	type = empty
	hidden = yes
	
	immediate = { 
%s
	}
	
	option = {
            trigger_event = {
                id = save_data.0%s
            }
	}
}
'''
        arhat = '\t\tcharacter:999999 = { set_global_variable = { name = arhat value = this } every_courtier_or_guest = { limit = { is_character = yes } death = natural } every_councillor = { limit = { is_character = yes } death = natural } }'
        create_character = '\t\tcreate_character = { save_scope_as = save_data_char_%s gender = male trait = character_not_1 employer = global_var:arhat faith = global_var:arhat.faith culture = global_var:arhat.culture dynasty = none }\n'

        def helper(form, var, chars):
            if type(var) == type(tuple()):
                if var[1] == 'value':
                    if int(var[2]) / 1000 > 210000:
                        return '%s = { name = %s %s = 0 }\n' % (form[0], var[0], form[1])
                    else:
                        return '%s = { name = %s %s = %s }\n' % (form[0], var[0], form[1], round(int(var[2]) / 1000, 3))
                elif var[1] == 'char' and var[2] in chars:
                    return '%s = { name = %s %s = scope:save_data_char_%s }\n' % (form[0], var[0], form[1], var[2])
                elif var[1] == 'prov':
                    return '%s = { name = %s %s = province:%s }\n' % (form[0], var[0], form[1], var[2])
                elif var[1] == 'boolean':
                    return '%s = { name = %s }\n' % (form[0], var[0])
                elif var[1] == 'lt':
                    return '%s = { name = %s %s = title:%s }\n' % (form[0], var[0], form[1], var[2])
            else:
                return '%s = { name = %s }\n' % (form[0], var)
        
        with open('events\\save_data.txt', 'w', encoding='utf-8-sig') as ff:
            print('Writing Arhat Event')
            
            out = ['namespace = save_data\n\n', event % (1, arhat, 2)]

            print('Writing Char Creation Event')

            out.append(event % (2, ''.join([create_character % char for char in chars]), 3))

            print('Writing Char Data Event')

            outout = []

            for char, data in chars.items():
                outout.append('\t\tscope:save_data_char_%s = {\n' % char)

                for var in data[1]:
                    outout.append(helper(('\t\t\tset_variable', 'value'), var, chars))
                for lst in data[2]:
                    for var in lst[1]:
                        outout.append(helper(('\t\t\tadd_to_variable_list', 'target'), (lst[0], var[0], var[1]), chars))

                outout.append('\t\t}\n')

            out.append(event % (3, ''.join([item for item in outout if item]), 4))

            print('Writing Global Data Event')

            outout = []

            for var in glob_vars:
                outout.append(helper(('\t\tset_global_variable', 'value'), var, chars))
            for lst in glob_lists:
                for var in lst[1]:
                    outout.append(helper(('\t\tadd_to_global_variable_list', 'target'), (lst[0], var[0], var[1]), chars))
                    
            out.append(event % (4, ''.join([item for item in outout if item]), 5))

            print('Writing Prov Data Event')

            outout = []

            for data in provs:
                outout.append('\t\tprovince:%s = {\n' % data[0])

                for var in data[1]:
                    outout.append(helper(('\t\t\tset_variable', 'value'), var, chars))
                for lst in data[2]:
                    for var in lst[1]:
                        outout.append(helper(('\t\t\tadd_to_variable_list', 'target'), (lst[0], var[0], var[1]), chars))

                outout.append('\t\t}\n')

            out.append(event % (5, ''.join([item for item in outout if item]), 6))

            print('Writing Title Data Event')

            outout = []

            for data in titles:
                outout.append('\t\ttitle:%s = {\n' % data[0])

                for var in data[1]:
                    outout.append(helper(('\t\t\tset_variable', 'value'), var, chars))
                for lst in data[2]:
                    for var in lst[1]:
                        outout.append(helper(('\t\t\tadd_to_variable_list', 'target'), (lst[0], var[0], var[1]), chars))

                outout.append('\t\t}\n')

            out.append(event % (5, ''.join([item for item in outout if item]), 6))

            print('Parsing and Reconstructing the Events')

            out[1] = reconstruct(parse_block(out[1]))
            out[2] = reconstruct(parse_block(out[2]))

            print('Joining the Events')
            
            ff.write(''.join(out))
