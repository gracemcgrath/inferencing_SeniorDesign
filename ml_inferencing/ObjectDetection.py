import onnx
import numpy as np
import onnxruntime as ort
from PIL import Image
import cv2
import matplotlib.pyplot as plt
import sys
import os

# Code copied from jupyter notebook:
# URL: https://github.com/onnx/models/blob/main/vision/classification/onnxrt_inference.ipynb

print("Python version")
print(sys.version)


def get_true_filename(filename):
    try:
        # Hack for pyInstaller. Refer https://stackoverflow.com/a/13790741
        base = sys._MEIPASS
    except Exception:
        base = os.path.abspath(".")
    return os.path.join(base, filename)

while True:


    # original code method to read file in existing directory
    with open(get_true_filename('synset.txt')) as f:
        labels = [l.rstrip() for l in f]

    model_path = 'resnet50-v1-12.onnx'
    model = onnx.load(model_path)
    # Start from ORT 1.10, ORT requires explicitly setting the providers parameter if you want to use execution providers
    # other than the default CPU provider (as opposed to the previous behavior of providers getting set/registered by default
    # based on the build flags) when instantiating InferenceSession.
    # For example, if NVIDIA GPU is available and ORT Python package is built with CUDA, then call API as following:
    # onnxruntime.InferenceSession(path/to/model, providers=['CUDAExecutionProvider']).
    session = ort.InferenceSession(model.SerializeToString())

    def get_image(path, show=False):
        with Image.open(path) as img:
            img = np.array(img.convert('RGB'))
        if show:
            plt.imshow(img)
            plt.axis('off')
        return img
        return cv2.imshow('Original', img)

    def preprocess(img):
        img = img / 255.
        img = cv2.resize(img, (256, 256))
        h, w = img.shape[0], img.shape[1]
        y0 = (h - 224) // 2
        x0 = (w - 224) // 2
        img = img[y0 : y0+224, x0 : x0+224, :]
        img = (img - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
        img = np.transpose(img, axes=[2, 0, 1])
        img = img.astype(np.float32)
        img = np.expand_dims(img, axis=0)
        return img

    #predicts top probability
    def predict(path):
        img = get_image(path, show=True)
        img = preprocess(img)
        ort_inputs = {session.get_inputs()[0].name: img}
        preds = session.run(None, ort_inputs)[0]
        preds = np.squeeze(preds)
        a = np.argsort(preds)[::-1]
        print('class=%s ; probability=%f' %(labels[a[0]],preds[a[0]]))


    # #predicts top probability
    # def predict(path):
    #     img = get_image(path, show=True)
    #     img = preprocess(img)
    #     ort_inputs = {session.get_inputs()[0].name: img}
    #     preds = session.run(None, ort_inputs)[0]
    #     preds = np.squeeze(preds)
    #     a = np.argsort(preds)[::-1]
    #     print('class=%s' %(labels[a[0]],preds[a[0]]))


    img_path = input("Please select your image by typing the file name followed by the .jpg extension:  ")
    out = predict(img_path)
    print(out)

 
