#!/usr/bin/env python3
import os
from aws_cdk import (
  core,
  aws_iam as iam,
  aws_s3 as s3,
  aws_kms as kms,
  aws_ssm as ssm,
)

class KeyLayer(core.Construct):
  """
  Configure and deploy the network
  """
  def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)
    
    self.build_key = kms.Key(self,'ArtifactKey',
      alias='finsurf/cicd',
      trust_account_identities=True,
      description='Encryption key for FinSurf build system',
      enable_key_rotation=True)

    ssm.StringParameter(self,'ArtifactKeyParameter',
      parameter_name='/app-FinSurf/artifacts/encryption_key_arn',
      string_value=self.build_key.key_arn,
      description='The active key for encrypting FinSurf artifacts')
