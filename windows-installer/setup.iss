; SPEI Windows Installer Script
; Sistema de Prontuário Eletrônico Inteligente
; Version 1.0.0

[Setup]
AppName=SPEI - Sistema de Prontuário Eletrônico Inteligente
AppVersion=1.0.0
AppPublisher=CardioAI Pro
AppPublisherURL=https://spei.med.br
AppSupportURL=https://spei.med.br/suporte
AppUpdatesURL=https://spei.med.br/atualizacoes
DefaultDirName={autopf}\SPEI
DefaultGroupName=SPEI
AllowNoIcons=yes
LicenseFile=LICENSE.txt
InfoBeforeFile=README.txt
OutputDir=dist
OutputBaseFilename=SPEI-Setup-v1.0.0
SetupIconFile=assets\spei-icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
MinVersion=10.0
DisableProgramGroupPage=yes
DisableReadyPage=no
DisableFinishedPage=no
ShowLanguageDialog=no
LanguageDetectionMethod=uilanguage
UninstallDisplayIcon={app}\assets\spei-icon.ico
UninstallDisplayName=SPEI - Sistema de Prontuário Eletrônico Inteligente
VersionInfoVersion=1.0.0.0
VersionInfoCompany=CardioAI Pro
VersionInfoDescription=Sistema de Prontuário Eletrônico Inteligente
VersionInfoCopyright=Copyright (C) 2025 CardioAI Pro
VersionInfoProductName=SPEI
VersionInfoProductVersion=1.0.0

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Types]
Name: "full"; Description: "Instalação Completa"
Name: "compact"; Description: "Instalação Compacta"
Name: "custom"; Description: "Instalação Personalizada"; Flags: iscustom

[Components]
Name: "core"; Description: "Sistema Principal"; Types: full compact custom; Flags: fixed
Name: "database"; Description: "Banco de Dados PostgreSQL"; Types: full compact custom; Flags: fixed
Name: "ai"; Description: "Módulos de Inteligência Artificial"; Types: full custom
Name: "samples"; Description: "Dados de Exemplo"; Types: full custom
Name: "docs"; Description: "Documentação"; Types: full custom

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode
Name: "autostart"; Description: "Iniciar SPEI automaticamente com o Windows"; GroupDescription: "Opções de Sistema"
Name: "firewall"; Description: "Configurar regras do Windows Firewall"; GroupDescription: "Opções de Rede"

[Files]
; Core application files
Source: "app\*"; DestDir: "{app}\app"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core
Source: "runtime\*"; DestDir: "{app}\runtime"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core
Source: "config\*"; DestDir: "{app}\config"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core

; Utility scripts
Source: "utils\*"; DestDir: "{app}\utils"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core

; Assets and documentation
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core
Source: "docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: docs
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "BUILD-INSTRUCTIONS.md"; DestDir: "{app}"; Flags: ignoreversion; Components: docs

; AI Models (optional)
Source: "models\*"; DestDir: "{app}\models"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: ai

; Sample data (optional)
Source: "samples\*"; DestDir: "{app}\samples"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: samples

; Visual C++ Redistributables (downloaded during installation)
; Source: "redist\VC_redist.x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
Name: "{group}\SPEI"; Filename: "{app}\utils\SPEI.exe.bat"; WorkingDir: "{app}"
Name: "{group}\SPEI Web Interface"; Filename: "http://localhost:3000"; IconFilename: "{app}\assets\web-icon.ico"
Name: "{group}\Documentação"; Filename: "{app}\docs\index.html"
Name: "{group}\{cm:UninstallProgram,SPEI}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\SPEI"; Filename: "{app}\utils\SPEI.exe.bat"; WorkingDir: "{app}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\SPEI"; Filename: "{app}\utils\SPEI.exe.bat"; WorkingDir: "{app}"; Tasks: quicklaunchicon

[Registry]
Root: HKCU; Subkey: "Software\SPEI"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\SPEI"; ValueType: string; ValueName: "Version"; ValueData: "1.0.0"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "SPEI"; ValueData: """{app}\utils\SPEI.exe.bat"" --minimized"; Tasks: autostart; Flags: uninsdeletevalue

