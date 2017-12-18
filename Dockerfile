FROM nvidia/cuda:8.0-cudnn6-runtime-ubuntu16.04

RUN apt-get update && apt-get -y install python-dev python-pip && \
    pip install http://download.pytorch.org/whl/cu80/torch-0.3.0.post4-cp27-cp27mu-linux_x86_64.whl && \ 
    pip install torchvision && \
    pip install matplotlib opencv-python
    
    

