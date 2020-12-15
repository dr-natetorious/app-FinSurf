@ECHO OFF
@ECHO ==================================
@ECHO Deployment Tool
@ECHO Nate Bachmeier - Amazon Solutions
@ECHO ==================================

@SETLOCAL enableextensions enabledelayedexpansion
@SET base_path=%~dp0
@PUSHD %base_path%

@CALL cdk deploy * --require-approval never

@POPD