#!/usr/bin/env python3
from aws_cdk import (
    aws_ec2 as ec2,
    aws_eks as eks,
    aws_kms as kms,
    core
)

class KubernetesClusterLayer(core.Construct):
  """
  Configure and deploy the network
  """
  def __init__(self, scope: core.Construct, id: str, vpc:ec2.IVpc, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)
    
    self.encryptionKey = kms.Key(self,'KubeClusterKey')
    self.cluster = eks.Cluster(self,'KubeCluster',
      version= eks.KubernetesVersion.V1_18,
      vpc=vpc,
      default_capacity=0,
      secrets_encryption_key=self.encryptionKey,
      endpoint_access= eks.EndpointAccess.PRIVATE
    )