[Run]
; Download and setup runtime components during installation with progress tracking
Filename: "{app}\utils\progress-indicator.bat"; Parameters: """Baixando Python Runtime"" ""1"" ""8"" ""Iniciando download"""; WorkingDir: "{app}"; StatusMsg: "Preparando download do Python..."; Flags: runhidden waituntilterminated
Filename: "{app}\utils\download-python.bat"; WorkingDir: "{app}"; StatusMsg: "Baixando Python runtime (Etapa 1/8)..."; Flags: runhidden waituntilterminated

Filename: "{app}\utils\progress-indicator.bat"; Parameters: """Baixando Node.js Runtime"" ""2"" ""8"" ""Iniciando download"""; WorkingDir: "{app}"; StatusMsg: "Preparando download do Node.js..."; Flags: runhidden waituntilterminated
Filename: "{app}\utils\download-nodejs.bat"; WorkingDir: "{app}"; StatusMsg: "Baixando Node.js runtime (Etapa 2/8)..."; Flags: runhidden waituntilterminated

Filename: "{app}\utils\progress-indicator.bat"; Parameters: """Baixando PostgreSQL Database"" ""3"" ""8"" ""Iniciando download"""; WorkingDir: "{app}"; StatusMsg: "Preparando download do PostgreSQL..."; Flags: runhidden waituntilterminated
Filename: "{app}\utils\download-postgresql.bat"; WorkingDir: "{app}"; StatusMsg: "Baixando PostgreSQL database (Etapa 3/8)..."; Flags: runhidden waituntilterminated

Filename: "{app}\utils\progress-indicator.bat"; Parameters: """Baixando Redis Cache"" ""4"" ""8"" ""Iniciando download"""; WorkingDir: "{app}"; StatusMsg: "Preparando download do Redis..."; Flags: runhidden waituntilterminated
Filename: "{app}\utils\download-redis.bat"; WorkingDir: "{app}"; StatusMsg: "Baixando Redis cache (Etapa 4/8)..."; Flags: runhidden waituntilterminated

; Download and install Visual C++ Redistributables with fallback and progress
Filename: "{app}\utils\progress-indicator.bat"; Parameters: """Instalando Visual C++ Redistributables"" ""5"" ""8"" ""Baixando componentes"""; WorkingDir: "{app}"; StatusMsg: "Preparando Visual C++ Redistributables..."; Flags: runhidden waituntilterminated
Filename: "powershell"; Parameters: "-Command ""try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vc_redist.x64.exe' -OutFile '{tmp}\VC_redist.x64.exe' -UseBasicParsing } catch { certutil -urlcache -split -f 'https://aka.ms/vs/17/release/vc_redist.x64.exe' '{tmp}\VC_redist.x64.exe' }"""; StatusMsg: "Baixando Visual C++ Redistributables (Etapa 5/8)..."; Flags: waituntilterminated runhidden
Filename: "{tmp}\VC_redist.x64.exe"; Parameters: "/quiet /norestart"; StatusMsg: "Instalando Visual C++ Redistributables..."; Flags: waituntilterminated

; Initialize database with progress
Filename: "{app}\utils\progress-indicator.bat"; Parameters: """Inicializando Banco de Dados"" ""6"" ""8"" ""Configurando PostgreSQL"""; WorkingDir: "{app}"; StatusMsg: "Preparando banco de dados..."; Flags: runhidden waituntilterminated
Filename: "{app}\utils\init-database.bat"; WorkingDir: "{app}"; StatusMsg: "Inicializando banco de dados (Etapa 6/8)..."; Flags: waituntilterminated runhidden

; Install Python dependencies with progress
Filename: "{app}\utils\progress-indicator.bat"; Parameters: """Instalando Dependências Python"" ""7"" ""8"" ""Configurando backend"""; WorkingDir: "{app}"; StatusMsg: "Preparando dependências Python..."; Flags: runhidden waituntilterminated
Filename: "{app}\utils\install-dependencies.bat"; WorkingDir: "{app}"; StatusMsg: "Instalando dependências Python (Etapa 7/8)..."; Flags: waituntilterminated runhidden

