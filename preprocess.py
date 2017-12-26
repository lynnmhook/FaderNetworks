#!/usr/bin/env python
import os
import matplotlib.image as mpimg
import cv2
import numpy as np
import torch
import subprocess
import tempfile

try:
    from studio import fs_tracker
    DEFAULT_ZIP_PATH = fs_tracker.get_artifact('data')
    # IMG_DIR = fs_tracker.get_artifact('data')

except ImportError:
    fs_tracker = None
    DEFAULT_ZIP_PATH = 'data/img_align_celeba.zip'
    DEFAULT_ATTR_PATH = 'data/list_attr_celeba.txt'

IMG_DIR = os.path.join(tempfile.gettempdir(), 'data')
DEFAULT_ATTR_PATH = os.path.join(IMG_DIR, 'attributes.txt')

IMG_ZIP_PATH = os.environ.get('IMG_ZIP_PATH', DEFAULT_ZIP_PATH)

IMG_ATTR_PATH = os.environ.get('IMG_ATTR_PATH', DEFAULT_ATTR_PATH)
IMG_SIZE = 128

IMG_PATH = os.path.join(IMG_DIR, 'images_%i_%i.pth' % (IMG_SIZE, IMG_SIZE))
IMG20K_PATH = os.path.join(IMG_DIR, 'images_%i_%i_20000.pth' % (IMG_SIZE, IMG_SIZE))
ATTR_PATH = os.path.join(IMG_DIR, 'attributes.pth')

def preprocess_images():

    if os.path.isfile(IMG_PATH):
        print("%s exists, nothing to do." % IMG_PATH)
        return

    print("Reading images from img_align_celeba/ ...")
    raw_images = []
    for i in range(1, N_IMAGES + 1):
        if i % 10000 == 0:
            print(i)
        raw_images.append(mpimg.imread(os.path.join(IMG_DIR, '%06i.jpg' % i))[20:-20])

    if len(raw_images) != N_IMAGES:
        raise Exception("Found %i images. Expected %i" % (len(raw_images), N_IMAGES))

    print("Resizing images ...")
    all_images = []
    for i, image in enumerate(raw_images):
        if i % 10000 == 0:
            print(i)
        assert image.shape == (178, 178, 3)
        if IMG_SIZE < 178:
            image = cv2.resize(image, (IMG_SIZE, IMG_SIZE), interpolation=cv2.INTER_AREA)
        elif IMG_SIZE > 178:
            image = cv2.resize(image, (IMG_SIZE, IMG_SIZE), interpolation=cv2.INTER_LANCZOS4)
        assert image.shape == (IMG_SIZE, IMG_SIZE, 3)
        all_images.append(image)

    data = np.concatenate([img.transpose((2, 0, 1))[None] for img in all_images], 0)
    data = torch.from_numpy(data)
    assert data.size() == (N_IMAGES, 3, IMG_SIZE, IMG_SIZE)

    print("Saving images to %s ..." % IMG_PATH)
    torch.save(data[:20000].clone(), IMG20K_PATH)
    torch.save(data, IMG_PATH)

def preprocess():
    if os.path.isfile(ATTR_PATH):
        print("%s exists, nothing to do." % ATTR_PATH)
        return

    attr_lines = [line.rstrip() for line in open(IMG_ATTR_PATH, 'r')]
    N_IMAGES = int(attr_lines[0])
    attr_keys = attr_lines[1].split()
    n_attrib = len(attr_lines[1].split(','))

    attr_lines = attr_lines[:N_IMAGES+2]
    attributes = {k: np.zeros(N_IMAGES, dtype=np.bool) for k in attr_keys}

    all_images = []

    print("Loading images form " + IMG_ATTR_PATH)
    for i, line in enumerate(attr_lines[2:]):
        image_id = i + 1
        split = line.split()
        
        if i % 10000 == 0:
            print(i)

        image_path = os.path.join(IMG_DIR, split[0])
        if not os.path.isfile(image_path):
            continue

        raw_image = mpimg.imread(image_path)[20:-20]
        method = cv2.INTER_AREA if raw_image.shape[0] < IMG_SIZE else cv2.INTER_LANCZOS4
        image = cv2.resize(raw_image, (IMG_SIZE, IMG_SIZE), interpolation=method)

        all_images.append(image)

        assert all(x in ['-1', '1'] for x in split[1:])
        for j, value in enumerate(split[1:]):
            attributes[attr_keys[j]][i] = value == '1'

    print("Saving attributes to %s ..." % ATTR_PATH)
    torch.save(attributes, ATTR_PATH)

    data = np.concatenate([img.transpose((2, 0, 1))[None] for img in all_images], 0)
    data = torch.from_numpy(data)
    # assert data.size() == (N_IMAGES, 3, IMG_SIZE, IMG_SIZE)

    print("Saving images to %s ..." % IMG_PATH)
    torch.save(data, IMG_PATH)


def unzip_data():
    print("Unzipping images file...")
    subprocess.Popen(['unzip', '-u', IMG_ZIP_PATH, '-d', IMG_DIR], stdout=subprocess.PIPE).communicate()
    

unzip_data()
preprocess()

#preprocess_images()
#preprocess_attributes()
