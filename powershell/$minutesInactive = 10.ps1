$minutesInactive = Read-host "Deseja verificar os ultimo login ha quantos minutos?"
$time = (Get-Date).AddMinutes(-$minutesInactive)
$log = "C:\users\administrator\documents\usuarios_inativos_$(Get-Date -Format 'yyyy-MM-dd-HHmm').txt"

$usuariosInativos = Get-ADUser -Filter {LastLogonDate -lt $time} -Properties LastLogonDate | 
Select-Object Name, LastLogonDate

$usuariosInativos | Format-Table Name, LastLogonDate

$usuariosInativos | Select-Object Name, LastLogonDate | Out-File $log

Write-Host "Usuarios inativos ha mais de $minutesInactive minutos salvos em: $log"

$usuariosInativos | ForEach-Object {
    $usuario = $_.Name
    $confirmacao = Read-Host "Deseja realizar alguma acao com o usuario: $usuario? (Sim/Nao)"

   if ($confirmacao -eq "Sim") {
        $conf2 = Read-Host "Deseja desativar o usuario $usuario ou deixa-lo inativo? (Desativar/Remover)"
        
        if ($conf2 -eq "Desativar") {
            Disable-ADAccount -Identity $usuario
            Write-Host "Usuario $usuario desativado."
        }
        elseif ($conf2 -eq "Remover") {
            Remove-ADUser -Identity $usuario
            Write-Host "Usuario $usuario removido."
        }
        else {
            Write-Host "Input incorreto, tente novamente."
        }
    } 
    else {
        Write-Host "Usuario $usuario não foi desativado ou removido."
    }
}
