#!/usr/bin/env python3
import os
from layers.buckets import BucketLayer
from aws_cdk import (
  core,
  aws_s3 as s3,
  aws_codebuild as build,
  aws_codepipeline as pipeline,
  aws_codepipeline_actions as actions,
)

src_root_dir = os.path.join(os.path.dirname(__file__),"../..")

class CodePipelineLayer(core.Construct):
  """
  Configure and deploy the network
  """
  def __init__(self, scope: core.Construct, id: str, buckets:BucketLayer, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)
   
    self.core_pipeline = pipeline.Pipeline(self, 'CorePipeline',
      pipeline_name='FinSurf-CorePipeline',stages=[
        pipeline.StageProps(stage_name='Step-1', actions=[
        ]),
        pipeline.StageProps(stage_name='Step-2')
      ])