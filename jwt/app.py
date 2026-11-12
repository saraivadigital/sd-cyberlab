"""
SD CyberLab — JWT Algorithm Confusion (alg: none)
"""
import jwt, json, base64
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
SECRET = "estrela_da_morte_123"

PAGE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>🛡️ SD CyberLab: 🔑 Lab JWT — Auth Service</title>
  <style>
    *{box-sizing:border-box}
    body{font-family:monospace;background:#0d1117;color:#c9d1d9;padding:2rem;margin:0}
    .brand{display:flex;align-items:center;gap:.5rem;font-size:1.4rem;font-weight:bold;color:#ffa657;margin-bottom:.4rem;letter-spacing:.03em}
    .brand span{font-size:1.6rem}
    h1{color:#ffa657;margin-top:0;font-size:1.3rem}
    h2{color:#8b949e;font-size:.95rem;margin-bottom:.5rem;text-transform:uppercase;letter-spacing:.06em}
    code{background:#161b22;padding:2px 7px;border-radius:4px;display:block;margin:4px 0;word-break:break-all;font-size:.9rem}
    .box{background:#161b22;border:1px solid #30363d;padding:1rem 1.2rem;margin:1rem 0;border-radius:6px}
    a{color:#ffa657}li{margin:5px 0}
    .dica{border-left:3px solid #e3b341;padding:.5rem 1rem;background:#1a1600;border-radius:0 4px 4px 0;color:#e3b341;margin-top:.5rem}
    .formato{color:#8b949e;font-size:.85rem;margin-top:.4rem}
  </style>
</head>
<body>
  <div class="brand"><span>🛡️</span> SD CyberLab</div>
  <h1>🔑 Lab JWT — Auth Service</h1>
  <div class="box">
    <h2>Token de usuário (role=user)</h2>
    <code>{{ token_user }}</code>
    <p>
      <a href="/api/token/user">Pegar token</a> |
      <a href="/api/token/hint">Script de forjamento</a>
    </p>
  </div>
  <div class="box">
    <h2>Endpoints protegidos</h2>
    <code>curl -H "Authorization: Bearer &lt;token&gt;" http://localhost:5004/api/whoami</code>
    <code>curl -H "Authorization: Bearer &lt;token&gt;" http://localhost:5004/api/admin</code>
    <div class="dica">
      💡 <strong>Dica:</strong> inspecione o cabeçalho do token JWT. A biblioteca desta app
      respeita o campo <code>alg</code> sem questionar — e se você sugerisse um algoritmo diferente?
      <div class="formato">Formato da flag: <code>SDC_Flag{...}</code></div>
    </div>
  </div>
</body></html>"""

def make_token(user, role):
    return jwt.encode({"user": user, "role": role}, SECRET, algorithm="HS256")

@app.route("/")
def index():
    return render_template_string(PAGE, token_user=make_token("chewbacana", "user"))

@app.route("/api/token/user")
def get_user_token():
    return jsonify({"token": make_token("chewbacana", "user"), "hint": "Tente forjar um com role=admin"})

@app.route("/api/token/hint")
def admin_hint():
    h = base64.urlsafe_b64encode(json.dumps({"alg":"none","typ":"JWT"}).encode()).rstrip(b"=").decode()
    p = base64.urlsafe_b64encode(json.dumps({"user":"chewbacana","role":"admin"}).encode()).rstrip(b"=").decode()
    script = (
        "import base64, json\n"
        "header  = base64.urlsafe_b64encode(json.dumps({'alg':'none','typ':'JWT'}).encode()).rstrip(b'=').decode()\n"
        "payload = base64.urlsafe_b64encode(json.dumps({'user':'chewbacana','role':'admin'}).encode()).rstrip(b'=').decode()\n"
        "token   = f'{header}.{payload}.'\n"
        "print(token)"
    )
    return jsonify({"forged_token_example": f"{h}.{p}.", "script": script})

def decode_token(token):
    try:
        parts = token.split(".")
        if len(parts) != 3: return None, "Token malformado"
        header = json.loads(base64.urlsafe_b64decode(parts[0] + "=="))
        if header.get("alg", "").lower() == "none":
            payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=="))
            return payload, None  # ❌ aceita sem assinatura
        return jwt.decode(token, SECRET, algorithms=["HS256"]), None
    except Exception as e:
        return None, str(e)

@app.route("/api/whoami")
def whoami():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "): return jsonify({"error": "Token necessário"}), 401
    payload, err = decode_token(auth[7:])
    if err: return jsonify({"error": err}), 401
    return jsonify({"user": payload.get("user"), "role": payload.get("role")})

@app.route("/api/admin")
def admin():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "): return jsonify({"error": "Token necessário"}), 401
    payload, err = decode_token(auth[7:])
    if err: return jsonify({"error": err}), 401
    if payload.get("role") != "admin":
        return jsonify({"error": "Acesso negado — precisa de role=admin"}), 403
    return jsonify({
        "flag": "SDC_Flag{JWT_4lg_N0n3_Byp4ss}",
        "message": "Bem-vindo ao lado sombrio, " + payload.get("user", "?") + "!",
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
