
with open('ccs.txt', 'r', encoding='utf8') as f:
    ccs = f.read().strip().split('\n')

for cc in ccs:

    with open('bot.py', 'r', encoding='utf8') as f:
        code = f.read()

    edit_dict = {
        'cc':'[TARJETA] esto se edita y se ejecuta.',
        'month': '[MES] esto se edita y se ejecuta.',
        'year': '[AÑO] esto se edita y se ejecuta.'
    }
    
    cc_num, month, year = cc.split('|')

    code = code.replace(edit_dict['cc'], cc_num)
    code = code.replace(edit_dict['month'], month)
    code = code.replace(edit_dict['year'], year)
    
    exec(code)