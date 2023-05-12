
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode


app = Flask(__name__)

@app.route('/noticias', methods=['GET'])
def obter_noticias():
    capital = request.args.get('capital')
    
    capitais_do_brasil = [
        'rio-branco',
        'maceio',
        'macapa',
        'manaus',
        'salvador',
        'fortaleza',
        'vitoria',
        'goiania',
        'sao-luis',
        'cuiaba',
        'campo-grande',
        'belo-horizonte',
        'belem',
        'joao-pessoa',
        'curitiba',
        'recife',
        'teresina',
        'rio-de-janeiro',
        'natal',
        'porto-alegre',
        'porto-velho',
        'boa-vista',
        'florianopolis',
        'sao-paulo',
        'aracaju',
        'palmas',
        'brasilia'
    ]

    # Verificar se a capital foi fornecida
    if capital is None:
        return jsonify({'error': 'Capital não fornecida'}), 400

    capital_formatada = unidecode(capital.replace(" ", "-").lower())

    # Verificar se a capital fornecida está na lista de capitais brasileiras
    if capital_formatada not in capitais_do_brasil:
        return jsonify({'error': 'Capital inválida. Digite uma capital do Brasil.'}), 400

    # Construindo a URL da busca no G1
    url = f"https://g1.globo.com/busca/?q={capital}"

    # Realizando a requisição HTTP
    resposta = requests.get(url)

    # Verificando se a requisição foi bem-sucedida
    if resposta.status_code != 200:
        return jsonify({'error': 'Não foi possível obter as notícias.'}), 500

    # Obtendo o conteúdo da página
    conteudo = resposta.content

    # Criando o objeto BeautifulSoup
    soup = BeautifulSoup(conteudo, "html.parser")

    # Encontrando as notícias na página
    noticias = soup.find_all("div", class_="widget--info__text-container")

    # Extraindo os títulos das notícias e exibindo-os
    links = []
    for noticia in noticias:
        link_noticia = noticia.find("a")["href"]
        links.append(link_noticia)

    noticias_completas = []
    for link in links:
        url_noticia = f"https:{link}"
        resposta_noticia = requests.get(url_noticia)

        if resposta_noticia.status_code != 200:
            return jsonify({'error': 'Não foi possível obter as notícias.'}), 500

        conteudo_noticia = resposta_noticia.content
        soup_noticia = BeautifulSoup(conteudo_noticia, 'html.parser')
        script = soup_noticia.find('script').string
        start_index = script.find('"') + 1
        end_index = script.rfind('"')
        link_certo_noticia = script[start_index:end_index]

        ano = link_certo_noticia.split('/')[-4]

        resposta_certa_noticia = requests.get(link_certo_noticia)

        if resposta_certa_noticia.status_code != 200:
            return jsonify({'error': 'Não foi possível obter as notícias.'}), 500

        conteudo_certo_noticia = resposta_certa_noticia.content
        soup_certo_noticia = BeautifulSoup(conteudo_certo_noticia, 'html.parser')

        titulo_noticia = soup_certo_noticia.find("h1", class_="content-head__title")
        if titulo_noticia is not None:
            titulo = titulo_noticia.text
            subtitulo_noticia = soup_certo_noticia.find("h2", class_="content-head__subtitle")
            subtitulo = subtitulo_noticia.text
            texto_noticia = soup_certo_noticia.findAll("p", class_="content-text__container")
            texto = ''
            for paragrafo in texto_noticia:
              texto += paragrafo.text
            noticias_completas.append({'titulo': titulo, 'subtitulo': subtitulo, 'noticia': texto, 'capital': capital, 'ano': ano})
    
    # Retornar as notícias como resposta da API
    return jsonify(noticias_completas)

if __name__ == '__main__':
    app.run()
