Add-Type -AssemblyName System.Speech
$lumaSpeech = New-Object System.Speech.Synthesis.SpeechSynthesizer
$lumaSpeech.SelectVoice('Microsoft Zira Desktop')
$lumaSpeech.Rate = 1
$lumaAudio = Join-Path (Split-Path $PSScriptRoot) 'audio\hi.wav'
$lumaSpeech.SetOutputToWaveFile($lumaAudio)
$lumaSpeech.Speak('Hi!')
$lumaSpeech.Dispose()
