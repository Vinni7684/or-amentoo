from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import sqlite3
import uuid
import mercadopago
import os  # Biblioteca essencial para ler as variáveis ocultas do Render

app = Flask(__name__)
CORS(app)

# ==========================================
# CONFIGURAÇÕES DE API (SEGURAS VIA VARIÁVEIS DE AMBIENTE)
# ==========================================
# O Python vai buscar os valores direto do painel Environment do Render
API_KEY = os.environ.get("BRAZUCA_API_KEY")
BASE_URL = "https://brazucasms.com/api/external"

MP_ACCESS_TOKEN = os.environ.get("MERCADOPAGO_ACCESS_TOKEN")
mp_sdk = mercadopago.SDK(MP_ACCESS_TOKEN)

# ==========================================
# CATÁLOGO DE SERVIÇOS E PREÇOS
# ==========================================
CATALOGO = {
    "ub": {"nome": "Uber", "preco": 1.00},
    "if": {"nome": "iFood", "preco": 5.00},
    "wa": {"nome": "WhatsApp", "preco": 6.50},
    "tg": {"nome": "Telegram", "preco": 4.50}
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
    payment_id = request.args.get("data.id")
    
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
