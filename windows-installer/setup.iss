[Setup]
AppName=SPEI - Sistema de Prontuário Eletrônico Inteligente
AppVersion=1.0.0
AppPublisher=CardioAI Pro
AppPublisherURL=https://spei.med.br
AppSupportURL=https://spei.med.br/support
AppUpdatesURL=https://spei.med.br/updates
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
MinVersion=10.0.17763

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"

[Types]
Name: "full"; Description: "Instalação Completa (Recomendado)"
Name: "compact"; Description: "Instalação Compacta"
Name: "custom"; Description: "Instalação Personalizada"; Flags: iscustom

[Components]
Name: "core"; Description: "Sistema Principal SPEI"; Types: full compact custom; Flags: fixed
Name: "database"; Description: "Banco de Dados PostgreSQL"; Types: full compact custom; Flags: fixed
Name: "ai"; Description: "Módulos de Inteligência Artificial"; Types: full custom
Name: "samples"; Description: "Dados de Exemplo"; Types: full
Name: "docs"; Description: "Documentação"; Types: full

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1
Name: "firewall"; Description: "Configurar Firewall do Windows"; GroupDescription: "Configurações de Rede"
Name: "autostart"; Description: "Iniciar SPEI automaticamente com o Windows"; GroupDescription: "Configurações de Sistema"

[Files]
; Core application files
Source: "runtime\python\*"; DestDir: "{app}\runtime\python"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core
Source: "runtime\nodejs\*"; DestDir: "{app}\runtime\nodejs"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core
Source: "runtime\postgresql\*"; DestDir: "{app}\runtime\postgresql"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: database
Source: "runtime\redis\*"; DestDir: "{app}\runtime\redis"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core

; Application source code
Source: "..\backend\*"; DestDir: "{app}\backend"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core
Source: "..\frontend\*"; DestDir: "{app}\frontend"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core

; Configuration files
Source: "config\.env.windows"; DestDir: "{app}"; DestName: ".env"; Flags: ignoreversion; Components: core

; AI Models (commented out - models directory not available in repository)
; Source: "models\*"; DestDir: "{app}\models"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: ai

; Sample data (commented out - samples directory not available in repository)
; Source: "samples\*"; DestDir: "{app}\samples"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: samples

; Documentation
Source: "docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: docs

; Utilities and scripts
Source: "utils\*"; DestDir: "{app}\utils"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core

; Visual C++ Redistributables
Source: "redist\VC_redist.x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
Name: "{group}\SPEI"; Filename: "{app}\utils\SPEI.bat"; WorkingDir: "{app}"
Name: "{group}\SPEI Web Interface"; Filename: "http://localhost:3000"; IconFilename: "{app}\assets\web-icon.ico"
Name: "{group}\Documentação"; Filename: "{app}\docs\index.html"
Name: "{group}\{cm:UninstallProgram,SPEI}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\SPEI"; Filename: "{app}\utils\SPEI.bat"; WorkingDir: "{app}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\SPEI"; Filename: "{app}\utils\SPEI.bat"; WorkingDir: "{app}"; Tasks: quicklaunchicon

[Registry]
Root: HKCU; Subkey: "Software\SPEI"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\SPEI"; ValueType: string; ValueName: "Version"; ValueData: "1.0.0"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "SPEI"; ValueData: """{app}\utils\SPEI.bat"" --minimized"; Tasks: autostart; Flags: uninsdeletevalue

[Run]
; Install Visual C++ Redistributables
Filename: "{tmp}\VC_redist.x64.exe"; Parameters: "/quiet /norestart"; StatusMsg: "Instalando Visual C++ Redistributables..."; Flags: waituntilterminated

; Initialize database
Filename: "{app}\utils\init-database.bat"; WorkingDir: "{app}"; StatusMsg: "Inicializando banco de dados..."; Flags: waituntilterminated runhidden

; Install Python dependencies
Filename: "{app}\utils\install-dependencies.bat"; WorkingDir: "{app}"; StatusMsg: "Instalando dependências Python..."; Flags: waituntilterminated runhidden

; Build frontend
Filename: "{app}\utils\build-frontend.bat"; WorkingDir: "{app}"; StatusMsg: "Construindo interface web..."; Flags: waituntilterminated runhidden

; Configure firewall
Filename: "netsh"; Parameters: "advfirewall firewall add rule name=""SPEI API"" dir=in action=allow protocol=TCP localport=8000"; StatusMsg: "Configurando firewall..."; Flags: waituntilterminated runhidden; Tasks: firewall
Filename: "netsh"; Parameters: "advfirewall firewall add rule name=""SPEI Web"" dir=in action=allow protocol=TCP localport=3000"; StatusMsg: "Configurando firewall..."; Flags: waituntilterminated runhidden; Tasks: firewall

