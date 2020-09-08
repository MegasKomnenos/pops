from PIL import Image

if __name__ == '__main__':
    density = {
        (255, 255, 255): 10,
        (156, 255, 255): 50,
        (156, 255, 207): 150,
        (156, 255, 156): 300,
        (207, 255, 156): 600,
        (255, 255, 156): 1200,
        (255, 207, 156): 2400,
        (255, 156, 156): 3600
    }

    rgb = dict()

    with open('map_data\\definition.csv', 'rb') as f:
        for line in f.readlines()[1:]:
            line = line.decode("latin-1")
            line = line[:line.find('#')]
            line = line.split(';')

            if len(line) >= 4:
                rgb[line[0]] = (int(line[1]), int(line[2]), int(line[3]))
                
    rgb_rev = dict([(v, k) for k, v in rgb.items()])

    weight = dict()

    prov = Image.open('test1.png')
    pop = Image.open('test3.png')

    for y in range(prov.height):
        print(y)
        for x in range(prov.width):
            pxl = prov.getpixel((x, y))[:3]

            if rgb_rev[pxl] in weight:
                weight[rgb_rev[pxl]] += density[pop.getpixel((x, y))[:3]]
            else:
                weight[rgb_rev[pxl]] = density[pop.getpixel((x, y))[:3]]

    loc = ''

    for prov, weight in weight.items():
        loc += '\n\t\tprovince:%s = { set_variable = { name = pop_weight value = %s } }' % (prov, weight / 10000)

    t = '''namespace = pop_weight

pop_weight.0001 = {
    hidden = yes

    fire_only_once = yes

    immediate = {%s   
    }

    option = {
    }
}''' % loc

    with open('events\\pop_weight.txt', 'w') as f:
        f.write(t)
