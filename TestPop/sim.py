import re

def parse_block(block):
    block = re.sub('\#.*\".*?\".*', '', block)
    strings = re.findall('\".*?\"', block)
    block = re.sub('\".*?\"', ' %s ', block)
    block = re.sub('#.*', '\n', block)
    block = re.sub('(\[\[[\w&$]*\]|\^\^[\w&$]*\^|[\>\<\!\=]+|[\{\}\]^])', r' \1 ', block)
    block = block.strip()

    if block:
        block = re.split('\s+', block)

        if strings:
            i = 0

            for ii in range(len(block)):
                if block[ii] == '%s':
                    block[ii] = strings[i]

                    i += 1

        return block
    else:
        return []

def parse_file(path):
    with open(path, encoding='utf-8-sig') as f:
        file = list()
        stack = [file]
        rhs = False
    
        for token in parse_block(f.read()):
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

def parse_file_block(block):
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

def apply_macro(file, macros, check=[False]):
    out = list()
    
    for f in file:
        if f and type(f) == type(list()):
            if f[0].count('^') == 2:
                check[0] = True
                
                name = f[0][1:-1]

                for foo in [expand_macro(f[1], f'&{name}&', item) for item in macros[name]]:
                    out.extend(foo)
            else:
                out.append(apply_macro(f, macros, check))
        else:
            out.append(f)

    return out

def expand_macro(content, name, item):
    out = list()

    for c in content:
        if type(c) == type(list()):
            out.append(expand_macro(c, name, item))
        else:
            out.append(c.replace(name, item))

    return out
                        
