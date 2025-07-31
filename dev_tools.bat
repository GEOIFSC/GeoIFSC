@echo off
REM =====================================================================
REM GeoIFSC Plugin - Ferramentas de Desenvolvimento Robustas v3.0
REM =====================================================================
REM Autor: GeoIFSC Team
REM Data: 2025-01-10
REM =====================================================================

chcp 65001 >nul 2>&1  :: Força o uso de UTF-8 no terminal
setlocal EnableDelayedExpansion

:: === CONFIGURAÇÕES DINÂMICAS ===
set "SCRIPT_DIR=%~dp0"
set "PLUGIN_NAME=GeoIFSC"
set "SRC_DIR=%SCRIPT_DIR%src\geoifsc"
set "METADATA_FILE=%SCRIPT_DIR%metadata.txt"
set "README_FILE=%SCRIPT_DIR%README.md"
set "BACKUP_DIR=%SCRIPT_DIR%backups"
set "DIST_DIR=%SCRIPT_DIR%dist"
set "LOG_FILE=%SCRIPT_DIR%dev_tools.log"

:: Detecta QGIS e perfil ativo
call :DETECT_QGIS_DIR
if "%QGIS_PLUGINS_DIR%"=="" (
  echo ERRO: Não encontrou instalação do QGIS!
  pause & exit /b 1
)
set "PLUGIN_LINK_DIR=%QGIS_PLUGINS_DIR%\%PLUGIN_NAME%"

:: Cria pastas se faltar
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"

:: === MENU PRINCIPAL ===
:MAIN_MENU
cls
echo ========================================================
echo      GeoIFSC Dev Tools v3.0 - Menu Principal
echo ========================================================
echo 1 - Desenvolvimento e Instalacao
echo 2 - Empacotamento e Versao
echo 3 - Manutencao e Qualidade
echo 4 - Logs e Utilitarios
echo 0 - Sair
echo.
set /p "opt=Escolha [0-4]: "

if "%opt%"=="1" goto MENU_DESENV
if "%opt%"=="2" goto MENU_RELEASE
if "%opt%"=="3" goto MENU_MAINT
if "%opt%"=="4" goto MENU_LOGS
if "%opt%"=="0" goto END

:: Mensagem de erro para entrada inválida
echo Opcao invalida! Por favor, escolha uma opcao entre 0 e 4.
pause
goto MAIN_MENU

:: === SUBMENU 1: Desenvolvimento & Instalacao ===
:MENU_DESENV
cls
echo == Desenvolvimento e Instalacao ==
echo 1 - Instalar plugin
echo 2 - Remover plugin
echo 3 - Recarregar plugin
echo 4 - Status da instalacao
echo 0 - Voltar
echo.
set /p "opt=Escolha [0-4]: "
if "%opt%"=="1" goto INSTALL_PLUGIN
if "%opt%"=="2" goto REMOVE_PLUGIN
if "%opt%"=="3" goto RELOAD_PLUGIN
if "%opt%"=="4" goto STATUS_PLUGIN
if "%opt%"=="0" goto MAIN_MENU
goto MENU_DESENV

:: === SUBMENU 2: Empacotamento e Versao ===
:MENU_RELEASE
cls
echo == Empacotamento e Versao ==
echo 1 - Empacotar plugin
echo 2 - Bump de versao
echo 3 - Release completo
echo 4 - Gerenciar backups
echo 0 - Voltar
echo.
set /p "opt=Escolha [0-4]: "
if "%opt%"=="1" goto PACKAGE_PLUGIN
if "%opt%"=="2" goto BUMP_VERSION
if "%opt%"=="3" goto CREATE_RELEASE
if "%opt%"=="4" goto MANAGE_BACKUPS
if "%opt%"=="0" goto MAIN_MENU
goto MENU_RELEASE

