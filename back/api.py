from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

db_host = '127.0.0.1'
db_port = '5432'
db_name = 'IACidades'
db_user = 'postgres'
db_password = 'postgres'

def conectar_banco():
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        dbname=db_name,
        user=db_user,
        password=db_password
    )
    return conn

@app.route('/api/capitalcheck')
def obter_tabela():
    conn = conectar_banco()
    cursor = conn.cursor()

    sql = "SELECT * FROM capital"
    cursor.execute(sql)
    rows = cursor.fetchall()

    data = []
    for row in rows:
        d = {
            'cidade': row[0],
            'sentimento': row[1],
            'data_hora_requisicao': str(row[2])
        }
        data.append(d)

    response = jsonify(data)
    cursor.close()
    conn.close()

    return response

if __name__ == '__main__':
    app.run(port=8000)
