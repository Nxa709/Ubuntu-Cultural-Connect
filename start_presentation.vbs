' Double-click this file — no terminals will appear
Dim shell, root
Set shell = CreateObject("WScript.Shell")
root = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Start backend (hidden) with PostgreSQL
shell.Run "cmd /c set DATABASE_URL=postgresql://postgres.wrdljjwrigcuhhfipegh:Aug0508205959085%23@aws-1-eu-west-2.pooler.supabase.com:5432/postgres && cd """ & root & "\backend"" && uvicorn main:app --host 127.0.0.1 --port 8001", 0, False

' Wait, then start frontend (hidden)
WScript.Sleep 2000
shell.Run "cmd /c cd """ & root & "\frontend"" && npm run dev", 0, False

' Wait for servers, then open browser
WScript.Sleep 5000
shell.Run "http://localhost:5173", 1, False
