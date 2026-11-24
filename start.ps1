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
    config --quiet

if ($LASTEXITCODE -ne 0) {
    throw "Docker Compose configuration is invalid."
}

docker compose `
    -f $composeFile `
    -f compose.maintenance.yaml `
    -f compose.ml.yaml `
    up -d --build

if ($LASTEXITCODE -ne 0) {
    throw "Docker startup failed."
}

docker compose `
    -f $composeFile `
    -f compose.maintenance.yaml `
    -f compose.ml.yaml `
    ps
