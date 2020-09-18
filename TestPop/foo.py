def btree(lst, form, body):
    if not len(lst):
        return ''
    elif len(lst) == 1:
        return body % lst[0]
    else:
        return form % (lst[int(len(lst)/2)],
                       btree(lst[int(len(lst)/2):], form.replace('\n', '\n\t'), body),
                       btree(lst[:int(len(lst)/2)], form.replace('\n', '\n\t'), body))


cond = 'var:prod_run_eff_by_slot_slot >= %s'
body = '$eff$ = { slot = %s [[param0]$param0$ = $inp0$] [[param1]$param1$ = $inp1$] }'
form = 'if = {\n\tlimit = {\n\t\t%s\n\t}\n\t%s\n}\nelse = {\n\t%s\n}' % (cond, '%s', '%s')

with open('out.txt', 'w') as f:
    f.write(btree([i for i in range(16)], form, body))