:: === SUBMENU 3: Manutencao & Qualidade ===
:MENU_MAINT
cls
echo == Manutencao e Qualidade ==
echo 1 - Limpar cache Python
echo 2 - Validar projeto
echo 3 - Executar testes
echo 4 - Verificar QGIS
echo 0 - Voltar
echo.
set /p "opt=Escolha [0-4]: "
if "%opt%"=="1" goto CLEAN_CACHE
if "%opt%"=="2" goto VALIDATE_PROJECT
if "%opt%"=="3" goto RUN_TESTS
if "%opt%"=="4" goto CHECK_QGIS
if "%opt%"=="0" goto MAIN_MENU
goto MENU_MAINT

:: === SUBMENU 4: Logs & Utilitarios ===
:MENU_LOGS
cls
echo == Logs e Utilitarios ==
echo 1 - Ver logs de desenvolvimento
echo 2 - Exportar projeto completo
echo 3 - Configuracoes avancadas
echo 0 - Voltar
echo.
set /p "opt=Escolha [0-3]: "
if "%opt%"=="1" goto VIEW_LOGS
if "%opt%"=="2" goto EXPORT_PROJECT
if "%opt%"=="3" goto ADVANCED_CONFIG
if "%opt%"=="0" goto MAIN_MENU
goto MENU_LOGS

:: === Implementações dos comandos ===

:INSTALL_PLUGIN
echo Instalando plugin...
call :LOG_MESSAGE "install:start"
call :CHECK_QGIS_RUNNING
if "%QGIS_RUNNING%"=="true" (
  echo QGIS está rodando — feche para evitar conflitos.
  set /p "c=Continuar mesmo assim? (s/N): "
  if /i not "!c!"=="s" goto MAIN_MENU
)
if exist "%PLUGIN_LINK_DIR%" (
  call :REMOVE_PLUGIN_FILES
)
echo Tentando symlink...
rem -- mostre comando e erros para debug
echo >"%LOG_FILE%" [debug] mklink /D "%PLUGIN_LINK_DIR%" "%SRC_DIR%"
mklink /D "%PLUGIN_LINK_DIR%" "%SRC_DIR%"
set "MKERR=%ERRORLEVEL%"
if %MKERR% neq 0 (
  echo Falhou symlink (code=%MKERR%) — copiando arquivos...
  call :LOG_MESSAGE "symlink:fail code=%MKERR%"
  call :COPY_PLUGIN_FILES
  set "INSTALL_METHOD=copy"
) else (
  echo Symlink criado com sucesso!
  call :LOG_MESSAGE "symlink:ok"
  set "INSTALL_METHOD=symlink"
)
rem -- liste apenas entradas de link para confirmação
echo Verificando symlinks em %QGIS_PLUGINS_DIR%:
dir /AL "%QGIS_PLUGINS_DIR%"  
call :VALIDATE_INSTALLATION
echo [OK] Instalacao valida: %INSTALL_VALID% - Metodo: %INSTALL_METHOD%
call :LOG_MESSAGE "install:end status=%INSTALL_VALID% method=%INSTALL_METHOD%"
pause & goto MAIN_MENU

:REMOVE_PLUGIN
echo Removendo plugin...
if not exist "%PLUGIN_LINK_DIR%" (
  echo Plugin nao instalado.
) else (
  call :REMOVE_PLUGIN_FILES
  echo Plugin removido com sucesso!
  rem limpa variáveis de estado da instalação
  set "INSTALL_METHOD="
  set "INSTALL_VALID=false"
)
pause & goto MAIN_MENU

:RELOAD_PLUGIN
echo Recarregando plugin...
call :CHECK_QGIS_RUNNING
if "%QGIS_RUNNING%"=="true" (
  echo Fechando QGIS...
  taskkill /F /IM qgis-bin.exe 2>nul
  timeout /t 2 >nul
)
if "%INSTALL_METHOD%"=="copy" call :CLEAN_PLUGIN_CACHE
echo Recarregamento concluido.
call :LOG_MESSAGE "reload"
pause & goto MAIN_MENU

:STATUS_PLUGIN
call :CHECK_INSTALLATION_STATUS
echo Instalação: %INSTALLATION_STATUS%
echo Metodo: %INSTALL_METHOD%
echo Local: %PLUGIN_LINK_DIR%
pause & goto MAIN_MENU

