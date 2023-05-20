import requests
import psycopg2
import schedule
import time
from datetime import datetime

import capitaisBrasil

db_host = '127.0.0.1'
db_port = '5432'
db_name = 'IACidades'
db_user = 'postgres'
db_password = 'postgres'

def fazer_requisicao():
    for cidade in capitaisBrasil.capitais_do_brasil:
        url = f"http://localhost:5000/api/ia?capital={cidade}"
        response = requests.get(url)

        if response.status_code == 200:
            dados = response.json()
            data_hora_requisicao = datetime.now()
            data_hora_formatada = data_hora_requisicao.strftime("%Y-%m-%d %H:%M:%S") + f".{data_hora_requisicao.microsecond:06d}"
            salvar_no_banco_de_dados(dados, cidade, data_hora_formatada)
            print(f"Requisição para {cidade} feita com sucesso!")
        else:
            print(f"Falha na requisição para {cidade}")

def salvar_no_banco_de_dados(dados, cidade, data_hora_requisicao):
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        dbname=db_name,
        user=db_user,
        password=db_password
    )

    cursor = conn.cursor()

    # Verificar se a cidade já existe no banco de dados
    sql_verificar_cidade = "SELECT COUNT(*) FROM capital WHERE cidade = %s"
    cursor.execute(sql_verificar_cidade, (cidade,))
    cidade_existente = cursor.fetchone()[0]

    if cidade_existente > 0:
        # A cidade já existe, realizar o UPDATE
        sql_update = "UPDATE capital SET data_hora_requisicao = %s WHERE cidade = %s"
        cursor.execute(sql_update, (data_hora_requisicao, cidade))
        print(f"Cidade {cidade} atualizada no banco de dados")
    else:
        # A cidade não existe, realizar o INSERT
        for noticia in dados['sentimento']:
            sentimento = noticia['porcentagem']
            
            # Exemplo de comando SQL para inserção de dados
            sql_insert = "INSERT INTO capital (sentimento, cidade, data_hora_requisicao) VALUES (%s, %s, %s)"
            values = (sentimento, cidade, data_hora_requisicao)
            cursor.execute(sql_insert, values)

        print(f"Cidade {cidade} inserida no banco de dados")

    conn.commit()
    cursor.close()
    conn.close()


schedule.every(1).seconds.do(fazer_requisicao)

if __name__ == '__main__':
    while True:
        schedule.run_pending()
        time.sleep(1)