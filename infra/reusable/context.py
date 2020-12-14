from aws_cdk.core import Environment

class InfraContext:

  def __init__(self, env:Environment):
    self.__environment = env
    self.__networking = None
    self.__earnings_api = None
    self.__alexa_skill = None

  @property
  def environment(self):
    return self.__environment

  @property
  def networking(self):
    return self.__networking

  @property
  def earnings_api(self):
    return self.__earnings_api

  @property
  def alexa_skill(self):
    return self.__alexa_skill

  @environment.setter
  def environment(self, value):
    self.__environment = value

  @networking.setter
  def networking(self, value):
    self.__networking = value

  @earnings_api.setter
  def earnings_api(self, value):
    self.__earnings_api = value

  @alexa_skill.setter
  def alexa_skill(self, value):
    self.__alexa_skill = value