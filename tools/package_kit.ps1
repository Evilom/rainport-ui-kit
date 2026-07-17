$ErrorActionPreference = "Stop"

$KitRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$WorkspaceRoot = (Resolve-Path (Join-Path $KitRoot "..\..")).Path
$OutputRoot = [IO.Path]::GetFullPath((Join-Path $WorkspaceRoot "output\rainport-ui-kit"))
$StagingRoot = [IO.Path]::GetFullPath((Join-Path $OutputRoot "staging"))

function Assert-WithinWorkspace {
    param([Parameter(Mandatory = $true)][string]$Target)

    $workspacePrefix = [IO.Path]::GetFullPath($WorkspaceRoot).TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
    $resolvedTarget = [IO.Path]::GetFullPath($Target)
    if (-not $resolvedTarget.StartsWith($workspacePrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to modify a path outside the workspace: $resolvedTarget"
    }
}

function Get-Sha256 {
    param([Parameter(Mandatory = $true)][string]$Target)

    $Stream = [IO.File]::OpenRead($Target)
    $Algorithm = [Security.Cryptography.SHA256]::Create()
    try {
        return ([BitConverter]::ToString($Algorithm.ComputeHash($Stream))).Replace("-", "").ToLowerInvariant()
    }
    finally {
        $Algorithm.Dispose()
        $Stream.Dispose()
    }
}

Assert-WithinWorkspace -Target $OutputRoot
Assert-WithinWorkspace -Target $StagingRoot

New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
if (Test-Path -LiteralPath $StagingRoot) {
    Remove-Item -LiteralPath $StagingRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $StagingRoot -Force | Out-Null

$SourceStage = Join-Path $StagingRoot "source"
$UnityStage = Join-Path $StagingRoot "unity"
$GodotStage = Join-Path $StagingRoot "godot"
$CocosStage = Join-Path $StagingRoot "cocos"

New-Item -ItemType Directory -Path $SourceStage, $UnityStage, $GodotStage, $CocosStage -Force | Out-Null

Copy-Item -LiteralPath $KitRoot -Destination (Join-Path $SourceStage "rainport-ui-kit") -Recurse
Copy-Item -LiteralPath (Join-Path $KitRoot "adapters\unity") -Destination (Join-Path $UnityStage "com.rainport.ui") -Recurse
Copy-Item -LiteralPath (Join-Path $KitRoot "adapters\godot") -Destination (Join-Path $GodotStage "rainport-ui-godot") -Recurse
Copy-Item -LiteralPath (Join-Path $KitRoot "adapters\cocos") -Destination (Join-Path $CocosStage "rainport-ui-cocos") -Recurse

$Archives = @(
    @{ Source = (Join-Path $SourceStage "rainport-ui-kit"); Target = (Join-Path $OutputRoot "rainport-ui-kit-source.zip") },
    @{ Source = (Join-Path $UnityStage "com.rainport.ui"); Target = (Join-Path $OutputRoot "rainport-ui-kit-unity.zip") },
    @{ Source = (Join-Path $GodotStage "rainport-ui-godot"); Target = (Join-Path $OutputRoot "rainport-ui-kit-godot.zip") },
    @{ Source = (Join-Path $CocosStage "rainport-ui-cocos"); Target = (Join-Path $OutputRoot "rainport-ui-kit-cocos.zip") }
)

foreach ($Archive in $Archives) {
    Assert-WithinWorkspace -Target $Archive.Target
    Compress-Archive -LiteralPath $Archive.Source -DestinationPath $Archive.Target -CompressionLevel Optimal -Force
}

$HashLines = foreach ($Archive in $Archives) {
    "{0}  {1}" -f (Get-Sha256 -Target $Archive.Target), (Split-Path -Leaf $Archive.Target)
}
$HashPath = Join-Path $OutputRoot "SHA256SUMS.txt"
Assert-WithinWorkspace -Target $HashPath
$HashLines | Set-Content -LiteralPath $HashPath -Encoding utf8

Remove-Item -LiteralPath $StagingRoot -Recurse -Force

$Result = foreach ($Archive in $Archives) {
    $File = Get-Item -LiteralPath $Archive.Target
    [ordered]@{
        file = $File.Name
        bytes = $File.Length
        sha256 = Get-Sha256 -Target $File.FullName
    }
}

[ordered]@{
    output = $OutputRoot
    archives = $Result
} | ConvertTo-Json -Depth 4
