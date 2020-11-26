@ECHO OFF
@ECHO ==================================
@ECHO Local Debug Script
@ECHO Nate Bachmeier
@ECHO ==================================

@SETLOCAL enableextensions enabledelayedexpansion
@SET base_path=%~dp0

@SET LOCAL_DEBUG=true
@SET FLASK_APP=handler.py
@SET FLASK_ENV=development
@SET REDIS_HOST=localhost
@SET REDIS_PORT=6379


python -m flask run

