cd "$env:USERPROFILE\Documents\Unreal-Projects\rumor-unreal-server"
.\venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload
Read-Host -Prompt "Press Enter to exit"