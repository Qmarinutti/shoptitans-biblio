"""Serveur de test local : python -I outils/serveur_local.py  ->  http://localhost:8765
Sert le dossier biblio-site, avec CORS pour que le dashboard Supabase puisse lire supabase/02_plans.sql."""
import http.server, functools, pathlib

RACINE = pathlib.Path(__file__).resolve().parent.parent


class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()


http.server.ThreadingHTTPServer(("127.0.0.1", 8765), functools.partial(H, directory=str(RACINE))).serve_forever()
