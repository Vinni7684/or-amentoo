from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import sqlite3
import uuid
import mercadopago
import os

app = Flask(__name__)
CORS(app)

# ==========================================
# CONFIGURAÇÕES DE API (SEGURAS VIA VARIÁVEIS DE AMBIENTE)
# ==========================================
API_KEY = os.environ.get("BRAZUCA_API_KEY")
BASE_URL = "https://brazucasms.com/api/external"

MP_ACCESS_TOKEN = os.environ.get("MERCADOPAGO_ACCESS_TOKEN")
mp_sdk = mercadopago.SDK(MP_ACCESS_TOKEN)

# ==========================================
# CATÁLOGO DE SERVIÇOS E PREÇOS
# ==========================================
CATALOGO = {
    "ki": {"nome": "99 APP", "preco": 4.14},
    "acme": {"nome": "ACME", "preco": 4.49},
    "bbi": {"nome": "Aiqfome", "preco": 6.70},
    "uk": {"nome": "AirBnb", "preco": 4.14},
    "ab": {"nome": "Alibaba", "preco": 4.14},
    "hx": {"nome": "AliExpress", "preco": 4.80},
    "hw": {"nome": "Alipay/Alibaba", "preco": 4.14},
    "am": {"nome": "Amazon", "preco": 4.70},
    "pm": {"nome": "AOL", "preco": 4.14},
    "ml": {"nome": "Aposta Ganha", "preco": 4.14},
    "wx": {"nome": "Apple", "preco": 4.14},
    "bbl": {"nome": "Autodesk", "preco": 4.50},
    "li": {"nome": "Baidu", "preco": 4.14},
    "abd": {"nome": "BeBoo", "preco": 6.00},
    "ie": {"nome": "Bet365", "preco": 4.50},
    "bzb": {"nome": "Big Cash", "preco": 4.14},
    "bl": {"nome": "Bigo Live", "preco": 4.14},
    "zs": {"nome": "Bilibili", "preco": 4.14},
    "ua": {"nome": "BlaBlaCar", "preco": 4.55},
    "bz": {"nome": "Blizzard", "preco": 4.14},
    "jw": {"nome": "Br777", "preco": 4.14},
    "sy": {"nome": "Brahma", "preco": 4.14},
    "brdou": {"nome": "BrDouble", "preco": 4.34},
    "zt": {"nome": "Budweiser", "preco": 4.14},
    "mo": {"nome": "Bumble", "preco": 4.14},
    "ls": {"nome": "Careem", "preco": 4.14},
    "gj": {"nome": "Carousell", "preco": 4.14},
    "pc": {"nome": "Casino", "preco": 4.14},
    "et": {"nome": "Clubhouse", "preco": 4.14},
    "om": {"nome": "Corona", "preco": 4.14},
    "wc": {"nome": "Craigslist", "preco": 4.14},
    "ccl": {"nome": "Cruzeiro", "preco": 6.00},
    "aje": {"nome": "CupidMedia", "preco": 4.70},
    "ahi": {"nome": "Daki", "preco": 4.65},
    "zk": {"nome": "Deliveroo", "preco": 4.14},
    "xk": {"nome": "DiDi Taxi", "preco": 4.14},
    "ds": {"nome": "Discord", "preco": 4.14},
    "ud": {"nome": "Disney", "preco": 4.17},
    "blr": {"nome": "DocuSign", "preco": 4.14},
    "dh": {"nome": "Ebay", "preco": 4.14},
    "uf": {"nome": "Eneba", "preco": 4.14},
    "arf": {"nome": "Enjoei", "preco": 4.50},
    "etsy": {"nome": "Etsy", "preco": 4.14},
    "fb": {"nome": "Facebook", "preco": 4.80},
    "alc": {"nome": "Facily", "preco": 4.70},
    "asl": {"nome": "Familhao", "preco": 4.40},
    "any": {"nome": "FastEarn", "preco": 4.60},
    "se": {"nome": "Feeld", "preco": 4.14},
    "aim": {"nome": "Firebase", "preco": 4.70},
    "cn": {"nome": "Fiverr", "preco": 4.14},
    "nz": {"nome": "Foodpanda", "preco": 4.14},
    "mv": {"nome": "Fruitz", "preco": 4.14},
    "bk": {"nome": "G2G", "preco": 4.14},
    "xe": {"nome": "GalaxyChat", "preco": 4.14},
    "arg": {"nome": "Gappx", "preco": 4.61},
    "ul": {"nome": "Getir", "preco": 4.14},
    "aiu": {"nome": "GetNinjas", "preco": 4.65},
    "ads": {"nome": "GoChat", "preco": 4.14},
    "go": {"nome": "Google", "preco": 6.00},
    "ccu": {"nome": "Google Chat", "preco": 6.00},
    "gmsg": {"nome": "GoogleMessenger", "preco": 4.14},
    "gf": {"nome": "GoogleVoice", "preco": 6.00},
    "afe": {"nome": "GovBr", "preco": 4.50},
    "yw": {"nome": "Grindr", "preco": 4.14},
    "alb": {"nome": "Guiche Web", "preco": 4.50},
    "ik": {"nome": "GuruBets", "preco": 4.25},
    "guv": {"nome": "Guvi", "preco": 4.14},
    "df": {"nome": "Happn", "preco": 4.14},
    "vz": {"nome": "Hinge", "preco": 4.14},
    "hrnjie": {"nome": "Huarenjie", "preco": 4.14},
    "iq": {"nome": "Icq", "preco": 4.14},
    "pd": {"nome": "IFood", "preco": 4.14},
    "im": {"nome": "IMO Messenger", "preco": 4.14},
    "rl": {"nome": "InDriver", "preco": 4.14},
    "ig": {"nome": "Instagram", "preco": 4.17},
    "il": {"nome": "IQOS", "preco": 4.14},
    "za": {"nome": "Jingdong", "preco": 4.14},
    "xx": {"nome": "Joyride", "preco": 4.14},
    "pu": {"nome": "Justdating", "preco": 4.14},
    "k8bet": {"nome": "K8Bet", "preco": 4.59},
    "kt": {"nome": "KakaoTalk", "preco": 4.14},
    "kiq": {"nome": "Kliq", "preco": 4.14},
    "vp": {"nome": "Kwai", "preco": 4.14},
    "fh": {"nome": "Lalamove", "preco": 4.55},
    "dl": {"nome": "Lazada", "preco": 4.14},
    "do": {"nome": "Leboncoin", "preco": 4.14},
    "me": {"nome": "Line Msg", "preco": 4.14},
    "tn": {"nome": "LinkedIn", "preco": 4.14},
    "lucky": {"nome": "Lucky Play", "preco": 6.70},
    "beh": {"nome": "LUUP", "preco": 4.50},
    "afq": {"nome": "MagaLu", "preco": 4.65},
    "fd": {"nome": "Mamba", "preco": 4.50},
    "bwv": {"nome": "Manus", "preco": 6.00},
    "cq": {"nome": "Mercado", "preco": 4.59},
    "amv": {"nome": "MeSeems", "preco": 6.00},
    "mc": {"nome": "MiChat", "preco": 4.14},
    "mm": {"nome": "Microsoft", "preco": 4.14},
    "gm": {"nome": "Mocospace", "preco": 4.14},
    "axm": {"nome": "Ñ Me Perturbe", "preco": 6.00},
    "abn": {"nome": "Namars", "preco": 4.14},
    "awg": {"nome": "Natura Avon", "preco": 4.14},
    "nv": {"nome": "Naver", "preco": 4.14},
    "nf": {"nome": "Netflix", "preco": 4.14},
    "ew": {"nome": "Nike", "preco": 4.14},
    "tf": {"nome": "Noon", "preco": 4.14},
    "xo": {"nome": "Notifire", "preco": 4.14},
    "ok": {"nome": "Ok.ru", "preco": 4.50},
    "vm": {"nome": "Okcupid", "preco": 7.09},
    "sn": {"nome": "Olx", "preco": 4.14},
    "dr": {"nome": "OpenAI", "preco": 4.43},
    "auz": {"nome": "Outlier", "preco": 4.80},
    "ot": {"nome": "Outros", "preco": 4.85},
    "bqh": {"nome": "PEDIR GAS", "preco": 4.60},
    "fx": {"nome": "PGbonus", "preco": 4.14},
    "opd": {"nome": "Poe", "preco": 4.14},
    "pf": {"nome": "Pof.com", "preco": 4.14},
    "fj": {"nome": "Potato Chat", "preco": 4.14},
    "anw": {"nome": "Premmia", "preco": 4.65},
    "afs": {"nome": "Privalia", "preco": 4.61},
    "aa": {"nome": "Probo", "preco": 4.14},
    "dp": {"nome": "ProtonMail", "preco": 4.14},
    "ayk": {"nome": "Radquest", "preco": 4.50},
    "aba": {"nome": "Rappi", "preco": 6.00},
    "ajj": {"nome": "Rebtel", "preco": 4.14},
    "aoz": {"nome": "Reclame Aqui", "preco": 4.63},
    "qf": {"nome": "RedBook", "preco": 4.14},
    "reip": {"nome": "Rei do Pitaco", "preco": 4.77},
    "abj": {"nome": "Serasa", "preco": 4.55},
    "aez": {"nome": "Shein", "preco": 6.00},
    "vg": {"nome": "ShellBox", "preco": 4.14},
    "ka": {"nome": "Shopee", "preco": 4.25},
    "bw": {"nome": "Signal", "preco": 4.14},
    "skyva": {"nome": "SKY VALOR", "preco": 4.27},
    "pb": {"nome": "SkyTV", "preco": 4.14},
    "agb": {"nome": "Smiles", "preco": 4.14},
    "fu": {"nome": "Snapchat", "preco": 4.14},
    "bxz": {"nome": "SOOP", "preco": 6.00},
    "mx": {"nome": "SoulApp", "preco": 9.82},
    "ky": {"nome": "Spaten", "preco": 4.14},
    "mt": {"nome": "Steam", "preco": 4.14},
    "xr": {"nome": "Tango", "preco": 4.14},
    "ep": {"nome": "Temu", "preco": 4.50},
    "qq": {"nome": "Tencent QQ", "preco": 4.14},
    "lz": {"nome": "Things", "preco": 4.14},
    "rb": {"nome": "Tick", "preco": 4.14},
    "gp": {"nome": "Ticketmaster", "preco": 4.51},
    "lf": {"nome": "TikTok", "preco": 4.14},
    "timmm": {"nome": "TIM", "preco": 4.17},
    "amp": {"nome": "Timepass", "preco": 4.14},
    "oi": {"nome": "Tinder", "preco": 4.14},
    "auc": {"nome": "TotalPass", "preco": 4.30},
    "hb": {"nome": "Twitch", "preco": 4.40},
    "tw": {"nome": "Twitter", "preco": 4.14},
    "ub": {"nome": "Uber", "preco": 4.14},
    "ahb": {"nome": "Ubisoft", "preco": 6.00},
    "afr": {"nome": "Ultragaz", "preco": 4.64},
    "abh": {"nome": "Uol", "preco": 4.54},
    "vi": {"nome": "Viber", "preco": 4.08},
    "kc": {"nome": "Vinted", "preco": 4.14},
    "kx": {"nome": "Vivo", "preco": 4.14},
    "vk": {"nome": "Vk.com", "preco": 4.50},
    "wr": {"nome": "Walmart", "preco": 4.70},
    "bfa": {"nome": "Webmotors", "preco": 4.50},
    "wb": {"nome": "WeChat", "preco": 4.40},
    "kf": {"nome": "Weibo", "preco": 4.14},
    "xv": {"nome": "Wish", "preco": 4.14},
    "fa": {"nome": "XadrezFeliz", "preco": 4.14},
    "aml": {"nome": "Xbox", "preco": 4.50},
    "yu": {"nome": "Xiaomi", "preco": 4.50},
    "mb": {"nome": "Yahoo", "preco": 4.12},
    "yl": {"nome": "Yalla", "preco": 4.14},
    "ya": {"nome": "Yandex", "preco": 4.20},
    "yi": {"nome": "Yemeksepeti", "preco": 4.14},
    "yetz": {"nome": "Yetz Promo", "preco": 6.19},
    "sm": {"nome": "YoWin", "preco": 4.14},
    "em": {"nome": "Zé Delivery", "preco": 4.14},
    "btm": {"nome": "ZeeNow", "preco": 4.60},
    "zh": {"nome": "Zoho", "preco": 4.14}
}

