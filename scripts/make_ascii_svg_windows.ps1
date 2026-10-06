param(
  [string]$Source = "source-photo.jpg",
  [string]$Output = "profile-ascii.svg"
)

# Windows fallback for the first local render when Python is unavailable.
# The canonical cross-platform generator remains make_ascii_svg.py.
Add-Type -AssemblyName System.Drawing
$profile = Get-Content profile.json -Raw | ConvertFrom-Json
$image = [System.Drawing.Bitmap]::new((Resolve-Path $Source).Path)
$columns = 120
$rows = [Math]::Round($columns * 8 / 15)
$ramp = " .`:-=+*#%@"
$cellWidth = 800.0 / $columns
$cellHeight = $cellWidth * 15 / 8
$sb = [System.Text.StringBuilder]::new()
$null = $sb.Append('<svg xmlns="http://www.w3.org/2000/svg" width="840" height="880" viewBox="0 0 840 880" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">')
$null = $sb.Append('<rect width="840" height="880" rx="12" fill="#0d1117"/><rect x=".5" y=".5" width="839" height="879" rx="12" fill="none" stroke="#30363d"/>')
$null = $sb.Append('<line x1="0" y1="30" x2="840" y2="30" stroke="#30363d"/>')
foreach ($item in @(@("#ff5f56",20), @("#ffbd2e",36), @("#27c93f",52))) { $null = $sb.Append("<circle cx=`"$($item[1])`" cy=`"15`" r=`"5`" fill=`"$($item[0])`"/>") }
$handle = [System.Security.SecurityElement]::Escape([string]$profile.terminal_user)
$name = [System.Security.SecurityElement]::Escape([string]$profile.display_name)
$null = $sb.Append("<text x=`"420`" y=`"19`" fill=`"#7d8590`" font-size=`"12`" text-anchor=`"middle`">$handle@github: ~$ ./portrait.sh</text>")
$rowDuration = 5.8 / $rows
for ($y = 0; $y -lt $rows; $y++) {
  $chars = [System.Text.StringBuilder]::new()
  for ($x = 0; $x -lt $columns; $x++) {
    $pixel = $image.GetPixel([Math]::Min($image.Width - 1, [Math]::Floor(($x + .5) * $image.Width / $columns)), [Math]::Min($image.Height - 1, [Math]::Floor(($y + .5) * $image.Height / $rows)))
    $lum = [Math]::Pow((.299 * $pixel.R + .587 * $pixel.G + .114 * $pixel.B) / 255, 1.18)
    $index = if ($lum -ge .82) { 0 } else { [Math]::Max(0, [Math]::Min($ramp.Length - 1, [Math]::Round((1 - $lum) * ($ramp.Length - 1)))) }
    $null = $chars.Append($ramp[$index])
  }
  $line = [System.Security.SecurityElement]::Escape($chars.ToString())
  $top = 34 + $y * $cellHeight
  $baseline = $top + $cellHeight * .74
  $delay = [Math]::Round($y * $rowDuration, 3)
  $null = $sb.Append("<clipPath id=`"r$y`"><rect x=`"20`" y=`"$([Math]::Round($top,1))`" height=`"$([Math]::Round($cellHeight,1))`" width=`"0`"><animate attributeName=`"width`" from=`"0`" to=`"800`" begin=`"${delay}s`" dur=`"$([Math]::Round($rowDuration,2))s`" fill=`"freeze`"/></rect></clipPath>")
  $null = $sb.Append("<text xml:space=`"preserve`" clip-path=`"url(#r$y)`" x=`"20`" y=`"$([Math]::Round($baseline,1))`" fill=`"#c9d1d9`" font-size=`"$([Math]::Round($cellHeight*.86,1))`" textLength=`"800`" lengthAdjust=`"spacing`">$line</text>")
}
$null = $sb.Append("<line x1=`"0`" y1=`"850`" x2=`"840`" y2=`"850`" stroke=`"#30363d`"/><text x=`"20`" y=`"870`" fill=`"#7d8590`" font-size=`"13`">$handle@github:~$ whoami <tspan fill=`"#c9d1d9`">$name</tspan></text></svg>")
$image.Dispose()
[System.IO.File]::WriteAllText((Join-Path (Get-Location) $Output), $sb.ToString(), [System.Text.UTF8Encoding]::new($false))
Write-Output "wrote $Output"