def apply_script(file, scripts, check=[False]):
    out = list()

    for f in file:
        if f[0] in scripts:
            check[0] = True
            
            if f[2] == 'yes':
                out.extend(apply_paras(scripts[f[0]], []))
            elif f[2] == 'no':
                out.append(['NOT', '=', apply_paras(scripts[f[0]], [])])
            else:
                out.extend(apply_paras(scripts[f[0]], f[2]))
        elif type(f[2]) != type(list()) or not f[2] or type(f[2][0]) != type(list()):
            out.append(f)
        else:
            out.append([f[0], f[1], apply_script(f[2], scripts, check)])
            
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
    import glob

    scripts = dict()
    macros = dict()

    for path in glob.glob('common\\scripted_effects\\*.txt'):
        file = parse_file(path)

        for script in file:
            scripts[script[0]] = script[2]
    for path in glob.glob('macro\\*.txt'):
        file = parse_file(path)

        for macro in file:
            macros[macro[0]] = macro[2]

    check = [True]

    while check[0]:
        check[0] = False

        for name, script in scripts.items():
            scripts[name] = apply_macro(script, macros, check)

    with open('events\\sim.txt', 'w', encoding='utf-8-sig') as ff:
        event = '''namespace = sim_run

sim_run.01 = {
	type = empty
	hidden = yes
	
	immediate = {
		character:999999 = {
			set_global_variable = { name = arhat value = this }
			
			every_courtier_or_guest = {
				limit = {
					is_character = yes
				}
				death = natural
			}
			every_councillor = {
				limit = {
					is_character = yes
				}
				death = natural
			}

			init_main = yes
		}
	}
	
	option = {
            trigger_event = {
                id = sim_run.02
            }
	}
}
sim_run.02 = {
	type = empty
	hidden = yes
	
	immediate = {
		set_global_variable = { name = sim_i value = 0 }

		while = {
			count = 300
			
			global_var:arhat = {
				change_global_variable = { name = sim_i add = 1 }
				
				trigger_event = { id = census.01 }
				trigger_event = { id = census.02 }
				
				if = {
					limit = {
						global_var:sim_i > 50
					}
					every_in_global_list = {
						limit = {
							OR = {
								NOT = {
									has_variable = prod_size
								}
								
								var:prod_size < 0.1
							}
						}
						variable = prod_instances
						
						prod_pop_instance = yes
					}
					every_in_global_list = {
						limit = {
							OR = {
								NOT = {
									has_variable = trade_power
								}
								
								var:trade_power < 10
							}
						}
						variable = trade_merchants	
						
						trade_pop_merchant = yes
					}
				}
				
				trigger_event = { id = census.03 }
				
				every_province = {
					limit = {
						is_valid_prov = yes
					}
					if = {
						limit = {
							has_variable = farm_potential
							
							var:farm_potential >= 1
						}
						set_variable = { name = sim_t value = var:farm_potential }
						change_variable = { name = sim_t divide = 5 }
						
						build_start_project = {
							name = farm
							size = var:farm_potential
							para = var:sim_t
							owner = 2
						}
						
						set_variable = { name = farm_potential value = 0 }
					}
					if = {
						limit = {
							has_variable = pasture_potential
							
							var:pasture_potential >= 1
						}
						set_variable = { name = sim_t value = var:pasture_potential }
						change_variable = { name = sim_t divide = 5 }
						
						build_start_project = {
							name = pasture
							size = var:pasture_potential
							para = var:sim_t
							owner = 2
						}
						
						set_variable = { name = pasture_potential value = 0 }
					}
				}
				
				trigger_event = { id = census.04 }
				trigger_event = { id = census.05 }
				trigger_event = { id = census.06 }
				trigger_event = { id = census.07 }
				trigger_event = { id = census.08 }
				trigger_event = { id = census.09 }
				trigger_event = { id = census.10 }
				trigger_event = { id = census.11 }

				every_ruler = {
					limit = {
						is_character = yes
						is_landed = yes
					}
					set_variable = { name = sim_income value = 0 }
				}
				
				every_province = {
					limit = {
						is_valid_prov = yes
					}
					change_variable = { name = pop_wealth add = var:pop_earn_free } 
					change_variable = { name = pop_wealth subtract = var:pop_pay_free }

					if = {
						limit = {
							is_city = yes
						}
						province_owner = {
							if = {
								limit = {
									is_character = yes
									is_ruler = yes
									is_landed = yes
									has_variable = sim_income
								}
								change_variable = { name = sim_income add = prev.var:pop_earn_serf }
								change_variable = { name = sim_income add = prev.var:pop_pay_serf }
							}
							else = {
								prev = {
									change_variable = { name = pop_wealth add = var:pop_earn_serf }
									change_variable = { name = pop_wealth subtract = var:pop_pay_serf }
								}
							}
						}
					}
					else = {
						change_variable = { name = pop_wealth add = var:pop_earn_serf }
						change_variable = { name = pop_wealth subtract = var:pop_pay_serf }
					}
				}

				every_ruler = {
					limit = {
						is_character = yes
						is_landed = yes
					}
					set_variable = { name = sim_balance value = var:sim_income }
					change_variable = { name = sim_balance add = var:trade_earn }
					change_variable = { name = sim_balance subtract = var:trade_pay }
					
					if = {
						limit = {
							has_variable = sim_balance
							
							var:sim_balance > 0
						}
						eff_binary_1_16 = { name = sim_balance eff = add_gold }
					}
					else = {
						change_variable = { name = sim_balance multiply = -1 }
						
						eff_binary_1_16 = { name = sim_balance eff = remove_short_term_gold }
					}

					remove_variable = sim_balance
				}
				set_variable = { name = t_disp value = global_var:sim_i }
				
				debug_log = "Logging Start: [THIS.Var('t_disp').GetValue]"
				
				set_variable = { name = t_disp value = 0 }

				every_province = {
					limit = {
						is_valid_prov = yes
					}
					prev = {
						set_variable = { name = t_disp_t value = prev.var:pop_wealth }
						change_variable = { name = t_disp_t divide = 100 }
						change_variable = { name = t_disp add = var:t_disp_t }
					}
				}
				every_in_global_list = {
					variable = trade_merchants
					
					prev = {
						set_variable = { name = t_disp_t value = prev.var:trade_wealth }
						change_variable = { name = t_disp_t divide = 100 }
						change_variable = { name = t_disp add = var:t_disp_t }
					}
				}

				debug_log = "Total Wealth: [THIS.Var('t_disp').GetValue]"

				set_variable = { name = t_disp_s value = 0 }

				every_province = {
					limit = {
						is_valid_prov = yes
					}
					prev = {
						set_variable = { name = t_disp_t value = prev.var:pop_total }
						change_variable = { name = t_disp_t divide = 100 }
						change_variable = { name = t_disp_s add = var:t_disp_t }
					}
				}

				set_variable = { name = t_disp value = 0 }

				every_province = {
					limit = {
						is_valid_prov = yes
					}
					prev = {
						set_variable = { name = t_disp_t value = prev.var:pop_calorie }
						change_variable = { name = t_disp_t multiply = prev.var:pop_total }
						change_variable = { name = t_disp_t divide = 100 }
						change_variable = { name = t_disp add = var:t_disp_t }
					}
				}

				change_variable = { name = t_disp divide = var:t_disp_s }

				debug_log = "Average Calorie: [THIS.Var('t_disp').GetValue]"

				set_variable = { name = t_disp value = 0 }

				every_province = {
					limit = {
						is_valid_prov = yes
					}
					prev = {
						set_variable = { name = t_disp_t value = prev.var:pop_nutrient }
						change_variable = { name = t_disp_t multiply = prev.var:pop_total }
						change_variable = { name = t_disp_t divide = 100 }
						change_variable = { name = t_disp add = var:t_disp_t }
					}
				}

				change_variable = { name = t_disp divide = var:t_disp_s }

				debug_log = "Average Nutrient: [THIS.Var('t_disp').GetValue]"

				set_variable = { name = t_disp value = 0 }

				every_province = {
					limit = {
						is_valid_prov = yes
					}
					prev = {
						set_variable = { name = t_disp_t value = prev.var:pop_comfort }
						change_variable = { name = t_disp_t multiply = prev.var:pop_total }
						change_variable = { name = t_disp_t divide = 100 }
						change_variable = { name = t_disp add = var:t_disp_t }
					}
				}

				change_variable = { name = t_disp divide = var:t_disp_s }

				debug_log = "Average Comfort: [THIS.Var('t_disp').GetValue]"

				set_variable = { name = t_disp value = 0 }

				every_province = {
					limit = {
						is_valid_prov = yes
					}
					prev = {
						set_variable = { name = t_disp_t value = prev.var:pop_luxury }
						change_variable = { name = t_disp_t multiply = prev.var:pop_total }
						change_variable = { name = t_disp_t divide = 100 }
						change_variable = { name = t_disp add = var:t_disp_t }
					}
				}

				change_variable = { name = t_disp divide = var:t_disp_s }

				debug_log = "Average Luxury: [THIS.Var('t_disp').GetValue]"
				
				set_variable = { name = t_disp value = 0 }

				every_province = {
					limit = {
						is_valid_prov = yes
					}
					prev = {
						set_variable = { name = t_disp_t value = prev.var:forest_base }
						change_variable = { name = t_disp_t divide = 1000 }
						change_variable = { name = t_disp add = var:t_disp_t }
					}
				}

				debug_log = "Total Forest: [THIS.Var('t_disp').GetValue]"
				
				set_variable = { name = t_disp value = 0 }

				every_province = {
					limit = {
						is_valid_prov = yes
					}
					prev = {
						set_variable = { name = t_disp_t value = prev.var:forest_total }
						change_variable = { name = t_disp_t divide = 1000 }
						change_variable = { name = t_disp add = var:t_disp_t }
					}
				}

				debug_log = "Effective Forest: [THIS.Var('t_disp').GetValue]"

				^^goods^
					set_variable = { name = t_disp value = 0 }

					every_province = {
						limit = {
							is_valid_prov = yes
						}
						prev = {
							set_variable = { name = t_disp_t value = prev.county.var:trade_price_&goods& }
							change_variable = { name = t_disp_t multiply = prev.var:pop_total }
							change_variable = { name = t_disp_t divide = 100 }
							change_variable = { name = t_disp add = var:t_disp_t }
						}
					}
					
					change_variable = { name = t_disp divide = var:t_disp_s }
					
					debug_log = "Average &goods& Price: [THIS.Var('t_disp').GetValue]"
					
					set_variable = { name = t_disp value = 0 }

					every_province = {
						limit = {
							is_valid_prov = yes
							
							has_variable = prod_has_&goods&
						}
						prev = {
							set_variable = { name = t_disp_t value = prev.var:prod_has_&goods& }
							change_variable = { name = t_disp_t divide = 100 }
							change_variable = { name = t_disp add = var:t_disp_t }
						}
					}
					every_in_global_list = {
						limit = {
							has_variable = trade_has_&goods&
						}
						variable = trade_merchants
						prev = {
							set_variable = { name = t_disp_t value = prev.var:trade_has_&goods& }
							change_variable = { name = t_disp_t divide = 100 }
							change_variable = { name = t_disp add = var:t_disp_t }
						}
					}
					
					debug_log = "Total &goods& Stockpile: [THIS.Var('t_disp').GetValue]"
					
					set_variable = { name = t_disp value = 0 }

					every_county = {
						limit = {
							is_valid_prov = yes
							
							has_variable = trade_sum_sply_&goods&
						}
						prev = {
							set_variable = { name = t_disp_t value = prev.var:trade_sum_sply_&goods& }
							change_variable = { name = t_disp_t divide = 400 }
							change_variable = { name = t_disp add = var:t_disp_t }
						}
					}
					
					debug_log = "Total &goods& Supply: [THIS.Var('t_disp').GetValue]"
					
					set_variable = { name = t_disp value = 0 }

					every_county = {
						limit = {
							is_valid_prov = yes
							
							has_variable = trade_dmnd_&goods&
						}
						prev = {
							set_variable = { name = t_disp_t value = prev.var:trade_dmnd_&goods& }
							change_variable = { name = t_disp_t divide = 100 }
							change_variable = { name = t_disp add = var:t_disp_t }
						}
					}
					every_ruler = {
						limit = {
							is_character = yes
							is_landed = yes
						}
						prev = {
							set_variable = { name = t_disp_t value = prev.var:trade_dmnd_&goods& }
							change_variable = { name = t_disp_t divide = 100 }
							change_variable = { name = t_disp add = var:t_disp_t }
						}
					}
					
					debug_log = "Total &goods& Demand: [THIS.Var('t_disp').GetValue]"
					
					set_variable = { name = t_disp value = 0 }

					every_province = {
						limit = {
							is_valid_prov = yes
							
							has_variable = prod_earn_&goods&
						}
						prev = {
							set_variable = { name = t_disp_t value = prev.var:prod_earn_&goods& }
							change_variable = { name = t_disp_t divide = 100 }
							change_variable = { name = t_disp add = var:t_disp_t }
						}
					}
					
					debug_log = "Total &goods& Revenue: [THIS.Var('t_disp').GetValue]"
				^

				set_variable = { name = t_disp value = global_var:sim_i }
				
				debug_log = "Logging End: [THIS.Var('t_disp').GetValue]"
				
				remove_variable = t_disp
				remove_variable = t_disp_t
			}
		}
		
		every_ruler = {
			limit = {
				is_character = yes
				is_landed = yes
			}
			set_variable = { name = sim_income value = 1 }
			
			^^goods^
				every_in_list = {
					variable = trade_dat_&goods&
					
					prev.capital_province = {
						add_to_variable_list = { name = trade_dat_&goods& target = prev }
					}
				}
				every_in_list = {
					variable = array_trade_dat_&goods&
					
					prev.capital_province = {
						add_to_variable_list = { name = array_trade_dat_&goods& target = prev }
					}
				}
				
				capital_province = {
					set_variable = { name = trade_in_&goods& value = prev.var:trade_in_&goods& }
					set_variable = { name = trade_out_&goods& value = prev.var:trade_out_&goods& }
					set_variable = { name = trade_earn_&goods& value = prev.var:trade_earn_&goods& }
					set_variable = { name = trade_pay_&goods& value = prev.var:trade_pay_&goods& }
					set_variable = { name = trade_sply_&goods& value = prev.var:trade_sply_&goods& }
					set_variable = { name = trade_dmnd_&goods& value = prev.var:trade_dmnd_&goods& }
					set_variable = { name = trade_price_&goods& value = prev.var:trade_price_&goods& }
					set_variable = { name = trade_gold value = prev.gold }
					set_variable = { name = trade_maa value = prev.var:mil_maa }
					set_variable = { name = trade_maintain value = prev.var:mil_maintain }
				}
				
				clear_variable_list = trade_dat_&goods&
				array_clear = { name = trade_dat_&goods& }
			^
		}
		
		every_in_global_list = {
			variable = trade_merchants
			
			^^goods^
				set_global_variable = { name = sim_t value = 0 }
				
				every_in_list = {
					variable = trade_dat_&goods&
					
					if = {
						limit = {
							has_variable = sim_income
						}
						prev = {
							remove_list_variable = { name = trade_dat_&goods& target = prev }
							add_to_variable_list = { name = trade_dat_&goods& target = prev.capital_province }
							
							ordered_in_list = {
								variable = array_trade_dat_&goods&
								position = global_var:sim_t
								
								prev = {
									remove_list_variable = { name = array_trade_dat_&goods& target = prev }
									add_to_variable_list = { name = array_trade_dat_&goods& target = prev }
								}
							}
						}
					}
					else = {
						change_global_variable = { name = sim_t add = 1 }
					}
				}
			^
			
			remove_global_variable = sim_t
		}
		
		every_ruler = {
			limit = {
				is_character = yes
				is_landed = yes
			}
			remove_variable = sim_income
		}
		
		remove_global_variable = sim_i
	}
	
	option = {
	}
}'''
                        
        file = apply_macro(parse_file_block(event), macros)
        
        check = [True]

        while check[0]:
            check[0] = False

            file = apply_script(file, scripts, check)
            
        ff.write(reconstruct(file))
