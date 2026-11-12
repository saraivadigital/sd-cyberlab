"""
SD CyberLab — Command Injection
"""
import subprocess
from flask import Flask, request, Response

app = Flask(__name__)

with open("/tmp/flag.txt", "w") as f:
    f.write("SDC_Flag{CMD1_0S_C0mm4nd_1nj3ct10n}\n")

STYLE = """<style>
    *{box-sizing:border-box}
    body{font-family:monospace;background:#0d1117;color:#c9d1d9;padding:2rem;margin:0}
    .brand{display:flex;align-items:center;gap:.5rem;font-size:1.4rem;font-weight:bold;color:#56d364;margin-bottom:.4rem;letter-spacing:.03em}
    .brand span{font-size:1.6rem}
    h1{color:#56d364;margin-top:0;font-size:1.3rem}
    h2{color:#8b949e;font-size:.95rem;margin-bottom:.5rem;text-transform:uppercase;letter-spacing:.06em}
    code{background:#161b22;padding:2px 7px;border-radius:4px;display:block;margin:4px 0;font-size:.9rem}
    .box{background:#161b22;border:1px solid #30363d;padding:1rem 1.2rem;margin:1rem 0;border-radius:6px}
    input{background:#0d1117;border:1px solid #30363d;color:#c9d1d9;padding:6px 10px;border-radius:4px;width:360px}
    button{background:#56d364;border:none;color:#0d1117;padding:6px 14px;border-radius:4px;cursor:pointer;font-weight:bold}
    pre{background:#010409;padding:1rem;border-radius:4px;overflow-x:auto;color:#56d364;white-space:pre-wrap}
    li{margin:5px 0}
    .dica{border-left:3px solid #e3b341;padding:.5rem 1rem;background:#1a1600;border-radius:0 4px 4px 0;color:#e3b341;margin-top:.5rem}
    .formato{color:#8b949e;font-size:.85rem;margin-top:.4rem}
</style>"""

PAGE_TOP = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>🛡️ SD CyberLab: 🌐 Lab CMDi — Network Tool</title>
  """ + STYLE + """
</head>
<body>
  <div class="brand"><span>🛡️</span> SD CyberLab</div>
  <h1>🌐 Lab CMDi — Network Tool</h1>
  <div class="box">
    <h2>Situação</h2>
    <p>Ferramenta de diagnóstico que executa <code>ping</code> com o host fornecido pelo usuário.</p>
    <p>O parâmetro é concatenado diretamente no comando shell com <code>shell=True</code>.</p>
  </div>
  <div class="box">
    <h2>Payloads para testar</h2>
    <ul>
      <li><code>127.0.0.1; id</code></li>
      <li><code>127.0.0.1 | whoami</code></li>
      <li><code>; ls /</code></li>
    </ul>
    <div class="dica">
      💡 <strong>Dica:</strong> conseguiu executar o <code>id</code>? O servidor guarda um arquivo
      especial em um diretório temporário — sistemas Unix usam <code>/tmp</code> com frequência.
      <div class="formato">Formato da flag: <code>SDC_Flag{...}</code></div>
    </div>
  </div>
"""
PAGE_BOTTOM = "</body></html>"

@app.route("/")
def index():
    html = PAGE_TOP + """
  <div class="box">
    <form method="POST" action="/ping">
      <label>Host para pingar:</label><br><br>
      <input name="host" value="127.0.0.1" placeholder="127.0.0.1">
      <button type="submit">Ping</button>
    </form>
  </div>""" + PAGE_BOTTOM
    return Response(html, mimetype="text/html")

@app.route("/ping", methods=["POST"])
def ping():
    host = request.form.get("host", "")
    try:
        result = subprocess.run(f"ping -c 2 {host}", shell=True,
            capture_output=True, text=True, timeout=10)
        output = result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        output = "Timeout."
    except Exception as e:
        output = str(e)

    safe_host = host.replace("&","&amp;").replace("<","&lt;").replace('"',"&quot;")
    html = PAGE_TOP + (
        '<div class="box"><form method="POST" action="/ping">'
        '<label>Host para pingar:</label><br><br>'
        '<input name="host" value="' + safe_host + '"> '
        '<button type="submit">Ping</button></form></div>'
        '<div class="box"><h2>Saída</h2><pre>' + output + '</pre></div>'
    ) + PAGE_BOTTOM
    return Response(html, mimetype="text/html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
