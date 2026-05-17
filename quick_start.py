#!/usr/bin/env python3
"""
🚀 PORNIRE RAPIDĂ - OCR INVOICE PROCESSOR
"""

import subprocess
import sys
import threading
import time
import webbrowser
import socket
import shutil
import os

# Portul frontend selectat dinamic
FRONTEND_PORT = 5173


def _is_port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        try:
            sock.connect((host, port))
            return True
        except OSError:
            return False


def _wait_for_port(host: str, port: int, timeout: int = 60) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        if _is_port_open(host, port):
            return True
        time.sleep(0.5)
    return False


def _find_free_port(start: int = 5173, end: int = 5183) -> int:
    for p in range(start, end + 1):
        # Consideră port liber dacă nu e deschis pe 127.0.0.1 și localhost
        if not _is_port_open("127.0.0.1", p) and not _is_port_open("localhost", p):
            return p
    return start


def _get_npm_cmd() -> str:
    # Preferă npm din PATH; pe Windows poate fi npm.cmd
    for candidate in ("npm", "npm.cmd"):
        path = shutil.which(candidate)
        if path:
            return path
    return "npm"


def _detect_backend_entrypoint() -> str | None:
    # Alege automat scriptul backend
    for candidate in ("run.py", "app.py"):
        if os.path.isfile(os.path.join(".", candidate)):
            return candidate
    return None


def start_backend():
    """Pornește backend Flask"""
    entry = _detect_backend_entrypoint()
    if not entry:
        print("❌ Nu am găsit fișierul de pornire pentru backend (run.py sau app.py).")
        return

    print("🐍 Pornesc backend Flask pe http://localhost:5000")
    try:
        # Rulează backend-ul cu același Python; logurile sunt afișate în acest terminal
        subprocess.Popen([sys.executable, entry], cwd=".")
    except Exception as e:
        print(f"❌ Backend nu a pornit: {e}")


