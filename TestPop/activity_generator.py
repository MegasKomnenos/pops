import json

if __name__ == '__main__':
    template_open = '''prod_open_%s = {
    if = {
        limit = {
%s        }
        set_variable = { name = prod_s$slot$ value = %s }
        set_variable = { name = prod_s$slot$_size value = 1 }%s%s%s
    }
}
'''
    template_up = '''prod_up_%s = {
    if = {
        limit = {
%s        }
        change_variable = { name = prod_s$slot$_size add = 1 }%s%s%s
    }
}
'''
    template_down = '''prod_down_%s = {
    if = {
        limit = {
            var:prod_s$slot$ = %s
            var:prod_s$slot$_size >= 1
        }
        change_variable = { name = prod_s$slot$_size subtract = 1 }

        if = {
            limit = {
                var:prod_s$slot$_size < 1
            }
            remove_variable = prod_s$slot$
            remove_variable = prod_s$slot$_size
        }%s%s%s
    }
}
'''
    template_sv = '''prod_next_%s_%s = {
    value = var:%s_usage_base%s
}
'''
    
    acts = json.load(open('activities.json'))

    effects = ''
    svs = ''

    for act in acts:
        name = act['name']
        idn = act['id']
        
        trigger = '\t\t\talways = yes\n'
        uses = ''
        sply = ''
        dmnd = ''
        
        if 'uses' in act:
            trigger = ''
            
            for k, v in act['uses'].items():
                svs += template_sv % (name, k, k, f'\n\tadd = {v}\n\tmultiply = var:{k}_usage_mult')
                trigger += f'\t\t\tvar:{k}_total >= prod_next_{name}_{k}\n'
                uses += '\n\t\tchange_variable = { name = %s_usage_base foo = %s }' % (k, v)
        if 'sply' in act:
            for k, v in act['sply'].items():
                sply += '\n\t\tchange_variable = { name = %s_sply_base foo = %s }' % (k, v)
        if 'dmnd' in act:
            for k, v in act['dmnd'].items():
                sply += '\n\t\tchange_variable = { name = %s_dmnd_base foo = %s }' % (k, v)

        effects += template_open % (name, trigger, idn, uses.replace(' foo ', ' add '), sply.replace(' foo ', ' add '), dmnd.replace(' foo ', ' add '))
        effects += template_up % (name, trigger, uses.replace(' foo ', ' add '), sply.replace(' foo ', ' add '), dmnd.replace(' foo ', ' add '))
        effects += template_down % (name, idn, uses.replace(' foo ', ' subtract '), sply.replace(' foo ', ' subtract '), dmnd.replace(' foo ', ' subtract '))

    with open('activity_effects.txt', 'w') as f:
        f.write(effects)
    with open('activity_svs.txt', 'w') as f:
        f.write(svs)
