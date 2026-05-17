import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-me')

STATUS_OPTIONS = ['Aberta', 'Em andamento', 'Concluída']


def get_connection():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise RuntimeError('DATABASE_URL environment variable is not set')
    return psycopg2.connect(database_url)


@app.route('/')
def index():
    id_filtro = request.args.get('id', '').strip()
    modelo_filtro = request.args.get('modelo', '').strip()
    servico_filtro = request.args.get('servico', '').strip()
    status_filtro = request.args.get('status', '').strip()
    data_inicio = request.args.get('data_inicio', '').strip()
    data_fim = request.args.get('data_fim', '').strip()
    cliente_filtro = request.args.get('cliente', '').strip()

    conn = get_connection()
    cursor = conn.cursor()

    query = 'SELECT * FROM ordens WHERE 1=1'
    params = []

    if id_filtro:
        query += ' AND id = %s'
        params.append(id_filtro)
    if modelo_filtro:
        query += ' AND modelo ILIKE %s'
        params.append(f'%{modelo_filtro}%')
    if servico_filtro:
        query += ' AND servico ILIKE %s'
        params.append(f'%{servico_filtro}%')
    if status_filtro:
        query += ' AND status = %s'
        params.append(status_filtro)
    if cliente_filtro:
        query += ' AND cliente ILIKE %s'
        params.append(f'%{cliente_filtro}%')
    if data_inicio:
        query += ' AND criado_em >= %s'
        params.append(data_inicio)
    if data_fim:
        query += ' AND criado_em <= %s'
        params.append(data_fim + ' 23:59:59')

    query += ' ORDER BY id DESC'
    cursor.execute(query, params)
    ordens = cursor.fetchall()

    cursor.execute('SELECT COUNT(*) FROM ordens')
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM ordens WHERE status = 'Aberta'")
    total_abertas = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM ordens WHERE status = 'Em andamento'")
    total_andamento = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM ordens WHERE status = 'Concluída'")
    total_concluidas = cursor.fetchone()[0]
    cursor.execute('SELECT COALESCE(SUM(valor), 0) FROM ordens')
    receita_total = cursor.fetchone()[0]

    conn.close()

    stats = {
        'total': total,
        'abertas': total_abertas,
        'andamento': total_andamento,
        'concluidas': total_concluidas,
        'receita': receita_total,
    }

    return render_template('index.html', ordens=ordens, stats=stats,
                           status_options=STATUS_OPTIONS,
                           filtros=request.args)


@app.route('/nova_os', methods=['POST'])
def nova_os():
    fields = ['placa', 'marca', 'modelo', 'ano', 'combustivel',
              'cliente', 'cpf_cnpj', 'servico', 'valor', 'comentario', 'status']
    data = tuple(request.form.get(f, '') for f in fields)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO ordens
        (placa, marca, modelo, ano, combustivel, cliente, cpf_cnpj, servico, valor, comentario, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', data)
    conn.commit()
    conn.close()
    flash('Ordem de serviço criada com sucesso!', 'success')
    return redirect(url_for('index'))


@app.route('/excluir_os/<int:id>', methods=['POST'])
def excluir_os(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM ordens WHERE id = %s', (id,))
    conn.commit()
    conn.close()
    flash('Ordem de serviço excluída.', 'warning')
    return redirect(url_for('index'))


@app.route('/editar_os/<int:id>', methods=['GET', 'POST'])
def editar_os(id):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        fields = ['placa', 'marca', 'modelo', 'ano', 'combustivel',
                  'cliente', 'cpf_cnpj', 'servico', 'valor', 'comentario', 'status']
        data = [request.form.get(f, '') for f in fields]
        data.append(id)
        cursor.execute('''
            UPDATE ordens SET placa=%s, marca=%s, modelo=%s, ano=%s, combustivel=%s,
            cliente=%s, cpf_cnpj=%s, servico=%s, valor=%s, comentario=%s, status=%s
            WHERE id=%s
        ''', data)
        conn.commit()
        conn.close()
        flash('Ordem de serviço atualizada!', 'success')
        return redirect(url_for('index'))

    cursor.execute('SELECT * FROM ordens WHERE id = %s', (id,))
    ordem = cursor.fetchone()
    conn.close()
    return render_template('editar.html', ordem=ordem, status_options=STATUS_OPTIONS)


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
