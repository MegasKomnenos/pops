import json

def btree(lst, form, body):
    if not len(lst):
        return ''
    elif len(lst) == 1:
        return body % lst[0][0]
    else:
        return form % (lst[int(len(lst)/2)][1],
                       btree(lst[int(len(lst)/2):], form.replace('\n', '\n\t'), body),
                       btree(lst[:int(len(lst)/2)], form.replace('\n', '\n\t'), body))

def repeat_str(lst, tmplt):
    out = ''

    for paras in lst:
        if type(paras) == type(list()):
            out += tmplt % tuple(paras)
        else:
            out += tmplt % paras

    return out

if __name__ == '__main__':
    tmplt_open = '''prod_open_%s = {
\tset_variable = { name = prod_s$slot$ value = %s }
\tset_variable = { name = prod_s$slot$_size value = 0 }
\tset_variable = { name = prod_s$slot$_pop value = 0 }%s%s%s
}
'''
    tmplt_close = '''prod_close_%s = {
\tremove_variable = prod_s$slot$
\tremove_variable = prod_s$slot$_size
\tremove_variable = prod_s$slot$_pop
\tremove_variable = prod_s$slot$_land%s%s
}
'''
    tmplt_build_start = '''prod_build_start_%s = {
    set_variable = { name = prod_b$slot$_total value = %s }%s
}
'''
    tmplt_build_done = '''prod_build_done_%s = {
    remove_variable = prod_b$slot$_total%s
}
'''
    tmplt_demol_start = '''prod_demol_start_%s = {
    set_variable = { name = prod_b$slot$_total value = %s }%s
}
'''
    tmplt_demol_done = '''prod_demol_done_%s = {
    remove_variable = prod_b$slot$_total%s%s
}
'''

    acts = json.load(open('acts.json'))

    names = []

    for act in acts:
        names.append((act['name'], act['id']))

    names.sort(key=lambda e : e[1])

    cond = 'var:prod_run_eff_by_id_id >= %s'
    body = '$eff$_%s = { $param0$ = $inp0$ [[param1]$param1$ = $inp1$] [[param2]$param2$ = $inp2$] }'
    form = '\tif = {\n\t\tlimit = {\n\t\t\t%s\n\t\t}\n\t\t%s\n\t}\n\telse = {\n\t\t%s\n\t}' % (cond, '%s', '%s')
    
    eff = '''prod_run_eff_by_id = {
\tset_variable = { name = prod_run_eff_by_id_id value = $id$ }
    
%s

\tremove_variable = prod_run_eff_by_id_id
}

''' % btree(names, form, body)

    for act in acts:
        eff += tmplt_open % (act['name'], act['id'], '\n\tset_variable = { name = prod_s$slot$_land value = flag:%s }' % act['land'], repeat_str(act['sply'], '\n\tset_variable = { name = prod_s$slot$_sply_base_%s value = %s }'), repeat_str(act['dmnd'], '\n\tset_variable = { name = prod_s$slot$_dmnd_base_%s value = %s }'))
        eff += tmplt_close % (act['name'], repeat_str([(foo[0], foo[0]) for foo in act['sply']], '\n\tremove_variable = prod_s$slot$_sply_base_%s\n\tremove_variable = prod_s$slot$_sply_%s'), repeat_str([(foo[0], foo[0]) for foo in act['dmnd']], '\n\tremove_variable = prod_s$slot$_dmnd_base_%s\n\tremove_variable = prod_s$slot$_dmnd_%s'))
        eff += tmplt_build_start % (act['name'], sum([foo[1] for foo in act['cost']]), repeat_str(act['cost'], '\n\tset_variable = { name = prod_b$slot$_cost_%s value = %s }'))
        eff += tmplt_build_done % (act['name'], repeat_str([foo[0] for foo in act['cost']], '\n\tremove_variable = prod_b$slot$_cost_%s'))
        eff += tmplt_demol_start % (act['name'], sum([foo[1] for foo in act['demol_cost']]), repeat_str(act['demol_cost'], '\n\tset_variable = { name = prod_b$slot$_cost_%s value = %s }'))
        eff += tmplt_demol_done % (act['name'], repeat_str([foo[0] for foo in act['demol_cost']], '\n\tremove_variable = prod_b$slot$_cost_%s'), repeat_str(act['demol_gain'], '\n\tchange_variable = { name = %s_gain_demol value = %s }'))

    with open('out.txt', 'w') as f:
        f.write(eff)