; Build frontend with progress
Filename: "{app}\utils\progress-indicator.bat"; Parameters: """Construindo Interface Web"" ""8"" ""8"" ""Finalizando instalação"""; WorkingDir: "{app}"; StatusMsg: "Preparando interface web..."; Flags: runhidden waituntilterminated
Filename: "{app}\utils\build-frontend.bat"; WorkingDir: "{app}"; StatusMsg: "Construindo interface web (Etapa 8/8)..."; Flags: waituntilterminated runhidden

; Configure firewall
Filename: "netsh"; Parameters: "advfirewall firewall add rule name=""SPEI API"" dir=in action=allow protocol=TCP localport=8000"; StatusMsg: "Configurando firewall para API..."; Flags: waituntilterminated runhidden; Tasks: firewall
Filename: "netsh"; Parameters: "advfirewall firewall add rule name=""SPEI Web"" dir=in action=allow protocol=TCP localport=3000"; StatusMsg: "Configurando firewall para interface web..."; Flags: waituntilterminated runhidden; Tasks: firewall

; Start services
Filename: "{app}\utils\SPEI.exe.bat"; Description: "{cm:LaunchProgram,SPEI}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; Stop services
Filename: "{app}\utils\stop-services.bat"; WorkingDir: "{app}"; Flags: waituntilterminated runhidden

; Remove firewall rules
Filename: "netsh"; Parameters: "advfirewall firewall delete rule name=""SPEI API"""; Flags: waituntilterminated runhidden
Filename: "netsh"; Parameters: "advfirewall firewall delete rule name=""SPEI Web"""; Flags: waituntilterminated runhidden

[Code]
var
  DatabasePasswordPage: TInputQueryWizardPage;
  AdminUserPage: TInputQueryWizardPage;
  PortConfigPage: TInputQueryWizardPage;

