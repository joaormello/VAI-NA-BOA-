import requests

token = "f72c4b0c9726c0a66629bfc2e5cf8e44d1be61b82400000f4ee05b86c1f980d8"
session = requests.Session()

# 1. Autenticação na API Olho Vivo da SPTrans
auth_url = f"http://api.olhovivo.sptrans.com.br/v2.1/Login/Autenticar?token={token}"
try:
    auth_resp = session.post(auth_url, timeout=12)
    print("Status Autenticacao:", auth_resp.status_code)
    print("Resposta Auth:", auth_resp.text)

    if auth_resp.status_code == 200 and auth_resp.text.lower() == "true":
        # 2. Busca pela linha 746C
        busca_url = "http://api.olhovivo.sptrans.com.br/v2.1/Linha/Buscar?termosBusca=746C"
        resp_linha = session.get(busca_url, timeout=12)
        linhas = resp_linha.json()
        print("Linhas encontradas:", len(linhas))
        for l in linhas:
            print(f"Linha {l.get('lt')}-{l.get('tl')} | {l.get('tp')} -> {l.get('ts')} | Codigo Linha: {l.get('cl')}")
except Exception as e:
    print("Erro ao consultar SPTrans:", e)
