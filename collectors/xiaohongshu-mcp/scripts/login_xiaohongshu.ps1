param()

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

$binary = $env:XHS_MCP_LOGIN_BINARY
if (-not $binary) { $binary = Read-RepoEnv "XHS_MCP_LOGIN_BINARY" }
if (-not $binary) { throw "请通过 XHS_MCP_LOGIN_BINARY 配置本机登录程序" }
$binary = [Environment]::ExpandEnvironmentVariables($binary)
$binary = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($binary)
if (-not (Test-Path -LiteralPath $binary -PathType Leaf)) { throw "登录程序不存在: $binary" }

$cookiePath = $env:XHS_MCP_COOKIES_PATH
if (-not $cookiePath) { $cookiePath = Read-RepoEnv "XHS_MCP_COOKIES_PATH" }
if (-not $cookiePath) { $cookiePath = Join-Path $HOME ".xhs-autopilot\xiaohongshu-mcp\cookies.json" }
$cookiePath = [Environment]::ExpandEnvironmentVariables($cookiePath)
$cookiePath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($cookiePath)
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $cookiePath) | Out-Null
$env:COOKIES_PATH = $cookiePath

Write-Host "即将打开小红书登录窗口。请扫码；仅保存登录态，不执行点赞、收藏、评论或发布。"
& $binary
exit $LASTEXITCODE
