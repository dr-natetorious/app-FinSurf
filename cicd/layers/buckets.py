#!/usr/bin/env python3
import os
from aws_cdk import (
  core,
  aws_s3 as s3,
  aws_kms as kms,
  aws_ssm as ssm,
)

src_root_dir = os.path.join(os.path.dirname(__file__),"../..")

class BucketLayer(core.Construct):
  """
  Configure and deploy the network
  """
  def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)
    
    self.artifacts_key = kms.Key(self,'ArtifactKey',
      alias='build/artifacts',
      description='Encryption key for FinSurf build artifacts',
      enable_key_rotation=True)

    self.artifacts_bucket = s3.Bucket(self,'FinSurfBuildArtifacts',
      block_public_access= s3.BlockPublicAccess.BLOCK_ALL,
      versioned=True,
      bucket_name='nbachmei.finsurf.us-east-1',
      encryption= s3.BucketEncryption.KMS,
      encryption_key= self.artifacts_key 
    )

    ssm.StringParameter(self,'BucketParameter',
      tier= ssm.ParameterTier.STANDARD,
      description='Location of the app-Surf artifact bucket',
      parameter_name='/app-FinSurf/artifacts/bucket_name',
      string_value=self.artifacts_bucket.bucket_arn)
