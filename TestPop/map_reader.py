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
    pasture = dict()
    forest = dict()

    prov = Image.open('provinces_ref.png')
    pop = Image.open('Map_new_ref.png')
    cereal = Image.open('cereal_ref.png')
    livestock = Image.open('Pasture_new_ref.png')
    tree = Image.open('Forest_new_ref.png')

    for y in range(prov.height):
        print(y)
        for x in range(prov.width):
            pxl = prov.getpixel((x, y))[:3]
            p = rgb_rev[pxl]

            if p in weight:
                weight[p] += density[pop.getpixel((x, y))[:3]]

                if cereal.getpixel((x, y))[:3] in score_cereal:
                    farm[p][0] += score_cereal[cereal.getpixel((x, y))[:3]]
                    farm[p][1] += 1

                pasture[p][0] += livestock.getpixel((x, y))[0] / 2.55
                pasture[p][1] += 1

                forest[p][0] += max(150 - tree.getpixel((x, y))[0], 0) / 1.5
                forest[p][1] += 1
            else:
                weight[p] = density[pop.getpixel((x, y))[:3]]

                if cereal.getpixel((x, y))[:3] in score_cereal:
                    farm[p] = [score_cereal[cereal.getpixel((x, y))[:3]], 1]
                else:
                    farm[p] = [50, 1]

                pasture[p] = [livestock.getpixel((x, y))[0] / 2.55, 1]
                forest[p] = [max(150 - tree.getpixel((x, y))[0], 0) / 1.5, 1]

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

    loc = ''

    for prov, pair in pasture.items():
        loc += 'province:%s = { set_variable = { name = pasture_score value = %s } }\n' % (prov, round(pair[0] / pair[1], 3))

    with open('pasture_score.txt', 'w') as f:
        f.write(loc)

    loc = ''

    for prov, pair in forest.items():
        loc += 'province:%s = { set_variable = { name = forest_score value = %s } }\n' % (prov, round(pair[0] / pair[1], 3))

    with open('forest_score.txt', 'w') as f:
        f.write(loc)

    size = dict()

    prov = Image.open('map_data\\provinces.png')

    for y in range(prov.height):
        print(y)
        for x in range(prov.width):
            pxl = prov.getpixel((x, y))[:3]

            if rgb_rev[pxl] in size:
                size[rgb_rev[pxl]] += 1
            else:
                size[rgb_rev[pxl]] = 1

    loc = ''

    for prov, size in size.items():
        loc += 'province:%s = { set_variable = { name = prov_size value = %s } }\n' % (prov, size / 1000)

    with open('prov_size.txt', 'w') as f:
        f.write(loc)
