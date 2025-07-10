import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Inicializa banco de dados e tabela ordens se não existir
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ordens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT,
            marca TEXT,
            modelo TEXT,
            ano TEXT,
            combustivel TEXT,
            cliente TEXT,
            cpf_cnpj TEXT,
            servico TEXT,
            valor REAL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ordens')
    ordens = cursor.fetchall()
    conn.close()
    return render_template('index.html', ordens=ordens)

@app.route('/nova_os', methods=['POST'])
def nova_os():
    placa = request.form['placa']
    marca = request.form['marca']
    modelo = request.form['modelo']
    ano = request.form['ano']
    combustivel = request.form['combustivel']
    cliente = request.form['cliente']
    cpf_cnpj = request.form['cpf_cnpj']
    servico = request.form['servico']
    valor = request.form['valor']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO ordens 
        (placa, marca, modelo, ano, combustivel, cliente, cpf_cnpj, servico, valor)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (placa, marca, modelo, ano, combustivel, cliente, cpf_cnpj, servico, valor))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))


# Rota para excluir uma ordem de serviço
@app.route('/excluir_os/<int:id>')
def excluir_os(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM ordens WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/editar_os/<int:id>', methods=['GET', 'POST'])
def editar_os(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        placa = request.form['placa']
        marca = request.form['marca']
        modelo = request.form['modelo']
        ano = request.form['ano']
        combustivel = request.form['combustivel']
        cliente = request.form['cliente']
        cpf_cnpj = request.form['cpf_cnpj']
        servico = request.form['servico']
        valor = request.form['valor']
        cursor.execute('''
            UPDATE ordens SET placa=?, marca=?, modelo=?, ano=?, combustivel=?, cliente=?, cpf_cnpj=?, servico=?, valor=?
            WHERE id=?
        ''', (placa, marca, modelo, ano, combustivel, cliente, cpf_cnpj, servico, valor, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    else:
        cursor.execute('SELECT * FROM ordens WHERE id = ?', (id,))
        ordem = cursor.fetchone()
        conn.close()
        return render_template('editar.html', ordem=ordem)


# Nova rota para impressão de ordem de serviço
@app.route('/imprimir_os/<int:id>')
def imprimir_os(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ordens WHERE id = ?', (id,))
    ordem = cursor.fetchone()
    conn.close()
    return render_template('imprimir.html', ordem=ordem)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)