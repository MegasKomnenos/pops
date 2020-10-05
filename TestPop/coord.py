def parse_line(line):
    line = line.strip()
    line = line.replace('\t', ' ')
    line = line.replace('{', ' { ')
    line = line.replace('}', ' } ')
    line = line.replace('[', ' [ ')
    line = line.replace(']', ' ] ')
    line = line.replace('!=', ' != ')
    line = line.replace('=', ' = ')
    line = line.replace('>', ' > ')
    line = line.replace('<', ' < ')

    while '  ' in line:
        line = line.replace('  ', ' ')

    line = line.replace('> =', '>=')
    line = line.replace('< =', '<=')
    line = line.replace('= =', '==')
    line = line.replace('! =', '!=')

    comma = False
    comment = False

    for i, char in enumerate(line):
        if char == '#':
            if not comma:
                line = line[:i]
                
                break
        elif char == '"':
            if comma:
                comma = False
            else:
                comma = True
        elif char == ' ':
            if comma:
                line = line[:i] + '%' + line[i + 1:]

    line = line.strip()

    prev = 0
    
    while True:
        start = line.find('[ [', prev)

        if start + 1:
            end = line.find(']', start)
            block = line[start:end + 1]
            block_new = block.replace(' ', '')
            line = line.replace(block, block_new)
            prev = start + len(block_new)
        else:
            break

    if line:
        tokens = line.split(' ')
        tokens = [token.replace('%', ' ') for token in tokens]

        return tokens
    else:
        return []
    

def parse_file(path):
    with open(path, encoding='utf-8-sig') as f:
        file = list()
        stack = [file]

        for line in f.readlines():
            rhs = False
            
            for token in parse_line(line):
                if token == '=' or token == '>' or token == '<' or token == '>=' or token == '<=' or token == '==' or token == '!=':
                    rhs = True

                    stack[-1][-1] = [stack[-1][-1], token]
                    stack.append(stack[-1][-1])
                elif token == '{':
                    rhs = False
                    
                    stack[-1].append(list())

                    if type(stack[-1][0]) == type(str()):
                        stack.append(stack.pop()[-1])
                    else:
                        stack.append(stack[-1][-1])
                elif token == '}' or token == ']':
                    stack.pop()
                elif '[[' in token:
                    stack[-1].append([token[1:], list()])
                    stack.append(stack[-1][-1][1])
                else:
                    stack[-1].append(token)

                    if rhs:
                        rhs = False

                        stack.pop()

        return file

if __name__ == '__main__':
    file = parse_file('gfx\\map\\map_object_data\\building_locators.txt')

    t = ''

    for entry in file[0][2][5][2]:
        prov_id = entry[0][2]
        prov_x = round(float(entry[1][2][0]), 3)
        prov_y = round(float(entry[1][2][2]), 3)

        t += 'province:%s = { set_variable = { name = prov_x value = %s } set_variable = { name = prov_y value = %s } }\n' % (prov_id, prov_x, prov_y)

    with open('out.txt', 'w') as f:
        f.write(t)

    
