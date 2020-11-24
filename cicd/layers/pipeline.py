#!/usr/bin/env python3
import os
from aws_cdk import (
  core,
  aws_s3 as s3,
  aws_ecr as ecr,
  aws_ecr_assets as assets,
  aws_codebuild as build,
  aws_codepipeline as pipeline
)

src_root_dir = os.path.join(os.path.dirname(__file__),"../..")

class BuildPipelineLayer(core.Construct):
  """
  Configure and deploy the network
  """
  def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

   
    self.core_pipeline = pipeline.Pipeline(self, 'CorePipeline',
      pipeline_name='FinSurf-CorePipeline')