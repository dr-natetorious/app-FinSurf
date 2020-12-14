#!/usr/bin/env python3
import os
from infra.cicd.context import BuildContext
from aws_cdk import (
  core,
  aws_s3 as s3,
  aws_ssm as ssm,
)

src_root_dir = os.path.join(os.path.dirname(__file__),"../..")

class BucketLayer(core.Construct):
  """
  Configure and deploy the network
  """
  def __init__(self, scope: core.Construct, id: str, context:BuildContext, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)
    
    self.artifacts_key = context.encryption_keys.build_key

    self.artifacts_bucket = s3.Bucket(self,'FinSurfBuildArtifacts',
      block_public_access= s3.BlockPublicAccess.BLOCK_ALL,
      versioned=True,
      bucket_name='nbachmei.finsurf.'+ context.environment.region,
      encryption= s3.BucketEncryption.KMS,
      encryption_key= self.artifacts_key 
    )

    ssm.StringParameter(self,'BucketParameter',
      tier= ssm.ParameterTier.STANDARD,
      description='Location of the app-Surf artifact bucket',
      parameter_name='/app-FinSurf/artifacts/bucket_name',
      string_value=self.artifacts_bucket.bucket_arn)
