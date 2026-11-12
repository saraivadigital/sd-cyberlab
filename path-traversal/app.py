"""
SD CyberLab — Path Traversal / LFI
"""
import os
from flask import Flask, request, Response

app = Flask(__name__)

BASE_DIR = "/app/files"
os.makedirs(BASE_DIR, exist_ok=True)

with open(f"{BASE_DIR}/readme.txt", "w") as f:
    f.write("Bem-vindo ao SD CyberLab File Server!\nEste é um arquivo público.\n")
with open(f"{BASE_DIR}/manual.txt", "w") as f:
    f.write("Manual do Sistema v2.4\nAcesse /files?name=readme.txt para ler arquivos.\n")
with open(f"{BASE_DIR}/missoes.txt", "w") as f:
    f.write("Missão 001: Entregar pacote para Chewbacana na Base Hoth.\nMissão 002: Encontrar R2-Dadinho em Tatooine.\n")
with open("/app/secret.txt", "w") as f:
    f.write("SDC_Flag{P4th_Tr4v3rs4l_LF1_Succ3ss}\nSenha do hangar: HAN-SOLO-7731!\n")
with open("/app/config.ini", "w") as f:
    f.write("[database]\nhost=172.17.1.10\nuser=admin\npassword=D4rth_DB_2024!\n\n[app]\nsecret_key=cyberlab_ultra_secret\n")

STYLE = """<style>
    *{box-sizing:border-box}
    body{font-family:monospace;background:#0d1117;color:#c9d1d9;padding:2rem;margin:0}
    .brand{display:flex;align-items:center;gap:.5rem;font-size:1.4rem;font-weight:bold;color:#e3b341;margin-bottom:.4rem;letter-spacing:.03em}
    .brand span{font-size:1.6rem}
    h1{color:#e3b341;margin-top:0;font-size:1.3rem}
    h2{color:#8b949e;font-size:.95rem;margin-bottom:.5rem;text-transform:uppercase;letter-spacing:.06em}
    code{background:#161b22;padding:2px 7px;border-radius:4px;display:block;margin:4px 0;font-size:.9rem}
    .box{background:#161b22;border:1px solid #30363d;padding:1rem 1.2rem;margin:1rem 0;border-radius:6px}
    a{color:#e3b341}
    pre{background:#010409;padding:1rem;border-radius:4px;overflow-x:auto;color:#e3b341;white-space:pre-wrap}
    li{margin:5px 0}.err{color:#f85149}
    .dica{border-left:3px solid #e3b341;padding:.5rem 1rem;background:#1a1600;border-radius:0 4px 4px 0;color:#e3b341;margin-top:.5rem}
    .formato{color:#8b949e;font-size:.85rem;margin-top:.4rem}
</style>"""

PAGE_TOP = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>🛡️ SD CyberLab: 📁 Lab Path Traversal — File Server</title>
  """ + STYLE + """
</head>
<body>
  <div class="brand"><span>🛡️</span> SD CyberLab</div>
  <h1>📁 Lab Path Traversal — File Server</h1>
  <div class="box">
    <h2>Situação</h2>
    <p>Servidor de arquivos que lê de <code>/app/files/</code> sem normalizar o caminho.</p>
    <p>Arquivos públicos:
      <a href="/files?name=readme.txt">readme.txt</a> |
      <a href="/files?name=manual.txt">manual.txt</a> |
      <a href="/files?name=missoes.txt">missoes.txt</a>
    </p>
  </div>
  <div class="box">
    <h2>Payloads para testar</h2>
    <ul>
      <li><code>/files?name=../../etc/passwd</code></li>
      <li><code>/files?name=....//....//etc/passwd</code> (bypass de filtro)</li>
      <li><code>/files?name=%2e%2e%2f%2e%2e%2fetc/passwd</code> (URL encoded)</li>
    </ul>
    <div class="dica">
      💡 <strong>Dica:</strong> você consegue sair do diretório <code>/app/files/</code>?
      Aplicações costumam guardar arquivos de configuração e segredos um nível acima do diretório público.
      <div class="formato">Formato da flag: <code>SDC_Flag{...}</code></div>
    </div>
  </div>
"""
PAGE_BOTTOM = "</body></html>"

@app.route("/")
def index():
    return Response(PAGE_TOP + PAGE_BOTTOM, mimetype="text/html")

@app.route("/files")
def read_file():
    name = request.args.get("name", "")
    if not name:
        html = PAGE_TOP + '<div class="box"><p class="err">Parâmetro "name" obrigatório.</p></div>' + PAGE_BOTTOM
        return Response(html, mimetype="text/html")
    path = os.path.join(BASE_DIR, name)  # ❌ sem normalização
    try:
        with open(path, "r") as f:
            content = f.read()
        safe_path = path.replace("&","&amp;").replace("<","&lt;")
        html = PAGE_TOP + '<div class="box"><h2>📄 ' + safe_path + '</h2><pre>' + content + '</pre></div>' + PAGE_BOTTOM
    except FileNotFoundError:
        safe_path = path.replace("&","&amp;").replace("<","&lt;")
        html = PAGE_TOP + '<div class="box"><p class="err">Arquivo não encontrado: ' + safe_path + '</p></div>' + PAGE_BOTTOM
    except Exception as e:
        html = PAGE_TOP + '<div class="box"><p class="err">' + str(e) + '</p></div>' + PAGE_BOTTOM
    return Response(html, mimetype="text/html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
