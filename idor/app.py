"""
SD CyberLab — IDOR (Insecure Direct Object Reference)
Objetivo: acessar perfis de outros usuários manipulando o ID na URL.
"""
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

USERS = {
    1: {"id": 1, "nome": "Admin",             "email": "admin@cyberlab.sd",     "role": "admin", "bio": "O Root"},
    2: {"id": 2, "nome": "Chewbacana",         "email": "chew@cyberlab.sd",      "role": "user",  "bio": "O Bruto"},
    3: {"id": 3, "nome": "Mestre Yodair",      "email": "mestrey@cyberlab.sd",   "role": "user",  "bio": "O Poderoso"},
    4: {"id": 4, "nome": "Luke Johnnywalker",  "email": "luke@cyberlab.sd",    "role": "user",  "bio": "O Jedi"},
    5: {"id": 5, "nome": "Anakiko Skywalker",  "email": "asky@cyberlab.sd",      "role": "user",  "bio": "O Inicio..."},
    6: {"id": 6, "nome": "Convidado",          "email": "convidado@cyberlab.sd", "role": "guest", "bio": "Visitante"},
    7: {"id": 7, "nome": "Darth Cleiton",      "email": "dc@cyberlab.sd",        "role": "user",  "bio": "O Bravo"},
    8: {"id": 8, "nome": "C3-Pior",            "email": "c3p@cyberlab.sd",       "role": "user",  "bio": "Droide Zuado"},
    9: {"id": 9, "nome": "R2-Dadinho",         "email": "r2d@cyberlab.sd",       "role": "user",  "bio": "Robozinho F..."},
}

PAGE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>🛡️ SD CyberLab: 🏢 Lab IDOR — Portal RH</title>
  <style>
    *{box-sizing:border-box}
    body{font-family:monospace;background:#0d1117;color:#c9d1d9;padding:2rem;margin:0}
    .brand{
      display:flex;align-items:center;gap:.5rem;
      font-size:1.4rem;font-weight:bold;color:#58a6ff;
      margin-bottom:.4rem;letter-spacing:.03em;
    }
    .brand span{font-size:1.6rem}
    h1{color:#58a6ff;margin-top:0;font-size:1.3rem}
    h2{color:#8b949e;font-size:.95rem;margin-bottom:.5rem;text-transform:uppercase;letter-spacing:.06em}
    a{color:#58a6ff}
    code{background:#161b22;padding:2px 7px;border-radius:4px;font-size:.9rem}
    .box{background:#161b22;border:1px solid #30363d;padding:1rem 1.2rem;margin:1rem 0;border-radius:6px}
    li{margin:5px 0}
    .tag{display:inline-block;background:#0d419d;color:#79c0ff;border-radius:12px;padding:1px 8px;font-size:.8rem;margin-left:6px}
    .dica{border-left:3px solid #e3b341;padding:.5rem 1rem;background:#1a1600;border-radius:0 4px 4px 0;color:#e3b341;margin-top:.5rem}
    .formato{color:#8b949e;font-size:.85rem;margin-top:.4rem}
  </style>
</head>
<body>
  <div class="brand"><span>🛡️</span> SD CyberLab</div>
  <h1>🏢 Lab IDOR — Portal RH</h1>
  <div class="box">
    <h2>Situação</h2>
    <p>Você está logado como <strong>Chewbacana (id=2)</strong>.</p>
    <p>O sistema retorna o perfil de qualquer usuário pelo ID informado na URL — <strong>sem verificar</strong> se você é o dono.</p>
  </div>
  <div class="box">
    <h2>Endpoints</h2>
    <ul>
      <li><code>GET /api/users</code> — lista todos os usuários</li>
      <li><code>GET /api/user/&lt;id&gt;/profile</code> — perfil completo <span class="tag">IDOR</span></li>
    </ul>
    <div class="dica">
      💡 <strong>Dica:</strong> você está logado com <code>id=2</code>. Será que todos os perfis merecem o mesmo nível de acesso?
      Itere os IDs e observe o que muda no campo <code>role</code> e <code>bio</code> de cada um.
      <div class="formato">Formato da flag: <code>SDC_Flag{...}</code></div>
    </div>
  </div>
  <div class="box">
    <h2>Links rápidos</h2>
    <a href="/api/users">Listar usuários</a> |
    <a href="/api/user/2/profile">Meu perfil (id=2)</a>
  </div>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(PAGE)

@app.route("/api/users")
def list_users():
    return jsonify([{"id": u["id"], "nome": u["nome"]} for u in USERS.values()])

@app.route("/api/user/<int:user_id>/profile")
def get_profile(user_id):
    user = USERS.get(user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404
    # Perfil do admin traz a flag no campo bio
    if user_id == 1:
        data = dict(user)
        data["bio"] = "SDC_Flag{1D0R_H0r1z0nt4l_Pr1v1l3g3_3sc4l4t10n}"
        return jsonify(data)
    return jsonify(user)  # ❌ sem verificar ownership

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
