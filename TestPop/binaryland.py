import os

def btree(lst, form, body):
    if not len(lst):
        return ''
    elif len(lst) == 1:
        return body % lst[0]
    else:
        return form % (lst[int(len(lst)/2)],
                       btree(lst[int(len(lst)/2):], form.replace('\n', '\n\t'), body),
                       btree(lst[:int(len(lst)/2)], form.replace('\n', '\n\t'), body))
        
if __name__ == "__main__":
        cond = 'opinion = { value >= %s target = $target$ }'
        body = 'set_variable = { name = $return$ value = %s }'
        form = 'if = {\n\tlimit = {\n\t\t%s\n\t}\n\t%s\n}\nelse = {\n\t%s\n}' % (cond, '%s', '%s')

        with open('output.txt', 'w') as f:
                f.write(btree([i for i in range(-100, 101)], form, body))
