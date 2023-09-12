
romExt = {
    "fc":".nes" ,
    "gb":".gb" ,
    "gbc":".gbc" ,
    "md":".md" ,
    "cps1":".cps",
    "sms":".sms" ,
}

def getRomList(dirName):
    import os
    from os import path
    dir = path.join('roms/', dirName)
    roms = [f for f in os.listdir(dir) if f.endswith(romExt[dirName])]    
    return roms


def getImgList(dirName):
    import os
    from os import path
    dir = path.join('images/', dirName)
    imgs = [f for f in os.listdir(dir) if f.endswith('.png')]
    return imgs

def imageDelete(imgPath, romPath):
    import os
    from os import path

    roms = [os.path.splitext(f)[0] for f in os.listdir(romPath)]
    imgs = [os.path.splitext(f)[0] for f in os.listdir(imgPath)]

    for f in imgs:
        if f not in roms:
            print("Roms not exists: ", f)
            os.remove(path.join(imgPath, f + '.png'))


def printRomInfo(imgPath, romPath):
    import os
    from os import path

    roms = [os.path.splitext(f)[0] for f in os.listdir(romPath)]
    imgs = [os.path.splitext(f)[0] for f in os.listdir(imgPath)]

    for f in roms:
        if f not in imgs:
            print("Image not exists: ", f)

# main function for test
if __name__ == "__main__":
    print("Test getRomList")
    print(getRomList('fc'))