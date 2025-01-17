from os import environ, path
from json import dumps
import boto3
from td.client import TDClient

class ClientFactory:

  @property
  def td_client_id(self) -> str:
    return self.__get_value('TDA_CLIENT_ID')

  @property
  def td_redirect_uri(self)->str:
    return self.__get_value('TDA_REDIRECT_URI')
  
  @property
  def td_credentials_secret_id(self) -> str:
    return self.__get_value('TDA_SECRET_ID')

  def create_client(self) -> TDClient:
    creds_file = self.__fetch_credential_file()
    client = TDClient(
      client_id=self.td_client_id,
      redirect_uri=self.td_redirect_uri,
      credentials_path=creds_file)

    client.login()
    return client


  def __fetch_credential_file(self, outpath:str = './creds.json'):
    if path.exists(outpath):
      return outpath

    secrets = boto3.client('secretsmanager')
    response = secrets.get_secret_value(
      SecretId=self.td_credentials_secret_id)

    td_creds = response['SecretString']
    
    with open(outpath,'w') as file:
      file.write(td_creds)

    return outpath

  def __get_value(self, name):
    return environ.get(name)