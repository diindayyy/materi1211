# sesi7/pythonanywhere_wsgi.py — CONTOH isi file WSGI di PythonAnywhere (tab Web → WSGI configuration file)
# Salin seluruh isi file ini ke file WSGI di PythonAnywhere, lalu ganti USERNAME dengan username Anda.
import sys

# Folder sesi7 hasil git clone, agar latihan_sesi7.py bisa di-import
path = "/home/USERNAME/materi1211/sesi7"
if path not in sys.path:
    sys.path.insert(0, path)

# PythonAnywhere mencari variabel bernama "application" (objek Flask di balik Dash)
from latihan_sesi7 import server as application  # noqa: E402,F401
