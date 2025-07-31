' Ejecución en segundo plano del backend Python.
' Inicio automático mediante acceso directo colocado en
' C:\Users\<Usuario>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c python ""D:\Curso de JavaScript\rss-backend\backend.py""", 0
