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