:PACKAGE_PLUGIN
call :READ_CURRENT_VERSION
set "ZIP_NAME=%PLUGIN_NAME%_v%CURRENT_VERSION%.zip"
set "ZIP_PATH=%DIST_DIR%\%ZIP_NAME%"
echo Empacotando: %ZIP_NAME%
powershell -Command "Compress-Archive -Path '%SRC_DIR%\*' -DestinationPath '%ZIP_PATH%' -Force" >nul 2>&1
if exist "%ZIP_PATH%" (
  echo ✓ Pacote criado em %ZIP_PATH%
  call :LOG_MESSAGE "package created=%ZIP_PATH%"
) else (
  echo ✗ Falha ao criar pacote.
)
pause & goto MAIN_MENU

:BUMP_VERSION
call :READ_CURRENT_VERSION
echo Versao atual: %CURRENT_VERSION%
echo 1-Patch 2-Minor 3-Major 4-Custom 5-Cancelar
set /p "opt=Escolha [1-5]: "
if "%opt%"=="5" goto MAIN_MENU
if "%opt%"=="1" set "NEW=%PATCH_VERSION%"
if "%opt%"=="2" set "NEW=%MINOR_VERSION%"
if "%opt%"=="3" set "NEW=%MAJOR_VERSION%"
if "%opt%"=="4" (
  set /p "NEW=Digite X.Y.Z: "
  call :VALIDATE_VERSION_FORMAT "%NEW%"
  if "!VERSION_VALID!"=="false" (
    echo Formato invalido! & pause & goto MAIN_MENU
  )
)
set /p "c=Confirmar %CURRENT_VERSION% -> %NEW%? (s/N): "
if /i not "%c%"=="s" goto MAIN_MENU
call :CREATE_VERSION_BACKUP "%CURRENT_VERSION%"
call :UPDATE_VERSION_IN_METADATA "%NEW%"
echo Versao atualizada.
call :LOG_MESSAGE "bump from=%CURRENT_VERSION% to=%NEW%"
pause & goto MAIN_MENU

:CREATE_RELEASE
echo === Release Completo ===
call :VALIDATE_PROJECT
call :RUN_TESTS
call :BUMP_VERSION
call :PACKAGE_PLUGIN
echo Release concluido.
pause & goto MAIN_MENU

:MANAGE_BACKUPS
cls
echo == Gerenciar Backups ==
echo 1-Criar backup
echo 2-Restaurar backup
echo 3-Excluir backup
echo 0-Voltar
set /p "opt=Escolha [0-3]: "
if "%opt%"=="1" (
  call :CREATE_VERSION_BACKUP "%CURRENT_VERSION%"
)
if "%opt%"=="2" (
  dir /B "%BACKUP_DIR%" & echo.
  set /p "file=Nome do ZIP: "
  if exist "%BACKUP_DIR%\%file%" (
    powershell -Command "Expand-Archive -Path '%BACKUP_DIR%\%file%' -DestinationPath '%SRC_DIR%' -Force"
    echo Restaurado.
  ) else echo Arquivo nao encontrado.
)
if "%opt%"=="3" (
  dir /B "%BACKUP_DIR%" & echo.
  set /p "file=Nome do ZIP: "
  if exist "%BACKUP_DIR%\%file%" del "%BACKUP_DIR%\%file%" & echo Excluido. else echo Nao encontrado.
)
if "%opt%"=="0" goto MAIN_MENU
pause & goto MAIN_MENU

:CLEAN_CACHE
echo Limpando cache Python...
for /r "%SRC_DIR%" %%f in (*.pyc) do del /q "%%f"
for /d /r "%SRC_DIR%" %%d in (__pycache__) do rmdir /s/q "%%d"
echo Cache limpo.
call :LOG_MESSAGE "clean_cache"
pause & goto MAIN_MENU

