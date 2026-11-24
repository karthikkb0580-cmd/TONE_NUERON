$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

$backupName = "tone_neuron_$timestamp.dump"

$backupPath = "backups/$backupName"

docker exec tone_neuron_postgres pg_dump `
    -U tone_neuron `
    -d tone_neuron_db `
    -Fc `
    -f "/tmp/$backupName"

if ($LASTEXITCODE -ne 0) {
    throw "Database backup failed."
}

docker cp "tone_neuron_postgres:/tmp/$backupName" $backupPath

if ($LASTEXITCODE -ne 0) {
    throw "Unable to copy database backup."
}

docker exec tone_neuron_postgres rm "/tmp/$backupName"

Write-Host "Database backup created: $backupPath"
