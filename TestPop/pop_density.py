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
    score_cereal = {
        (0, 0, 0): 100,
        (9, 32, 237): 100,
        (224, 224, 224): 0,
        (158, 158, 158): 10,
        (255, 255, 191): 20,
        (255, 174, 0): 35,
        (255, 102, 0): 50,
        (169, 255, 115): 65,
        (77, 209, 0): 80,
        (38, 115, 0): 100,
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
    farm = dict()

    prov = Image.open('provinces_ref.png')
    pop = Image.open('Map_new_ref.png')
    cereal = Image.open('cereal_ref.png')

    for y in range(prov.height):
        print(y)
        for x in range(prov.width):
            pxl = prov.getpixel((x, y))[:3]

            if rgb_rev[pxl] in weight:
                weight[rgb_rev[pxl]] += density[pop.getpixel((x, y))[:3]]

                if cereal.getpixel((x, y))[:3] in score_cereal:
                    farm[rgb_rev[pxl]][0] += score_cereal[cereal.getpixel((x, y))[:3]]
                    farm[rgb_rev[pxl]][1] += 1
            else:
                weight[rgb_rev[pxl]] = density[pop.getpixel((x, y))[:3]]

                if cereal.getpixel((x, y))[:3] in score_cereal:
                    farm[rgb_rev[pxl]] = [score_cereal[cereal.getpixel((x, y))[:3]], 1]
                else:
                    farm[rgb_rev[pxl]] = [50, 1]

    loc = ''

    for prov, weight in weight.items():
        loc += 'province:%s = { set_variable = { name = pop_weight value = %s } }\n' % (prov, weight / 10000)

    with open('pop_weight.txt', 'w') as f:
        f.write(loc)

    loc = ''

    for prov, pair in farm.items():
        loc += 'province:%s = { set_variable = { name = farm_score value = %s } }\n' % (prov, round(pair[0] / pair[1], 3))

    with open('farm_score.txt', 'w') as f:
        f.write(loc)