:VALIDATE_PROJECT
echo Validando projeto...
set "errs=0"
call :VALIDATE_FILE "%METADATA_FILE%" "metadata.txt"
call :VALIDATE_FILE "%SRC_DIR%\__init__.py" "__init__.py"
call :VALIDATE_FILE "%SRC_DIR%\geoifsc_plugin.py" "geoifsc_plugin.py"
call :VALIDATE_FILE "%SRC_DIR%\raster_upload_dialog.py" "View"
call :VALIDATE_FILE "%SRC_DIR%\raster_upload_controller.py" "Controller"
call :VALIDATE_FILE "%SRC_DIR%\raster_uploader_service.py" "Service"
call :VALIDATE_FILE "%SRC_DIR%\raster_upload_params.py" "Model"
call :VALIDATE_FILE "%SRC_DIR%\connection_utils.py" "Utils"
if %errs% gtr 0 (
  echo Erros de validacao:%errs%
) else echo Valido.
pause & goto MAIN_MENU

:RUN_TESTS
echo Executando testes...
if exist "%SCRIPT_DIR%test_plugin.py" (
  python "%SCRIPT_DIR%test_plugin.py"
) else (
  pytest --maxfail=1 --disable-warnings || echo Algum teste falhou.
)
pause & goto MAIN_MENU

:CHECK_QGIS
echo QGIS Detectado:%QGIS_VERSION%
echo Plugins em %QGIS_PLUGINS_DIR%:
dir /B "%QGIS_PLUGINS_DIR%"
pause & goto MAIN_MENU

:VIEW_LOGS
echo Logs de Desenvolvimento:
if exist "%LOG_FILE%" type "%LOG_FILE%" else echo Sem logs.
pause & goto MAIN_MENU

:EXPORT_PROJECT
call :READ_CURRENT_VERSION
set "TS=%date:~-4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%"
set "OUT=%DIST_DIR%\%PLUGIN_NAME%_full_%TS%.zip"
echo Exportando projeto:%RESET% %OUT%
powershell -Command "Compress-Archive -Path '%SCRIPT_DIR%*' -DestinationPath '%OUT%' -Force"
echo Export concluido.
pause & goto MAIN_MENU

:ADVANCED_CONFIG
echo -- Configuracoes Atuais --
echo SCRIPT_DIR    = %SCRIPT_DIR%
echo SRC_DIR       = %SRC_DIR%
echo METADATA_FILE = %METADATA_FILE%
echo QGIS_PLUGINS  = %QGIS_PLUGINS_DIR%
echo PLUGIN_LINK   = %PLUGIN_LINK_DIR%
echo BACKUP_DIR    = %BACKUP_DIR%
echo DIST_DIR      = %DIST_DIR%
echo LOG_FILE      = %LOG_FILE%
pause & goto MAIN_MENU

:END
echo Obrigado por usar GeoIFSC Dev Tools!
call :LOG_MESSAGE "session:end"
endlocal
goto :EOF

::=== FUNCOES AUXILIARES ===

:DETECT_QGIS_DIR
set "QGIS_PLUGINS_DIR=" & set "QGIS_VERSION="
if exist "%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins" (
  set "QGIS_PLUGINS_DIR=%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins"
  set "QGIS_VERSION=QGIS 3.x"
) else for %%v in (QGIS3.34 QGIS3.32 QGIS3.30) do (
  if exist "%APPDATA%\QGIS\%%v\profiles\default\python\plugins" (
    set "QGIS_PLUGINS_DIR=%APPDATA%\QGIS\%%v\profiles\default\python\plugins"
    set "QGIS_VERSION=%%v" & goto _dq_end
  )
) & (_dq_end)
if exist "%USERPROFILE%\.qgis2\python\plugins" (
  set "QGIS_PLUGINS_DIR=%USERPROFILE%\.qgis2\python\plugins"
  set "QGIS_VERSION=QGIS 2.x"
)
goto :EOF

:CHECK_QGIS_RUNNING
set "QGIS_RUNNING=false"
tasklist /FI "IMAGENAME eq qgis-bin.exe" 2>nul | find /I "qgis-bin.exe" >nul && set "QGIS_RUNNING=true"
exit /b

