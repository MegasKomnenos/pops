from PIL import Image
import glob

class Prov:
    def __init__(self):
        self.e = 0
        self.gs = set()

class World:
    def __init__(self):
        self.rgb = dict()

        with open('map_data\\definition.csv', 'rb') as f:
            for line in f.readlines()[1:]:
                line = line.decode("latin-1")
                line = line[:line.find('#')]

                if line:
                    line = line.split(';')

                    self.rgb[line[0]] = (int(line[1]), int(line[2]), int(line[3]))

        self.rgb_to_prov = {v:k for k, v in self.rgb.items()}
        self.provs = {k:Prov() for k in self.rgb}
        
        self.provmap = Image.open('map_data\\provinces.png')
        self.emap = Image.open('data\\test_modified_ref.png')
        self.gsmap = [(path[path.rfind('\\') + 1:path.find('_modified_ref')], Image.open(path)) for path in glob.glob('data\\*.png') if not 'test' in path]

        self.pixel_to_prov = [['' for _ in range(self.provmap.height)] for _ in range(self.provmap.width)]

        for y in range(self.provmap.height):
            for x in range(self.provmap.width):
                prov = self.rgb_to_prov[self.provmap.getpixel((x, y))]
                self.pixel_to_prov[x][y] = prov

        for y in range(self.emap.height):
            for x in range(self.emap.width):
                rgb = self.emap.getpixel((x, y))
                prov = self.pixel_to_prov[x*2][y*2]

                self.provs[prov].e += rgb[2] * 256 * 256 + rgb[1] * 256 + rgb[0]

                for name, img in self.gsmap:
                    if img.getpixel((x, y))[1] > 0:
                        self.provs[prov].gs.add(name)
                        

        for prov in self.provs.values():
            prov.e /= 500000
            prov.e = int(prov.e)

        string = ''

        for name, prov in self.provs.items():
            if prov.e or prov.gs:
                string += 'province:%s = { ' % name

                if prov.e:
                    string += 'set_variable = { name = extraction_total value = %s } ' % prov.e
                if prov.gs:
                    for g in prov.gs:
                        string += 'set_variable = { name = has_%s value = 1 } ' % g

                string += '}\n'

        with open('out.txt', 'w') as f:
            f.write(string)

    def close(self):
        self.provmap.close()
        self.emap.close()

        for _, gs in self.gsmap:
            gs.close()

a = World()
a.close()
