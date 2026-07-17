param()

$ErrorActionPreference = 'Stop'
$kitRoot = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$fontDirectory = Join-Path $kitRoot 'assets\fonts'
$noticeDirectory = Join-Path $kitRoot 'third-party'
$googleFontsCommit = '389b770410cc0b7c21c85673bfa2077420fe7f65'
$baseUrl = "https://raw.githubusercontent.com/google/fonts/$googleFontsCommit/ofl"

New-Item -ItemType Directory -Force -Path $fontDirectory, $noticeDirectory | Out-Null

$downloads = @(
    @{
        Url = "$baseUrl/zcoolkuaile/ZCOOLKuaiLe-Regular.ttf"
        Destination = Join-Path $fontDirectory 'ZCOOLKuaiLe-Regular.ttf'
    },
    @{
        Url = "$baseUrl/notosanssc/NotoSansSC%5Bwght%5D.ttf"
        Destination = Join-Path $fontDirectory 'NotoSansSC-Variable.ttf'
    },
    @{
        Url = "$baseUrl/zcoolkuaile/OFL.txt"
        Destination = Join-Path $noticeDirectory 'ZCOOL-KuaiLe-OFL.txt'
    },
    @{
        Url = "$baseUrl/notosanssc/OFL.txt"
        Destination = Join-Path $noticeDirectory 'Noto-Sans-SC-OFL.txt'
    }
)

foreach ($download in $downloads) {
    Invoke-WebRequest -UseBasicParsing -Uri $download.Url -OutFile $download.Destination
}

$downloads | ForEach-Object {
    $file = Get-Item -LiteralPath $_.Destination
    [PSCustomObject]@{
        File = $file.Name
        Bytes = $file.Length
        Sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $file.FullName).Hash.ToLowerInvariant()
    }
}