# ==========================================
# BANCO DE DADOS DOS PEDIDOS
# ==========================================
def iniciar_banco():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id TEXT PRIMARY KEY,
            servico TEXT,
            status TEXT,
            activation_id TEXT,
            numero TEXT
        )
    ''')
    conn.commit()
    conn.close()

def obter_conexao():
    conn = sqlite3.connect('banco.db')
    conn.row_factory = sqlite3.Row
    return conn

iniciar_banco()

# ==========================================
# ROTAS DO SISTEMA
# ==========================================

@app.route("/servicos")
def get_servicos():
    return jsonify(CATALOGO)

@app.route("/gerar_pagamento", methods=["POST"])
def gerar_pagamento():
    data = request.json or {}
    servico_cod = data.get("servico")
    
    if servico_cod not in CATALOGO:
        return jsonify({"erro": "Serviço não encontrado"}), 400
        
    preco = CATALOGO[servico_cod]["preco"]
    nome = CATALOGO[servico_cod]["nome"]
    pedido_id = str(uuid.uuid4())
    
    conn = obter_conexao()
    conn.execute('INSERT INTO pedidos (id, servico, status) VALUES (?, ?, ?)', (pedido_id, servico_cod, 'pendente'))
    conn.commit()
    conn.close()

    url_base = request.url_root.replace("http://", "https://")
    webhook_url = f"{url_base}webhook"

    payment_data = {
        "transaction_amount": preco,
        "description": f"Número virtual para {nome}",
        "payment_method_id": "pix",
        "payer": {"email": "cliente.sms@email.com"},
        "external_reference": pedido_id,
        "notification_url": webhook_url
    }
    
    payment_response = mp_sdk.payment().create(payment_data)
    payment = payment_response["response"]
    
    if payment.get("status") == "pending":
        return jsonify({
            "pedido_id": pedido_id,
            "copia_e_cola": payment["point_of_interaction"]["transaction_data"]["qr_code"],
            "qr_code_base64": payment["point_of_interaction"]["transaction_data"]["qr_code_base64"]
        })
    else:
        return jsonify({"erro": "Falha ao gerar o Pix no Mercado Pago"}), 400

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    payment_id = None
    
    # 1. Tenta capturar se o Mercado Pago enviar em formato JSON (Webhook Oficial)
    if request.is_json:
        payload = request.get_json()
        if payload and "data" in payload:
            payment_id = payload["data"].get("id")
            
    # 2. Se não achar, tenta capturar via parâmetros de URL (IPN antiga ou fallback)
    if not payment_id:
        payment_id = request.args.get("id") or request.args.get("data.id")
    
    if payment_id:
        payment_info = mp_sdk.payment().get(payment_id)
        payment = payment_info.get("response", {})
        
        if payment.get("status") == "approved":
            pedido_id = payment.get("external_reference")
            
            conn = obter_conexao()
            pedido = conn.execute('SELECT * FROM pedidos WHERE id = ?', (pedido_id,)).fetchone()
            
            if pedido and pedido['status'] == 'pendente':
                conn.execute("UPDATE pedidos SET status = 'processando' WHERE id = ?", (pedido_id,))
                conn.commit()
                
                servico_cod = pedido['servico']
                r = requests.get(BASE_URL, params={
                    "api_key": API_KEY,
                    "action": "getNumber",
                    "service": servico_cod,
                    "operator": "any",
                    "country": 73
                })
                
                if "ACCESS_NUMBER" in r.text:
                    dados = r.text.split(":")
                    activation_id = dados[1]
                    numero = dados[2]
                    
                    conn.execute("UPDATE pedidos SET status = 'entregue', activation_id = ?, numero = ? WHERE id = ?", 
                                 (activation_id, numero, pedido_id))
                else:
                    conn.execute("UPDATE pedidos SET status = 'falha_estoque' WHERE id = ?", (pedido_id,))
                
                conn.commit()
            conn.close()
            
    return jsonify({"status": "recebido"}), 200

@app.route("/status_pedido/<pedido_id>")
def status_pedido(pedido_id):
    conn = obter_conexao()
    pedido = conn.execute('SELECT * FROM pedidos WHERE id = ?', (pedido_id,)).fetchone()
    conn.close()
    
    if not pedido:
        return jsonify({"erro": "Pedido não existe"}), 404
        
    return jsonify({
        "status": pedido['status'],
        "numero": pedido['numero'],
        "activation_id": pedido['activation_id']
    })

@app.route("/sms/<id>")
def sms(id):
    r = requests.get(BASE_URL, params={"api_key": API_KEY, "action": "getStatus", "id": id})
    return jsonify({"resposta": r.text})

@app.route("/cancelar/<id>")
def cancelar(id):
    r = requests.get(BASE_URL, params={"api_key": API_KEY, "action": "setStatus", "id": id, "status": 8})
    return jsonify({"resposta": r.text})

@app.route("/novosms/<id>")
def novosms(id):
    r = requests.get(BASE_URL, params={"api_key": API_KEY, "action": "setStatus", "id": id, "status": 3})
    return jsonify({"resposta": r.text})

if __name__ == "__main__":
    app.run()