procedure InitializeWizard;
begin
  // Database password configuration page
  DatabasePasswordPage := CreateInputQueryPage(wpSelectComponents,
    'Configuração do Banco de Dados', 'Configure a senha do banco de dados PostgreSQL',
    'Digite uma senha segura para o banco de dados. Esta senha será usada para proteger seus dados médicos.');
  DatabasePasswordPage.Add('Senha do banco de dados:', True);
  DatabasePasswordPage.Values[0] := 'spei2025!';

  // Admin user configuration page
  AdminUserPage := CreateInputQueryPage(DatabasePasswordPage.ID,
    'Configuração do Administrador', 'Configure a conta de administrador do sistema',
    'Digite as informações para a conta de administrador inicial do SPEI.');
  AdminUserPage.Add('Nome do administrador:', False);
  AdminUserPage.Add('Email do administrador:', False);
  AdminUserPage.Add('Senha do administrador:', True);
  AdminUserPage.Values[0] := 'Administrador';
  AdminUserPage.Values[1] := 'admin@spei.local';
  AdminUserPage.Values[2] := 'admin123!';

  // Port configuration page
  PortConfigPage := CreateInputQueryPage(AdminUserPage.ID,
    'Configuração de Portas', 'Configure as portas de rede do sistema',
    'Configure as portas que o SPEI usará para comunicação. Use as portas padrão a menos que haja conflitos.');
  PortConfigPage.Add('Porta da API (backend):', False);
  PortConfigPage.Add('Porta da interface web (frontend):', False);
  PortConfigPage.Add('Porta do banco de dados:', False);
  PortConfigPage.Values[0] := '8000';
  PortConfigPage.Values[1] := '3000';
  PortConfigPage.Values[2] := '5432';
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  Port: Integer;
begin
  Result := True;
  
  if CurPageID = DatabasePasswordPage.ID then
  begin
    if Length(DatabasePasswordPage.Values[0]) < 8 then
    begin
      MsgBox('A senha do banco de dados deve ter pelo menos 8 caracteres.', mbError, MB_OK);
      Result := False;
    end;
  end
  else if CurPageID = AdminUserPage.ID then
  begin
    if (Length(AdminUserPage.Values[0]) = 0) or (Length(AdminUserPage.Values[1]) = 0) or (Length(AdminUserPage.Values[2]) = 0) then
    begin
      MsgBox('Todos os campos do administrador são obrigatórios.', mbError, MB_OK);
      Result := False;
    end
    else if Length(AdminUserPage.Values[2]) < 6 then
    begin
      MsgBox('A senha do administrador deve ter pelo menos 6 caracteres.', mbError, MB_OK);
      Result := False;
    end;
  end
  else if CurPageID = PortConfigPage.ID then
  begin
    // Validate API port
    if not TryStrToInt(PortConfigPage.Values[0], Port) or (Port < 1024) or (Port > 65535) then
    begin
      MsgBox('A porta da API deve ser um número entre 1024 e 65535.', mbError, MB_OK);
      Result := False;
    end
    // Validate web port
    else if not TryStrToInt(PortConfigPage.Values[1], Port) or (Port < 1024) or (Port > 65535) then
    begin
      MsgBox('A porta da interface web deve ser um número entre 1024 e 65535.', mbError, MB_OK);
      Result := False;
    end
    // Validate database port
    else if not TryStrToInt(PortConfigPage.Values[2], Port) or (Port < 1024) or (Port > 65535) then
    begin
      MsgBox('A porta do banco de dados deve ser um número entre 1024 e 65535.', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  EnvFile: string;
  ConfigContent: TArrayOfString;
begin
  if CurStep = ssPostInstall then
  begin
    // Update .env.windows file with user configuration
    EnvFile := ExpandConstant('{app}\config\.env.windows');
    
    if LoadStringsFromFile(EnvFile, ConfigContent) then
    begin
      // Update database password
      StringChangeEx(ConfigContent, 'DB_PASSWORD={{DB_PASSWORD}}',
        'DB_PASSWORD=' + DatabasePasswordPage.Values[0], True);
      
      // Update admin user information
      StringChangeEx(ConfigContent, 'ADMIN_NAME={{ADMIN_NAME}}',
        'ADMIN_NAME=' + AdminUserPage.Values[0], True);
      StringChangeEx(ConfigContent, 'ADMIN_EMAIL={{ADMIN_EMAIL}}',
        'ADMIN_EMAIL=' + AdminUserPage.Values[1], True);
      StringChangeEx(ConfigContent, 'ADMIN_PASSWORD={{ADMIN_PASSWORD}}',
        'ADMIN_PASSWORD=' + AdminUserPage.Values[2], True);
      StringChangeEx(ConfigContent, 'INITIAL_ADMIN_EMAIL={{ADMIN_EMAIL}}',
        'INITIAL_ADMIN_EMAIL=' + AdminUserPage.Values[1], True);
      StringChangeEx(ConfigContent, 'INITIAL_ADMIN_PASSWORD={{ADMIN_PASSWORD}}',
        'INITIAL_ADMIN_PASSWORD=' + AdminUserPage.Values[2], True);
      
      // Update port configuration
      StringChangeEx(ConfigContent, 'API_PORT={{API_PORT}}',
        'API_PORT=' + PortConfigPage.Values[0], True);
      StringChangeEx(ConfigContent, 'FRONTEND_PORT={{WEB_PORT}}',
        'FRONTEND_PORT=' + PortConfigPage.Values[1], True);
      StringChangeEx(ConfigContent, 'DB_PORT={{DB_PORT}}',
        'DB_PORT=' + PortConfigPage.Values[2], True);
      
      SaveStringsToFile(EnvFile, ConfigContent, False);
    end;
  end;
end;

function InitializeUninstall(): Boolean;
begin
  Result := True;
  if MsgBox('Tem certeza de que deseja remover o SPEI e todos os seus dados?', mbConfirmation, MB_YESNO) = IDNO then
    Result := False;
end;
