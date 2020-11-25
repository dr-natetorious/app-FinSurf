#from typing import Optional
# from aws_cdk.core import App, Stack, Environment
# from layers.images import BuildImagesLayer
# from layers.buckets import BucketLayer
# #from layers.pipeline import CodePipelineLayer
# from layers.buildjobs import BuildJobLayer
# from layers.kms import KeyLayer

class BuildContext:
    def __init__(self):
        pass
    
    @property
    def build_images(self):# -> BuildImagesLayer:
        return self.__build_images

    @build_images.setter
    def build_images(self,value): #:BuildImagesLayer)->None:
        self.__build_images = value
    
    @property
    def buckets(self):# -> BucketLayer:
        return self.__buckets

    @buckets.setter
    def buckets(self,value):#:BucketLayer)->None:
        self.__buckets = value

    @property
    def build_projects(self):# -> BuildJobLayer:
        return self.__build_proj

    @build_projects.setter
    def build_projects(self,value):#:BuildJobLayer)->None:
        self.__build_proj = value
    
    @property
    def encryption_keys(self):# -> KeyLayer:
        return self.__encryption_keys

    @encryption_keys.setter
    def encryption_keys(self,value):#:KeyLayer)->None:
        self.__encryption_keys = value