; Start services
Filename: "{app}\utils\SPEI.bat"; Description: "{cm:LaunchProgram,SPEI}"; Flags: nowait postinstall skipifsilent

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
  // Database configuration page
  DatabasePasswordPage := CreateInputQueryPage(wpSelectComponents,
    'Configuração do Banco de Dados', 'Configure a senha do banco de dados',
    'Por favor, defina uma senha segura para o banco de dados PostgreSQL:');
  DatabasePasswordPage.Add('Senha do banco de dados:', True);
  DatabasePasswordPage.Values[0] := 'spei_secure_' + IntToStr(Random(9999));

  // Admin user configuration page
  AdminUserPage := CreateInputQueryPage(DatabasePasswordPage.ID,
    'Usuário Administrador', 'Configure o usuário administrador do sistema',
    'Defina as credenciais do usuário administrador:');
  AdminUserPage.Add('Email do administrador:', False);
  AdminUserPage.Add('Senha do administrador:', True);
  AdminUserPage.Values[0] := 'admin@hospital.local';
  AdminUserPage.Values[1] := 'Admin123!';

  // Port configuration page
  PortConfigPage := CreateInputQueryPage(AdminUserPage.ID,
    'Configuração de Portas', 'Configure as portas de rede',
    'Defina as portas que o sistema utilizará:');
  PortConfigPage.Add('Porta da API (padrão: 8000):', False);
  PortConfigPage.Add('Porta da Interface Web (padrão: 3000):', False);
  PortConfigPage.Values[0] := '8000';
  PortConfigPage.Values[1] := '3000';
end;

function NextButtonClick(CurPageID: Integer): Boolean;
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
    if (Length(AdminUserPage.Values[0]) = 0) or (Length(AdminUserPage.Values[1]) < 6) then
    begin
      MsgBox('Por favor, preencha o email e defina uma senha com pelo menos 6 caracteres.', mbError, MB_OK);
      Result := False;
    end;
  end
  else if CurPageID = PortConfigPage.ID then
  begin
    if (StrToIntDef(PortConfigPage.Values[0], 0) <= 1024) or 
       (StrToIntDef(PortConfigPage.Values[1], 0) <= 1024) then
    begin
      MsgBox('As portas devem ser números maiores que 1024.', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ConfigFile: string;
  ConfigContent: TStringList;
begin
  if CurStep = ssPostInstall then
  begin
    // Update configuration file with user settings
    ConfigFile := ExpandConstant('{app}\.env');
    ConfigContent := TStringList.Create;
    try
      ConfigContent.LoadFromFile(ConfigFile);
      
      // Replace placeholders with actual values
      StringChangeEx(ConfigContent.Text, '{{DB_PASSWORD}}', DatabasePasswordPage.Values[0], True);
      StringChangeEx(ConfigContent.Text, '{{ADMIN_EMAIL}}', AdminUserPage.Values[0], True);
      StringChangeEx(ConfigContent.Text, '{{ADMIN_PASSWORD}}', AdminUserPage.Values[1], True);
      StringChangeEx(ConfigContent.Text, '{{API_PORT}}', PortConfigPage.Values[0], True);
      StringChangeEx(ConfigContent.Text, '{{WEB_PORT}}', PortConfigPage.Values[1], True);
      
      ConfigContent.SaveToFile(ConfigFile);
    finally
      ConfigContent.Free;
    end;
  end;
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := False;
  // Skip configuration pages in silent mode
  if (PageID = DatabasePasswordPage.ID) or 
     (PageID = AdminUserPage.ID) or 
     (PageID = PortConfigPage.ID) then
    Result := WizardSilent;
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  
  // Check Windows version
  if not IsWin64 then
  begin
    MsgBox('SPEI requer Windows 64-bit. A instalação será cancelada.', mbError, MB_OK);
    Result := False;
    Exit;
  end;
  
  // Check available disk space (minimum 2GB)
  if GetSpaceOnDisk(ExpandConstant('{app}'), False, nil, nil, nil) < 2147483648 then
  begin
    MsgBox('Espaço insuficiente em disco. São necessários pelo menos 2GB livres.', mbError, MB_OK);
    Result := False;
    Exit;
  end;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  Result := '';
  NeedsRestart := False;
  
  // Check if ports are available
  if IsPortInUse(StrToInt(PortConfigPage.Values[0])) then
  begin
    Result := 'A porta ' + PortConfigPage.Values[0] + ' já está em uso. Por favor, escolha outra porta.';
    Exit;
  end;
  
  if IsPortInUse(StrToInt(PortConfigPage.Values[1])) then
  begin
    Result := 'A porta ' + PortConfigPage.Values[1] + ' já está em uso. Por favor, escolha outra porta.';
    Exit;
  end;
end;

function IsPortInUse(Port: Integer): Boolean;
var
  ResultCode: Integer;
begin
  Result := False;
  if Exec('netstat', '-an | findstr :' + IntToStr(Port), '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
    Result := (ResultCode = 0);
end;
