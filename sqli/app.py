"""
SD CyberLab — SQL Injection (UNION-based + login bypass)
"""
import sqlite3
from flask import Flask, request, render_template_string, session, redirect

app = Flask(__name__)
app.secret_key = "sqli_secret"
DB = "/tmp/lab_sqli.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT);
        CREATE TABLE IF NOT EXISTS secrets (id INTEGER PRIMARY KEY, note TEXT);
        DELETE FROM users; DELETE FROM secrets;
        INSERT INTO users VALUES (1, 'admin',      'D4rth_V4d3r!',  'admin');
        INSERT INTO users VALUES (2, 'chewbacana', 'wookie123',      'user');
        INSERT INTO users VALUES (3, 'mestrey',    'Y0d4Mestre!',    'user');
        INSERT INTO users VALUES (4, 'padcal',     'F0rca456',       'user');
        INSERT INTO users VALUES (5, 'asky',       'AnakikoSky!',    'user');
        INSERT INTO secrets VALUES (1, 'SDC_Flag{SQ L1_Un10n_3xf1l_S3cr3ts}');
        INSERT INTO secrets VALUES (2, 'Chave de acesso à Estrela da Morte: SD-XRAY-7731-DELTA');
        INSERT INTO secrets VALUES (3, 'Coordenadas da Base Rebelde: 74.491N-10.221W');
    """)
    conn.commit(); conn.close()

init_db()

PAGE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>🛡️ SD CyberLab: 🗄️ Lab SQLi — Sistema de Login</title>
  <style>
    *{box-sizing:border-box}
    body{font-family:monospace;background:#0d1117;color:#c9d1d9;padding:2rem;margin:0}
    .brand{display:flex;align-items:center;gap:.5rem;font-size:1.4rem;font-weight:bold;color:#d2a8ff;margin-bottom:.4rem;letter-spacing:.03em}
    .brand span{font-size:1.6rem}
    h1{color:#d2a8ff;margin-top:0;font-size:1.3rem}
    h2{color:#8b949e;font-size:.95rem;margin-bottom:.5rem;text-transform:uppercase;letter-spacing:.06em}
    code{background:#161b22;padding:2px 7px;border-radius:4px;display:block;margin:4px 0;font-size:.9rem}
    .box{background:#161b22;border:1px solid #30363d;padding:1rem 1.2rem;margin:1rem 0;border-radius:6px}
    input{background:#0d1117;border:1px solid #30363d;color:#c9d1d9;padding:6px 10px;border-radius:4px;width:280px;display:block;margin:6px 0}
    button{background:#d2a8ff;border:none;color:#0d1117;padding:6px 14px;border-radius:4px;cursor:pointer;font-weight:bold;margin-top:6px}
    .ok{color:#3fb950}.err{color:#f85149}
    table{border-collapse:collapse;width:100%}
    td,th{border:1px solid #30363d;padding:6px 10px;text-align:left}
    th{color:#d2a8ff}
    a{color:#d2a8ff}
    .dica{border-left:3px solid #e3b341;padding:.5rem 1rem;background:#1a1600;border-radius:0 4px 4px 0;color:#e3b341;margin-top:.5rem}
    .formato{color:#8b949e;font-size:.85rem;margin-top:.4rem}
  </style>
</head>
<body>
  <div class="brand"><span>🛡️</span> SD CyberLab</div>
  <h1>🗄️ Lab SQLi — Sistema de Login</h1>
  <div class="box">
    <h2>Situação</h2>
    <p>O login concatena os valores diretamente na query SQL sem prepared statements.</p>
  </div>
  {% if logged %}
  <div class="box">
    <p class="ok">✅ Logado como: <strong>{{ user }}</strong> (role: {{ role }})</p>
    <a href="/logout">Logout</a>
  </div>
  {% endif %}
  {% if error %}<div class="box"><p class="err">❌ {{ error }}</p></div>{% endif %}
  {% if not logged %}
  <div class="box">
    <h2>Login</h2>
    <form method="POST" action="/login">
      <input name="username" placeholder="Usuário">
      <input name="password" type="password" placeholder="Senha">
      <button type="submit">Entrar</button>
    </form>
  </div>
  <div class="box">
    <h2>Payloads para testar</h2>
    <p><strong>Bypass (campo usuário):</strong></p>
    <code>admin'--</code>
    <code>' OR '1'='1'--</code>
    <div class="dica">
      💡 <strong>Dica:</strong> depois de entrar, explore o endpoint de busca com UNION.
      O banco tem mais de uma tabela — e nem todas são visíveis no login.
      <div class="formato">Formato da flag: <code>SDC_Flag{...}</code></div>
    </div>
  </div>
  {% endif %}
  {% if results is not none %}
  <div class="box">
    <h2>Resultados</h2>
    {% if results %}
    <table><tr><th>ID</th><th>Username</th><th>Password</th><th>Role</th></tr>
    {% for r in results %}<tr>{% for col in r %}<td>{{ col }}</td>{% endfor %}</tr>{% endfor %}
    </table>
    {% else %}<p style="color:#8b949e">Nenhum resultado.</p>{% endif %}
  </div>
  {% endif %}
  {% if logged %}
  <div class="box">
    <h2>Busca de usuários</h2>
    <form method="GET" action="/search">
      <input name="q" placeholder="Nome do usuário" style="display:inline;width:280px">
      <button type="submit" style="display:inline">Buscar</button>
    </form>
    <div class="dica" style="margin-top:1rem">
      💡 <strong>Dica:</strong> o parâmetro de busca também não usa prepared statements.
      Tente descobrir quais tabelas existem no banco e o que elas guardam.
      <div class="formato">Formato da flag: <code>SDC_Flag{...}</code></div>
    </div>
  </div>
  {% endif %}
</body></html>"""

@app.route("/")
def index():
    return render_template_string(PAGE, logged=session.get("logged", False),
        user=session.get("user"), role=session.get("role"), error=None, results=None)

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    try:
        conn = sqlite3.connect(DB); cur = conn.cursor(); cur.execute(query)
        row = cur.fetchone(); conn.close()
    except Exception as e:
        return render_template_string(PAGE, logged=False, error=f"SQL Error: {e}", results=None, user=None, role=None)
    if row:
        session["logged"] = True; session["user"] = row[1]; session["role"] = row[3]
        return redirect("/")
    return render_template_string(PAGE, logged=False, error="Credenciais inválidas.", results=None, user=None, role=None)

@app.route("/search")
def search():
    if not session.get("logged"): return redirect("/")
    q = request.args.get("q", "")
    query = f"SELECT * FROM users WHERE username LIKE '%{q}%'"
    try:
        conn = sqlite3.connect(DB); cur = conn.cursor(); cur.execute(query)
        rows = cur.fetchall(); conn.close()
    except Exception as e:
        rows = [[f"SQL Error: {e}", "", "", ""]]
    return render_template_string(PAGE, logged=True, user=session.get("user"),
        role=session.get("role"), error=None, results=rows)

@app.route("/logout")
def logout():
    session.clear(); return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
