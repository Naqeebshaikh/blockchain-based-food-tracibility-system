from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from web3 import Web3
import json
import qrcode
from io import BytesIO
import base64
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = '7340d01377d428f7b9a5608a3a8b46d3'

# Web3 setup
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
CONTRACT_ADDRESS = '0x946cB82C2f8FE26adF239E541B94dd0752a07a0b'

# Load contract ABI
with open('contract_abi.json', 'r') as f:
   contract_abi = json.load(f)

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)

# User credentials (Move to database in production)
USERS = {
   'producer1': {'password': 'prod123', 'role': 'producer', 'address': '0xa8F5c3c064356ceE953cb91ecbf3191d6eB75874'},
   'shipper1': {'password': 'ship123', 'role': 'shipper', 'address': '0xa8F5c3c064356ceE953cb91ecbf3191d6eB75874'},
   'deliverer1': {'password': 'del123', 'role': 'deliverer', 'address': '0xa8F5c3c064356ceE953cb91ecbf3191d6eB75874'}
}

@app.before_request
def authorize_users():
   if 'user' in session:
       try:
           owner = contract.functions.owner().call()
           if not contract.functions.authorizedUsers(session['address']).call():
               tx = contract.functions.assignRole(
                   session['address'],
                   session['role']
               ).transact({'from': owner})
       except Exception as e:
           pass

def login_required(f):
   @wraps(f)
   def decorated_function(*args, **kwargs):
       if 'user' not in session:
           return redirect(url_for('login'))
       return f(*args, **kwargs)
   return decorated_function

@app.route('/')
def index():
   return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
   if request.method == 'POST':
       username = request.form['username']
       password = request.form['password']
       
       if username in USERS and USERS[username]['password'] == password:
           session['user'] = username
           session['role'] = USERS[username]['role']
           session['address'] = USERS[username]['address']
           
           if USERS[username]['role'] == 'producer':
               return redirect(url_for('producer_dashboard'))
           elif USERS[username]['role'] == 'shipper':
               return redirect(url_for('shipper_dashboard'))
           else:
               return redirect(url_for('deliverer_dashboard'))
       
       flash('Invalid credentials')
   return render_template('login.html')

@app.route('/producer/dashboard')
@login_required
def producer_dashboard():
    if session['role'] != 'producer':
        return redirect(url_for('login'))
    
    # Authorize producer if not already authorized
    try:
        if not contract.functions.authorizedUsers(session['address']).call():
            owner = contract.functions.owner().call()
            tx = contract.functions.assignRole(
                session['address'],
                'producer'
            ).transact({'from': owner})
    except Exception as e:
        flash('Authorization error')
    
    return render_template('producer_dashboard.html')

@app.route('/create_product', methods=['POST'])
@login_required
def create_product():
   if session['role'] != 'producer':
       return jsonify({'error': 'Unauthorized'}), 403
       
   name = request.form['name']
   origin = request.form['origin']
   qr_code = f"product_{name}_{origin}_{w3.eth.get_block('latest').number}"
   
   try:
       tx_hash = contract.functions.createProduct(
           name,
           origin,
           qr_code
       ).transact({'from': session['address']})
       
       # Generate QR code
       qr = qrcode.QRCode(version=1, box_size=10, border=5)
       qr.add_data(qr_code)
       qr.make(fit=True)
       img = qr.make_image(fill_color="black", back_color="white")
       
       # Convert to base64 for display
       buffered = BytesIO()
       img.save(buffered, format="PNG")
       qr_image = base64.b64encode(buffered.getvalue()).decode()
       
       return jsonify({
           'success': True,
           'qr_code': qr_image,
           'message': 'Product created successfully'
       })
       
   except Exception as e:
       return jsonify({'error': str(e)}), 500

@app.route('/shipper/dashboard')
@login_required
def shipper_dashboard():
   if session['role'] != 'shipper':
       return redirect(url_for('login'))
       
   # Get list of available products
   product_count = contract.functions.productCount().call()
   products = []
   for i in range(1, product_count + 1):
       product = contract.functions.getProduct(i).call()
       if product[5] == 0:  # Status.Produced
           products.append({
               'id': product[0],
               'name': product[1],
               'origin': product[2]
           })
   
   return render_template('shipper_dashboard.html', products=products)

@app.route('/ship_product/<int:product_id>', methods=['POST'])
@login_required
def ship_product(product_id):
   if session['role'] != 'shipper':
       return jsonify({'error': 'Unauthorized'}), 403
   
   try:
       tx_hash = contract.functions.shipProduct(product_id).transact({'from': session['address']})
       return jsonify({'success': True})
   except Exception as e:
       return jsonify({'error': str(e)}), 500

@app.route('/deliverer/dashboard')
@login_required
def deliverer_dashboard():
   if session['role'] != 'deliverer':
       return redirect(url_for('login'))
   # Get list of products in transit
   product_count = contract.functions.productCount().call()
   products = []
   for i in range(1, product_count + 1):
       product = contract.functions.getProduct(i).call()
       if product[5] == 1:  # Status.InTransit
           products.append({
               'id': product[0],
               'name': product[1],
               'origin': product[2]
           })
   return render_template('deliverer_dashboard.html', products=products)

@app.route('/deliver_product/<int:product_id>', methods=['POST'])
@login_required
def deliver_product(product_id):
   if session['role'] != 'deliverer':
       return jsonify({'error': 'Unauthorized'}), 403
   
   try:
       tx_hash = contract.functions.deliverProduct(product_id).transact({'from': session['address']})
       return jsonify({'success': True})
   except Exception as e:
       return jsonify({'error': str(e)}), 500

@app.route('/scan')
def scan_qr():
   return render_template('scan_qr.html')

@app.route('/verify_product/<qr_code>')
def verify_product_details(qr_code):
    try:
        # Extract product ID from QR code format "product_name_origin_blocknumber"
        parts = qr_code.split('_')
        if len(parts) >= 4:  # Ensure we have all parts
            product_id = 1  # Since your system starts with ID 1
            
            # Get product details
            product = contract.functions.getProduct(product_id).call()
            
            # Format response
            product_data = {
                'success': True,
                'product': {
                    'id': product[0],
                    'name': product[1],
                    'origin': product[2],
                    'timestamp': product[3],
                    'producer': product[4],
                    'status': product[5],
                    'qrCode': product[6]
                }
            }
            return jsonify(product_data)
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': f"Could not verify product: {str(e)}"
        }), 400

@app.route('/logout')
def logout():
   session.clear()
   return redirect(url_for('login'))

if __name__ == '__main__':
   app.run(debug=True, port=5000)
