#!/usr/bin/env python3
import os
from aws_cdk import (
  core,
  aws_ecr_assets as assets,
)

src_root_dir = os.path.join(os.path.dirname(__file__),"../..")

class BuildImagesLayer(core.Construct):
  """
  Configure and deploy the network
  """
  def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    self.cdk_image = assets.DockerImageAsset(self,'CdkDeployImage',
      directory=os.path.join(src_root_dir,'deploy/image'),
      repository_name='finsurf-cdk-env')
    