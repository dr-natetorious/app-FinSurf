from aws_cdk import (
    aws_ec2 as ec2,
    aws_kinesis as ks,
    core
)

class KinesisLayer(core.Construct):
  """
  Configure and deploy the network
  """
  def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    self.kinesis = ks.Stream(self,'MailStream',
      encryption= ks.StreamEncryption.MANAGED)

