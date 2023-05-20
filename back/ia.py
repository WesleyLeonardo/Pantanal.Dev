
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode

from transformers import BertTokenizer, BertForSequenceClassification
import torch

import capitaisBrasil

tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
model = BertForSequenceClassification.from_pretrained('bert-base-multilingual-cased')

app = Flask(__name__)

@app.route('/api/ia', methods=['GET'])
def obter_noticias():
    capital = request.args.get('capital')
    
    if capital is None:
        return jsonify({'error': 'Capital não fornecida'}), 400

    capital_formatada = unidecode(capital.replace(" ", "-").lower())

    if capital_formatada not in capitaisBrasil.capitais_do_brasil:
        return jsonify({'error': 'Capital inválida. Digite uma capital do Brasil.'}), 400
    
    url = f"https://g1.globo.com/busca/?q={capital}"

    resposta = requests.get(url)

    if resposta.status_code != 200:
        return jsonify({'error': 'Não foi possível obter as notícias.'}), 500

    conteudo = resposta.content

    soup = BeautifulSoup(conteudo, "html.parser")
    
    paginacao = soup.find("a", class_="pagination__load-more")
    
    links = []
    
    noticias = soup.find_all("div", class_="widget--info__text-container")

    for noticia in noticias:
        link_noticia = noticia.find("a")["href"]
        links.append(link_noticia)
    
    link_paginacao = paginacao["href"]
        
    url_nova = f"https://g1.globo.com/busca/{link_paginacao}"
    
    resposta_nova = requests.get(url_nova)

    if resposta_nova.status_code != 200:
        return jsonify({'error': 'Não foi possível obter as notícias.'}), 500

    conteudo_novo = resposta_nova.content

    soup_novo = BeautifulSoup(conteudo_novo, "html.parser")

    noticias_novas = soup_novo.find_all("div", class_="widget--info__text-container")

    for noticia in noticias_novas:
        link_noticia = noticia.find("a")["href"]
        links.append(link_noticia)
         
    noticias_completas = []
        
    total_sentimento = 0
    media_sentimento = []
    
    def classificar_sentimento(texto):
        tokens = tokenizer.encode_plus(
            texto,
            add_special_tokens=True,
            max_length=512,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        input_ids = tokens['input_ids'].to(device)
        attention_mask = tokens['attention_mask'].to(device)

        outputs = model(input_ids, attention_mask=attention_mask)
        logits = outputs.logits
        predicoes = torch.softmax(logits, dim=1)
        classe_sentimento = torch.argmax(predicoes).item()
        
        sentimento = "positivo" if classe_sentimento == 1 else "negativo"
        return sentimento
    
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
            texto = " ".join([paragrafo.text.strip() for paragrafo in texto_noticia])
                
            sentimento = classificar_sentimento(texto)
            
            if sentimento == "negativo":
                total_sentimento += 0
            else:
                total_sentimento += 1
            
            noticias_completas.append({
                'titulo': titulo,
                'subtitulo': subtitulo,
                'noticia': texto,
                'capital': capital,
                'ano': ano,
                'sentimento': sentimento
            })
        
    sentimento_real = float(total_sentimento / len(noticias_completas))
    media_sentimento.append({
        'porcentagem': round(sentimento_real, 2)*100
    })
    
    return jsonify({
        'sentimento': media_sentimento,
        'noticias': noticias_completas
        })

if __name__ == '__main__':
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    app.run()