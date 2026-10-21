# PowerShell Script to Set Up Weekly Automated Master TxDOT Synchronization
# Runs every Monday at 8:00 AM on your Windows PC

$taskName = "Amestx_Weekly_TxDOT_Master_Sync"
$action = New-ScheduledTaskAction -Execute "python.exe" -Argument "C:\Users\fibrg\Desktop\Amestx Estimator App\backend\sync_txdot_master.py" -WorkingDirectory "C:\Users\fibrg\Desktop\Amestx Estimator App\backend"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 8:00AM
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Runs weekly master synchronization for Amestx TxDOT letting schedules, dates, and estimates against official TxDOT databases." -Force

Write-Host "✅ Successfully scheduled weekly master TxDOT sync task!" -ForegroundColor Green
Write-Host "The master synchronizer will run automatically every Monday at 8:00 AM." -ForegroundColor Yellow