def start_frontend():
    """Pornește frontend React pe portul ales"""
    global FRONTEND_PORT
    # Verifică structură frontend
    fe_dir = os.path.join(".", "frontend")
    if not os.path.isdir(fe_dir):
        print("❌ Directorul 'frontend' nu există. Verifică structura proiectului.")
        return
    if not os.path.isfile(os.path.join(fe_dir, "package.json")):
        print("❌ 'package.json' lipsește în directorul 'frontend'. Rulează 'npm init' sau reinstalează frontend-ul.")
        return

    # Alege un port liber
    FRONTEND_PORT = _find_free_port(5173, 5183)
    print(f"⚛️ Pornesc frontend React pe http://localhost:{FRONTEND_PORT}")

    # Mică pauză pentru backend
    time.sleep(2)

    # Repară automat vite.config.js dacă are duplicate/eroare
    try:
        vite_config_path = os.path.join(fe_dir, "vite.config.js")
        needs_fix = False
        if os.path.isfile(vite_config_path):
            with open(vite_config_path, "r", encoding="utf-8") as f:
                content = f.read()
            if content.count("export default") > 1 or content.count("defineConfig") > 1 or content.count("@vitejs/plugin-react") > 1:
                needs_fix = True
        else:
            needs_fix = True

        if needs_fix:
            fixed_content = (
                "import { defineConfig } from 'vite'\n"
                "import react from '@vitejs/plugin-react'\n"
                "\n"
                "// https://vitejs.dev/config/\n"
                "export default defineConfig({\n"
                "  plugins: [react()],\n"
                "  server: {\n"
                "    proxy: {\n"
                "      '/api': {\n"
                "        target: 'http://localhost:5000',\n"
                "        changeOrigin: true,\n"
                "        secure: false,\n"
                "      }\n"
                "    }\n"
                "  }\n"
                "})\n"
            )
            with open(vite_config_path, "w", encoding="utf-8") as f:
                f.write(fixed_content)
            print("🧹 Am reparat 'frontend/vite.config.js' (eliminate duplicate import/export).")
    except Exception as e:
        print(f"⚠️ Nu am putut verifica/repara vite.config.js: {e}")

    # Repară automat postcss.config.js dacă este corupt/duplicat sau lipsește
    try:
        postcss_path = os.path.join(fe_dir, "postcss.config.js")
        needs_fix_postcss = False
        if os.path.isfile(postcss_path):
            with open(postcss_path, "r", encoding="utf-8") as f:
                pcontent = f.read()
            # Detelecție simplă de fișier corupt: export dublu sau conținut injectat
            if pcontent.count("export default") > 1 or pcontent.count("module.exports") > 1 or pcontent.count("tailwindcss") == 0:
                needs_fix_postcss = True
        else:
            needs_fix_postcss = True

        if needs_fix_postcss:
            postcss_fixed = (
                "export default {\n"
                "  plugins: {\n"
                "    tailwindcss: {},\n"
                "    autoprefixer: {},\n"
                "  },\n"
                "}\n"
            )
            with open(postcss_path, "w", encoding="utf-8") as f:
                f.write(postcss_fixed)
            print("🧹 Am reparat 'frontend/postcss.config.js'.")
    except Exception as e:
        print(f"⚠️ Nu am putut verifica/repara postcss.config.js: {e}")

    # Dacă lipsesc dependențele Node, le instalez automat
    try:
        node_modules_dir = os.path.join(fe_dir, "node_modules")
        if not os.path.isdir(node_modules_dir):
            npm = _get_npm_cmd()
            print("📦 Instalez dependențele frontend (npm install)...")
            subprocess.run([npm, "install"], cwd=fe_dir, check=True)
    except Exception as e:
        print(f"⚠️ Nu am putut instala dependențele npm: {e}")

    # Repară automat un vite.config.js corupt/duplicat
    try:
        vite_config_path = os.path.join(fe_dir, "vite.config.js")
        needs_fix = False
        if os.path.isfile(vite_config_path):
            with open(vite_config_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Heuristici: multiple exporturi sau importuri duplicate indică fișier corupt
            if content.count("export default") > 1 or content.count("defineConfig") > 1 or content.count("@vitejs/plugin-react") > 1:
                needs_fix = True
        else:
            needs_fix = True

        if needs_fix:
            fixed_content = (
                "import { defineConfig } from 'vite'\n"
                "import react from '@vitejs/plugin-react'\n"
                "\n"
                "export default defineConfig({\n"
                "  plugins: [react()],\n"
                "  server: {\n"
                "    proxy: {\n"
                "      '/api': {\n"
                "        target: 'http://localhost:5000',\n"
                "        changeOrigin: true,\n"
                "        secure: false,\n"
                "      }\n"
                "    }\n"
                "  }\n"
                "})\n"
            )
            with open(vite_config_path, "w", encoding="utf-8") as f:
                f.write(fixed_content)
            print("🧹 Am reparat 'frontend/vite.config.js' (eliminate duplicate import/export).")
    except Exception as e:
        print(f"⚠️ Nu am putut verifica/repara vite.config.js: {e}")

    try:
        npm = _get_npm_cmd()
        # Transmite parametri suplimentari către scriptul dev (vite): port + strictPort
        cmd = [npm, "run", "dev", "--", "--port", str(FRONTEND_PORT), "--strictPort"]
        env = os.environ.copy()
        env.setdefault("BROWSER", "none")  # evită deschiderea automată de către dev server

        subprocess.run(cmd, cwd=fe_dir, check=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f"❌ Frontend nu a pornit (cod ieșire {e.returncode}). Verifică logurile de mai sus.")
    except FileNotFoundError:
        print("❌ 'npm' nu a fost găsit. Instalează Node.js și asigură-te că npm este în PATH.")
    except Exception as e:
        print(f"❌ Eroare la pornirea frontend-ului: {e}")


def open_app():
    """Deschide aplicația în browser după ce frontend-ul este disponibil"""
    url = f"http://localhost:{FRONTEND_PORT}"
    if _wait_for_port("localhost", FRONTEND_PORT, timeout=120):
        webbrowser.open(url)
        print(f"🌐 Aplicația OCR s-a deschis în browser: {url}")
    else:
        print(f"⌛ Frontend-ul nu a devenit disponibil la timp ({url}).")


if __name__ == "__main__":
    # Alege portul înainte de pornire, astfel încât mesajele să reflecte corect
    FRONTEND_PORT = _find_free_port(5173, 5183)

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                  OCR INVOICE PROCESSOR                       ║
║                    🚀 PORNIRE RAPIDĂ                         ║  
╚══════════════════════════════════════════════════════════════╝

🔥 Pornesc aplicația completă...
📍 Backend: http://localhost:5000  
📍 Frontend: http://localhost:{FRONTEND_PORT}
📱 Aplicația se va deschide automat în browser!

⚠️  Pentru a opri: CTRL+C în ambele terminale
""")

    # Pornește serviciile
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    browser_thread = threading.Thread(target=open_app, daemon=True)

    backend_thread.start()
    browser_thread.start()

    # Așteaptă și pornește frontend-ul (ține procesul activ)
    try:
        start_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Oprire la cererea utilizatorului. La revedere!")
