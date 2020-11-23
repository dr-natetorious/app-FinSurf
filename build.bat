@ECHO OFF
@ECHO ==================================
@ECHO Local Build Script
@ECHO Nate Bachmeier - Amazon Solutions
@ECHO ==================================

@SETLOCAL enableextensions enabledelayedexpansion
@SET base_path=%~dp0
@PUSHD %base_path%

@MKDIR %base_path/bin

docker run -it -v %base_path%\bin:/output -v %cd%:/src -w /src mcr.microsoft.com/dotnet/sdk:3.1 build.sh