$composeFile = @(
    "compose.yaml",
    "compose.yml",
    "docker-compose.yaml",
    "docker-compose.yml"
) | Where-Object {
    Test-Path $_
} | Select-Object -First 1

if (!$composeFile) {
    throw "Docker Compose configuration not found."
}

docker compose `
    -f $composeFile `
    -f compose.maintenance.yaml `
    -f compose.ml.yaml `
    stop
