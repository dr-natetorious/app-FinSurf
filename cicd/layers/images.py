#!/usr/bin/env python3
import os
from aws_cdk import (
  core,
  aws_ecr_assets as assets,
)

src_root_dir = os.path.join(os.path.dirname(__file__),"../images")

class BuildImagesLayer(core.Construct):
  """
  Configure and deploy the network
  """
  def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    self.python_build = assets.DockerImageAsset(self,'PythonBuild',
      directory=os.path.join(src_root_dir,'python-build'),
      repository_name='finsurf-python-build')

    self.cdk_deploy = assets.DockerImageAsset(self,'CdkDeployImage',
      directory=os.path.join(src_root_dir,'cdk-deploy'),
      repository_name='finsurf-cdk-env')
    