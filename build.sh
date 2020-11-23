#!/bin/bash

apt-get -y update
apt-get -y install zip

pushd /src/EmailServiceLambda
dotnet publish -o /publish

pushd /publish
zip -r /output/EmailServiceLambda.zip .
