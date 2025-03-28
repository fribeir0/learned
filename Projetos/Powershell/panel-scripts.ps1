$menu = @"
Escolha qual script deseja rodar:
1. Script 1 - Adicionar Usuarios em Grupos em lista (users.txt)
2. Script 2 - LastLogin Check X minutos
3. Script 3 - Desativar varios usuarios em lista (disable.txt)
4. Sair
"@

Write-Host $menu

$opcao = Read-Host "Digite o numero da opcao desejada"

switch ($opcao) {
    1 {
        Write-Host "Rodando Script 1 - Desativar usuários inativos..."
        $Domain = "fribeiro.local"


        $NewUSR = "C:\users\Administrator\Documents\users.txt"


        Get-Content $NewUSR | ForEach-Object {
            $data = $_ -split ","
            $first = $data[0]
            $last = $data[1]
            $depart = $data[2]
            $logon = $data[3]
            $password = "teste@134"
            $OU = "OU=Users,DC=fribeiro,DC=local"
            $userDetail = @{
                GivenName = $first
                Surname = $last
                Name = "$first $last"
                SamAccountName = $logon
                UserPrincipalName = "$logon@$Domain"
                AccountPassword = (ConvertTo-SecureString -AsPlainText $password -Force)
                Enabled = $true
                ChangePasswordAtLogon = $true
            }


            if (-not (Get-ADGroup -Filter { Name -eq $depart })) {
                New-ADGroup -Name $depart -GroupScope Global -GroupCategory Security -Description "Grupo do departamento $depart"
                Write-Host "Novo grupo criado: $depart" -ForegroundColor Green
            }


            try {
                New-ADUser @userDetail -PassThru | Out-Null
                Write-Host "Usuario $logon criado com sucesso!" -ForegroundColor Green


                Add-ADGroupMember -Identity $depart -Members $logon
                Write-Host "Usuario $logon adicionado ao grupo $depart." -ForegroundColor Green
            } catch {
                Write-Host "Deu erro ao criar o usuario ou adiciona-lo ao grupo: $_" -ForegroundColor Red
            }
        }

        break
    }
    2 {
        Write-Host "Rodando Script 2 - LastLogin Checks..."
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

        break
    }
    3 {
        Write-Host "Rodando Script 3 - Desativando varios usuarios..."
        $disableUSR = "C:\users\administrator\documents\disable.txt"
        $time = Get-Date -Format "yyyy-MM-dd-HHmm"
        $log = "C:\users\administrator\documents\log_$time.txt"

        Add-Content -Path $log -Value "===== Log de Desativação - $time ====="

        Get-Content $disableUSR | ForEach-Object {
            $user = $_.Trim()
            $hora = Get-Date -Format "HH:mm:ss"

            if (Get-ADUser -Filter { Name -eq $user }) {
                Disable-ADAccount -Identity $user
                $msg = "[$hora] Usuario $user desativado com sucesso."
            } else {
                $msg = "[$hora] ERRO: O usuario $user nao existe."
            }

            Write-Host $msg
            Add-Content -Path $log -Value $msg
        }

        Write-Host "Log gerado em: $log"
        break
    }
    4 {
        Write-Host "Saindo do painel..."
        break
    }
    default {
        Write-Host "Opçao invalida, tente novamente."
    }
}

Write-Host "Obrigado por usar o painel! Ate logo!"
