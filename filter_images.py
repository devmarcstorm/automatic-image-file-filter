#!/usr/bin/env python3

import os
from PIL import Image
from shutil import copyfile, copystat
import configparser as conf
import ast

class colors:
    TITLE = '\033[0m'
    OK_GREEN = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    NORMAL = '\033[0m'

def main():
    try:
        config = conf.ConfigParser()
        print(os.path.dirname(os.path.realpath(__file__)))
        config.read('{}/config.ini'.format(os.path.dirname(os.path.realpath(__file__))))

        # path variables
        path_in = config.get('PathVariables', 'InputPath')
        path_out = config.get('PathVariables', 'OutputPath')

        # file variables
        dir_name = config.get('FileVariables', 'DirectoryName')
        img_out_name = config.get('FileVariables', 'ImageOutputName')

        # image variables
        valid_extentions = ast.literal_eval(config.get('ImageVariables', 'ValidExtensions'))
        min_width = config.getint('ImageVariables', 'MinimalWidth')
        min_height = config.getint('ImageVariables', 'MinimalHeight')
        aspectRatioFilter = config.getboolean('ImageVariables', 'AspectRatioFilter')
        aspectRatioWidth = config.getint('ImageVariables', 'AspectRatioWidth')
        aspectRatioHeight = config.getint('ImageVariables', 'AspectRatioHeight')

        # list variables
        image_list = []
        images_big = []
        dirList = os.listdir(path_in)
        img_count = 0
        image_index = 0

        # behavior variables
        delete = config.getboolean('BehaviourVariables', 'Delete')
        rename = config.getboolean('BehaviourVariables', 'Rename')

    except (conf.NoOptionError, conf.NoSectionError, NameError, SyntaxError, ValueError, FileNotFoundError, Exception) as e:
        print(colors.ERROR + 'ERROR: {}'.format(e))
        print('       Please check your config.ini file.')
        print(colors.NORMAL)
        return

    print()
    print('--------------------')
    print('IMAGE FILTER - START')
    print('--------------------')
    print('valid extentions: {}'.format(valid_extentions))
    print('min width: {}'.format(min_width))
    print('min height: {}'.format(min_height))
    print('imput path: {}'.format(path_in))
    print('output path: {}/{}'.format(path_out, dir_name))
    print('delete images in output path: {}'.format(delete))
    print('rename images in output path: {} with "{}"'.format(rename, img_out_name))
    print('--------------------')
    print()

    # proof path of existence
    if not (os.path.exists(path_in)):
        print(colors.ERROR + 'The given input path {} does not exsist'.format(path_in) + colors.NORMAL)
        return
    if not (os.path.exists(path_out)):
        print(colors.ERROR + 'The given output path {} does not exsist'.format(path_out) + colors.NORMAL)
        return

    # find all images
    for image in dirList:
        ext = os.path.splitext(image)[1]
        if (ext in valid_extentions):
            image_list.append(image)
            img_count += 1
    print(colors.OK_GREEN + 'Found {} images in {}'.format(img_count, path_in) + colors.NORMAL)
    print()

    # filter found images
    img_count = 0
    for image in image_list:
        try:
            im = Image.open('{}/{}'.format(path_in, image))
            width, height = im.size
            if ((width >= min_width and height >= min_height)):
                print(colors.OK_GREEN + 'Found image {} with resolution:'.format(image))
                print('   w: {} + h: {}'.format(width, height))
                print('   aspect ratio: {} : {}'.format(width / height, 16 / 10))
                if (aspectRatioFilter):
                    if (width / height == aspectRatioWidth / aspectRatioHeight):
                        print(colors.NORMAL)
                        images_big.append(image)
                        img_count += 1
                    else:
                        print(colors.WARNING + '   {} not copied due to wrong aspect ratio (not {}/{})'.format(image, aspectRatioWidth, aspectRatioHeight))
                        print(colors.NORMAL)
                else:
                    print(colors.NORMAL)
                    images_big.append(image)
                    img_count += 1
        except OSError as e:
            print(colors.ERROR + 'ERROR: {}'.format(e) + colors.NORMAL)
            print()


    if not (os.path.exists(path_out + '/' + dir_name)):
        os.makedirs(path_out + '/' + dir_name)

    # clear new path if 'delete' is True
    if (delete):
        dirList.clear
        i = 0
        for filename in os.listdir(path_out + '/' + dir_name):
            ext = os.path.splitext(filename)[1]
            if (ext in valid_extentions and not filename.startswith('.')):
                src = '{}/{}/{}'.format(path_out, dir_name, filename)
                os.remove(src)
                i += 1
        print(colors.WARNING + 'Removed {} images in {}/{}'.format(i, path_out, dir_name))
        print(colors.NORMAL)

    # copy filterd images to the new path
    for image in images_big:
        ext = os.path.splitext(image)[1]
        if not (os.path.exists(path_out + '/' + dir_name + '/' + image + ext)):
            copyfile('{}/{}'.format(path_in, image), '{}/{}/{}_{}.{}'.format(path_out, dir_name, image, image_index, ext))
    print(colors.OK_GREEN + 'Copied {} images in {}/{}'.format(img_count, path_out, dir_name))
    print(colors.NORMAL)

    # rename all images in the new path if 'rename' is True
    if (rename):
        dirList.clear
        i = 0
        for filename in os.listdir(path_out + '/' + dir_name):
            ext = os.path.splitext(filename)[1]
            dst = img_out_name + "_" + str(i) + ext
            if (ext in valid_extentions and not filename.startswith('.')):
                src = path_out + '/' + dir_name + '/' + filename
                dst = path_out + '/' + dir_name + '/' + dst
                os.rename(src, dst)
                i += 1
        print(colors.WARNING + 'Renamed {} images in {}/{}'.format(i, path_out, dir_name) + colors.NORMAL)

    print()
    print('--------------------')
    print('IMAGE FILTER - DONE')
    print('--------------------')
    print()

if __name__ == "__main__":
    main()
