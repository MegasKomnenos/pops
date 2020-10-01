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
                    stack.append(stack.pop()[-1])
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

def apply_script(file, scripts):
    out = list()

    for f in file:
        if f[0] in scripts:
            if f[2] == 'yes':
                out.extend(apply_paras(scripts[f[0]], []))
            elif f[2] == 'no':
                out.append(['NOT', apply_paras(scripts[f[0]], [])])
            else:
                out.extend(apply_paras(scripts[f[0]], f[2]))
        elif type(f[2]) != type(list()) or not f[2] or type(f[2][0]) != type(list()):
            out.append(f)
        else:
            out.append([f[0], f[1], apply_script(f[2], scripts)])
            
    return out

def apply_paras(script, paras):
    out = list()

    for section in script:
        if '[' in section[0]:
            for para in paras:
                if section[0][1:-1] == para[0]:
                    out.extend(apply_paras(section[1], paras))

                    break
        else:
            outout = list()
            
            for part in section[:2]:
                if '$' in part:
                    foo = str(part)
                    
                    for para in paras:
                        foo = foo.replace(f'${para[0]}$', para[2])

                    outout.append(foo)
                else:
                    outout.append(part)

            if type(section[2]) != type(list()):
                if '$' in section[2]:
                    foo = str(section[2])
                    
                    for para in paras:
                        foo = foo.replace(f'${para[0]}$', para[2])

                    outout.append(foo)
                else:
                    outout.append(section[2])
            else:
                outout.append(apply_paras(section[2], paras))

            out.append(outout)
                
    return out

def reconstruct(file, t=''):
    txt = ''

    for f in file:
        if f:
            if len(f) == 3 and type(f[0]) != type(list()) and type(f[1]) != type(list()):
                if type(f[2]) == type(list()):
                    txt += '%s%s %s {' % (t, f[0], f[1])

                    if not f[2]:
                        txt += '}\n'
                    elif type(f[2][0]) != type(list()):
                        for item in f[2]:
                            txt += ' %s' % item
                        txt += ' }\n'
                    else:
                        txt += '\n%s%s}\n' % (reconstruct(f[2], t + '\t'), t)
                else:
                    txt += '%s%s %s %s\n' % (t, f[0], f[1], f[2])
            elif len(f) == 2 and type(f[0]) != type(list()):
                txt += '%s[%s\n%s%s]\n' % (t, f[0], reconstruct(f[1], t + '\t'), t)

    return txt
            
            
if __name__ == '__main__':
    file = parse_file('common\\scripted_effects\\01_prod.txt')
    scripts = {block[0]:block[2] for block in file}

    with open('foofoo.txt', 'w') as f:
        f.write(reconstruct(apply_script(parse_file('foo.txt'), scripts)))
