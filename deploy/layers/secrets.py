from aws_cdk import (
  core,
  aws_ec2 as ec2,
  aws_secretsmanager as sm
)

class SecretsLayer(core.Construct):
  """
  Configure and deploy the network
  """
  def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    self.tda_secret = sm.Secret(self,'TDA_SECRET',
      description='Holds the Ameritrade root access document',
      removal_policy=core.RemovalPolicy.DESTROY)
