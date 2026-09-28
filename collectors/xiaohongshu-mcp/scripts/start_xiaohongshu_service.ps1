param(
    [int]$WaitSeconds = 20
)

$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path

function Read-RepoEnv([string]$Name) {
    foreach ($filename in @(".env.local", ".env")) {
        $envFile = Join-Path $repo $filename
        if (-not (Test-Path -LiteralPath $envFile)) { continue }
        foreach ($line in Get-Content -LiteralPath $envFile) {
            if ($line -match "^$([regex]::Escape($Name))=(.*)$") {
                return $Matches[1].Trim().Trim('"').Trim("'")
            }
        }
    }
    return $null
}

function Read-Setting([string]$Name, [string]$Default = "") {
    $value = [Environment]::GetEnvironmentVariable($Name)
    if (-not $value) {
        $value = Read-RepoEnv $Name
    }
    if ($value) { return $value }
    return $Default
}

$endpoint = Read-Setting "XHS_MCP_ENDPOINT" "http://127.0.0.1:18063"
$uri = [Uri]$endpoint
if ($uri.Scheme -ne "http" -or $uri.Host -notin @("127.0.0.1", "localhost", "::1") -or $uri.IsDefaultPort) {
    throw "XHS_MCP_ENDPOINT 必须是包含端口的本机 HTTP 地址"
}

try {
    $health = Invoke-RestMethod -Uri "$($endpoint.TrimEnd('/'))/health" -TimeoutSec 3
    if ($health.success -and $health.data.status -eq "healthy") {
        [pscustomobject]@{ Status = "already-running"; Endpoint = $endpoint }
        exit 0
    }
} catch {
    # Start the configured local service below.
}

$binary = Read-Setting "XHS_MCP_BINARY"
if (-not $binary) {
    throw "服务未运行；请通过 XHS_MCP_BINARY 配置实验版 xiaohongshu-mcp 二进制"
}
$binary = [Environment]::ExpandEnvironmentVariables($binary)
$binary = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($binary)
if (-not (Test-Path -LiteralPath $binary -PathType Leaf)) {
    throw "XHS_MCP_BINARY 不存在: $binary"
}

$cookiePath = Read-Setting "XHS_MCP_COOKIES_PATH" (Join-Path $HOME ".xhs-autopilot\xiaohongshu-mcp\cookies.json")
$cookiePath = [Environment]::ExpandEnvironmentVariables($cookiePath)
$cookiePath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($cookiePath)
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $cookiePath) | Out-Null
$env:COOKIES_PATH = $cookiePath

$logDir = Join-Path $repo "social-work\xiaohongshu-mcp"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

# Some Windows agent hosts inject both Path and PATH. Start-Process rejects that
# environment block, so normalize only this PowerShell process before spawning.
$processPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Process)
[Environment]::SetEnvironmentVariable("PATH", $null, [EnvironmentVariableTarget]::Process)
[Environment]::SetEnvironmentVariable("Path", $processPath, [EnvironmentVariableTarget]::Process)

$process = Start-Process -FilePath $binary `
    -ArgumentList "-port", ":$($uri.Port)", "-headless=true" `
    -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $logDir "service.stdout.log") `
    -RedirectStandardError (Join-Path $logDir "service.stderr.log") `
    -PassThru

$deadline = (Get-Date).AddSeconds($WaitSeconds)
while ((Get-Date) -lt $deadline) {
    if ($process.HasExited) {
        throw "xiaohongshu-mcp 启动失败，退出码 $($process.ExitCode)"
    }
    try {
        $health = Invoke-RestMethod -Uri "$($endpoint.TrimEnd('/'))/health" -TimeoutSec 3
        if ($health.success -and $health.data.status -eq "healthy") {
            [pscustomobject]@{ Status = "started"; Endpoint = $endpoint; Pid = $process.Id }
            exit 0
        }
    } catch {
        Start-Sleep -Milliseconds 500
    }
}

Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
throw "xiaohongshu-mcp 未在 $WaitSeconds 秒内通过健康检查"
