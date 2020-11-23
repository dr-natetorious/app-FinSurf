from aws_cdk import (
    aws_ec2 as ec2,
    aws_dynamodb as ddb,
    core
)

class DataStorageLayer(core.Construct):
  """
  Configure and deploy the network
  """
  def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    self.auditTable = ddb.Table(self, 'AuditTable',
      table_name='AuditTable',
      partition_key=ddb.Attribute(name='PartitionKey', type=ddb.AttributeType.STRING),
      sort_key=ddb.Attribute(name='SortKey', type=ddb.AttributeType.STRING),
      billing_mode= ddb.BillingMode.PAY_PER_REQUEST,
      point_in_time_recovery=True,
      encryption= ddb.TableEncryption.AWS_MANAGED,
      #time_to_live_attribute=ddb.Attribute(name='Expiration', type=ddb.AttributeType.NUMBER)
    )

