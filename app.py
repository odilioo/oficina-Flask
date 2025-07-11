import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def get_connection():
    return psycopg2.connect(
        host="dpg-d1o51bripnbc7386fi0g-a.oregon-postgres.render.com",
        database="oficina_db_47y2",
        user="oficina_db_47y2_user",
        password="PU5eZvc0fGJq49Hz7drIHOccGUw1v314",
        port=5432
    )

@app.route('/')
def index():
    id_filtro = request.args.get('id')
    modelo_filtro = request.args.get('modelo')
    servico_filtro = request.args.get('servico')

    conn = get_connection()
    cursor = conn.cursor()

    query = 'SELECT * FROM ordens WHERE 1=1'
    params = []

    if id_filtro:
        query += ' AND id = %s'
        params.append(id_filtro)
    if modelo_filtro:
        query += ' AND modelo LIKE %s'
        params.append(f'%{modelo_filtro}%')
    if servico_filtro:
        query += ' AND servico LIKE %s'
        params.append(f'%{servico_filtro}%')

    cursor.execute(query, params)
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
    chassi = request.form['chassi']
    nro_motor = request.form['nro_motor']
    renavam = request.form['renavam']
    cor = request.form['cor']
    km = request.form['km']
    portas = request.form['portas']
    comentario = request.form['comentario']

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO ordens 
        (placa, marca, modelo, ano, combustivel, cliente, cpf_cnpj, servico, valor,
         chassi, nro_motor, renavam, cor, km, portas, comentario)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (placa, marca, modelo, ano, combustivel, cliente, cpf_cnpj, servico, valor,
          chassi, nro_motor, renavam, cor, km, portas, comentario))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))


# Rota para excluir uma ordem de serviço
@app.route('/excluir_os/<int:id>')
def excluir_os(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM ordens WHERE id = %s', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/editar_os/<int:id>', methods=['GET', 'POST'])
def editar_os(id):
    conn = get_connection()
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
        chassi = request.form['chassi']
        nro_motor = request.form['nro_motor']
        renavam = request.form['renavam']
        cor = request.form['cor']
        km = request.form['km']
        portas = request.form['portas']
        comentario = request.form['comentario']
        cursor.execute('''
            UPDATE ordens SET placa=%s, marca=%s, modelo=%s, ano=%s, combustivel=%s, cliente=%s, cpf_cnpj=%s, servico=%s, valor=%s,
            chassi=%s, nro_motor=%s, renavam=%s, cor=%s, km=%s, portas=%s, comentario=%s
            WHERE id=%s
        ''', (placa, marca, modelo, ano, combustivel, cliente, cpf_cnpj, servico, valor,
              chassi, nro_motor, renavam, cor, km, portas, comentario, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    else:
        cursor.execute('SELECT * FROM ordens WHERE id = %s', (id,))
        ordem = cursor.fetchone()
        conn.close()
        return render_template('editar.html', ordem=ordem)


# Nova rota para impressão de ordem de serviço
@app.route('/imprimir_os/<int:id>')
def imprimir_os(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ordens WHERE id = %s', (id,))
    ordem = cursor.fetchone()
    conn.close()
    return render_template('imprimir.html', ordem=ordem)

if __name__ == '__main__':
    app.run(debug=True)