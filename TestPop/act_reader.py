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
\tset_variable = { name = prod_%s value = $slot$ }
\tset_variable = { name = prod_s$slot$ value = %s }
\tset_variable = { name = prod_s$slot$_size value = 0 }
\tset_variable = { name = prod_s$slot$_pop value = 0 }%s%s%s
}
'''
    tmplt_build_start = '''prod_build_start_%s = {
    set_variable = { name = prod_b$slot$_total value = %s }%s
}
'''

    acts = json.load(open('acts.json'))

    names = []

    for act in acts:
        names.append((act['name'], act['id']))

    names.sort(key=lambda e : e[1])

    cond = 'var:prod_run_eff_by_act_act >= %s'
    body = '$eff$ = { act = %s [[param0]$param0$ = $inp0$] [[param1]$param1$ = $inp1$] }'
    form = 'if = {\n\t\tlimit = {\n\t\t\t%s\n\t\t}\n\t\t%s\n\t}\n\telse = {\n\t\t%s\n\t}' % (cond, '%s', '%s')
    
    eff = '''prod_run_eff_by_act = {
\tset_variable = { name = prod_run_eff_by_act_act value = $act$ }
    
\t%s

\tremove_variable = prod_run_eff_by_act_act
}

''' % btree(names, form, body)

    lands = []

    for act in acts:
        if not act['land'] in lands:
            lands.append(act['land'])

    lands_t = [(land, i + 1) for i, land in enumerate(lands)]

    cond = 'var:prod_run_eff_by_land_land >= %s'
    body = '$eff$ = { land = %s [[param0]$param0$ = $inp0$] [[param1]$param1$ = $inp1$] }'
    form = 'if = {\n\t\tlimit = {\n\t\t\t%s\n\t\t}\n\t\t%s\n\t}\n\telse = {\n\t\t%s\n\t}' % (cond, '%s', '%s')
    
    eff += '''prod_run_eff_by_land = {
\tset_variable = { name = prod_run_eff_by_land_land value = $land$ }
    
\t%s

\tremove_variable = prod_run_eff_by_land_land
}

''' % btree(lands_t, form, body)

    goods = []

    for act in acts:
        for good in act['cost']:
            if not good[0] in goods:
                goods.append(good[0])
        for good in act['sply']:
            if not good[0] in goods:
                goods.append(good[0])
        for good in act['dmnd']:
            if not good[0] in goods:
                goods.append(good[0])

    eff += '''prod_iter_goods = {%s
}
''' % repeat_str(goods, '\n\t$eff$ = { good = %s [[param0]$param0$ = $inp0$] [[param1]$param1$ = $inp1$] }')

    for act in acts:
        eff += tmplt_open % (act['name'], act['name'], act['id'], '\n\tset_variable = { name = prod_s$slot$_land value = %s }' % str(lands.index(act['land']) + 1), repeat_str(act['sply'], '\n\tset_variable = { name = prod_s$slot$_sply_base_%s value = %s }'), repeat_str(act['dmnd'], '\n\tset_variable = { name = prod_s$slot$_dmnd_base_%s value = %s }'))
        eff += tmplt_build_start % (act['name'], sum([foo[1] for foo in act['cost']]), repeat_str(act['cost'], '\n\tset_variable = { name = prod_b$slot$_cost_%s value = %s }'))
        
    with open('out.txt', 'w') as f:
        f.write(eff)
