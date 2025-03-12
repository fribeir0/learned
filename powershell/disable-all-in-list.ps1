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