:CHECK_INSTALLATION_STATUS
if exist "%PLUGIN_LINK_DIR%" (
  dir "%PLUGIN_LINK_DIR%" | find "<SYMLINKD>" >nul 2>&1 && (
    set "INSTALLATION_STATUS=Instalado (symlink)" & set "INSTALL_METHOD=symlink"
  ) || (
    set "INSTALLATION_STATUS=Instalado (cópia)"  & set "INSTALL_METHOD=copy"
  )
) else set "INSTALLATION_STATUS=Não instalado"
exit /b

:VALIDATE_INSTALLATION
set "INSTALL_VALID=false"
if exist "%PLUGIN_LINK_DIR%\__init__.py" if exist "%PLUGIN_LINK_DIR%\metadata.txt" set "INSTALL_VALID=true"
exit /b

:LOG_MESSAGE
echo [%date% %time%] %~1>>"%LOG_FILE%"
exit /b

:VALIDATE_FILE
if exist "%~1" (
  echo ✓ %~2% encontrado
) else (
  echo ✗ %~2% ausente
  set /a errs+=1
)
exit /b

:READ_CURRENT_VERSION
for /f "tokens=2 delims==" %%A in ('findstr /b /c:"version=" "%METADATA_FILE%"') do set "CURRENT_VERSION=%%A"
for /f "tokens=1-3 delims=." %%A in ("%CURRENT_VERSION%") do (
  set "MAJOR=%%A" & set "MINOR=%%B" & set "PATCH=%%C"
  set /a "NEXT_PATCH=PATCH+1" & set /a "NEXT_MINOR=MINOR+1" & set /a "NEXT_MAJOR=MAJOR+1"
  set "PATCH_VERSION=%%A.%%B.!NEXT_PATCH!"
  set "MINOR_VERSION=%%A.!NEXT_MINOR!.0"
  set "MAJOR_VERSION=!NEXT_MAJOR!.0.0"
)
exit /b

:VALIDATE_VERSION_FORMAT
echo %~1| findstr /r "^[0-9]\+\.[0-9]\+\.[0-9]\+$" >nul && set "VERSION_VALID=true" || set "VERSION_VALID=false"
exit /b

:UPDATE_VERSION_IN_METADATA
(for /f "delims=" %%L in ("%METADATA_FILE%") do (
  echo %%L| findstr /b "version=" >nul && (
    echo version=%~1
  ) || (
    echo %%L
  )
))>"%METADATA_FILE%.tmp"
move /y "%METADATA_FILE%.tmp" "%METADATA_FILE%" >nul
exit /b

:CREATE_VERSION_BACKUP
for /f "tokens=1-3 delims=/- " %%D in ("%date%") do set "D=%%F%%E%%D"
for /f "tokens=1-2 delims=:." %%H in ("%time%") do set "T=%%H%%I"
set "FILE=%BACKUP_DIR%\%PLUGIN_NAME%_v%~1_%D%_%T%.zip"
powershell -Command "Compress-Archive -Path '%SRC_DIR%\*' -DestinationPath '%FILE%' -Force" >nul
echo Backup criado: %FILE%
exit /b

:REMOVE_PLUGIN_FILES
echo Removendo arquivos do plugin...
if exist "%PLUGIN_LINK_DIR%" (
  rmdir /s /q "%PLUGIN_LINK_DIR%" >nul 2>&1 || (
    echo Erro ao remover arquivos do plugin.
    exit /b 1
  )
)
exit /b

:COPY_PLUGIN_FILES
echo Copiando arquivos do plugin...
xcopy /e /i "%SRC_DIR%\*" "%PLUGIN_LINK_DIR%\" || (
    echo Erro ao copiar arquivos do plugin.
    exit /b 1
)
exit /b

:CLEAN_PLUGIN_CACHE
echo Limpando cache do plugin...
for /r "%PLUGIN_LINK_DIR%" %%f in (*.pyc) do del /q "%%f"
for /d /r "%PLUGIN_LINK_DIR%" %%d in (__pycache__) do rmdir /s /q "%%d"
echo Cache do plugin limpo.
exit /b
