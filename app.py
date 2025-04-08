from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session

import pandas as pd
import os
from werkzeug.utils import secure_filename
from connectorSQL import save_to_db, get_users_from_db, get_orders_by_user, ensure_user_exists, update_order_status,delete_order,get_all_orders,get_db_connection


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = 'deva'

# Cria o diretório de uploads, se não existir
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Função para processar o arquivo e preencher os campos automaticamente
def process_file(file_path):
    try:
        file_extension = file_path.split('.')[-1]
        if file_extension == 'xlsx':
            df = pd.read_excel(file_path)
            order_data = df.iloc[0].tolist()  # Lê os dados da primeira linha
            return order_data
        flash("Tipo de arquivo não suportado. Apenas .xlsx são permitidos.", 'danger')
        return None
    except Exception as e:
        flash(f"Erro ao processar o arquivo: {e}", 'danger')
        return None

# Função para verificar a senha (exemplo simples)
def check_password(password):
    correct_password = 'admin123'  # Ajuste a senha conforme necessário
    return password == correct_password

@app.route('/', methods=['GET', 'POST'])
def index():
    users = get_users_from_db()
    orders = []
    user_filter = None

    if request.method == 'POST':
        user = request.form.get('user', '').strip()
        order_id = request.form.get('order_id', '').strip()
        description = request.form.get('description', '').strip()
        cost_center = request.form.get('cost_center', '').strip()
        cost_responsible = request.form.get('cost_responsible', '').strip()
        division = request.form.get('division', '').strip()
        center = request.form.get('center', '').strip()
        company = request.form.get('company', '').strip()

        # Verificar se foi enviado apenas o usuário (busca)
        if user and not any([order_id, description, cost_center, cost_responsible, division, center, company]):
            orders = get_orders_by_user(user)
            return render_template('index.html', orders=orders, users=users, selected_user=user)

        # Verificar se todos os campos estão preenchidos para criar ordem
        if not all([user, order_id, description, cost_center, cost_responsible, division, center, company]):
            flash('Todos os campos são obrigatórios!', 'danger')
            return redirect(url_for('index'))

        ensure_user_exists(user)


        order_data = (
            order_id,
            description,
            cost_center,
            cost_responsible,
            division,
            center,
            company,
            user,
            'Pendente'
        )
        if save_to_db(order_data):
            flash('Ordem criada com sucesso!', 'success')
        else:
            flash('Erro ao salvar a ordem.', 'danger')

        return redirect(url_for('index', user=user))  # Redireciona com filtro

    # Método GET
    user_filter = request.args.get('user')
    if user_filter:
        orders = get_orders_by_user(user_filter)

    return render_template('index.html', orders=orders, users=users, selected_user=user_filter)

@app.route('/update_status/<int:order_id>', methods=['POST'])
def update_status(order_id):
    if not session.get('logged_in'):
        flash('Você precisa estar logado para alterar o status.', 'warning')
        return redirect(url_for('login'))

    new_status = request.form.get('status')
    
    conn = get_db_connection()
    conn.execute('UPDATE orders SET status = ? WHERE id = ?', (new_status, order_id))
    conn.commit()
    conn.close()

    flash(f'Status da ordem {order_id} atualizado para "{new_status}".', 'success')
    return redirect(url_for('all_orders'))


@app.route('/delete_order/<order_id>', methods=['POST'])
def delete_order_route(order_id):
    delete_order(order_id)  # Chama a função de deletar
    flash(f'Ordem {order_id} excluída com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if check_password(password):
            session['logged_in'] = True
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('all_orders'))
        else:
            flash('Senha incorreta!', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/all_orders')
def all_orders():
    if not session.get('logged_in'):
        flash('Você precisa fazer login para acessar essa página.', 'warning')
        return redirect(url_for('login'))

    orders = get_all_orders()
    return render_template('all_orders.html', orders=orders)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Você saiu com sucesso.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
