@ECHO OFF
@ECHO ==================================
@ECHO Local Debug Script
@ECHO Nate Bachmeier
@ECHO ==================================

@SETLOCAL enableextensions enabledelayedexpansion
@SET base_path=%~dp0

@SET LOCAL_DEBUG=true
@SET FLASK_APP=webapp.py
@SET FLASK_ENV=development

python -m flask run

