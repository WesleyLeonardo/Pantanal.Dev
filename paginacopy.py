
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from transformers import BertTokenizer, BertForSequenceClassification, AdamW
import torch
from torch.utils.data import DataLoader
from sklearn.metrics import accuracy_score, precision_score


exemplos_treinamento = [
    {
        'texto': 'Concursos públicos e processos seletivos disponíveis oferecem oportunidades para trabalhar em diversas cidades da região de Presidente Prudente (SP). Há vagas para diferentes áreas e as inscrições podem ser feitas pela internet e presencialmente.  Confira as oportunidades: Etecs As Escolas Técnicas Estaduais (Etec) de duas cidades do Oeste Paulista estão realizando processos seletivos para contratar professores de ensino médio e técnico. Os interessados podem se inscrever através do site da intuição.  Confira as oportunidades de acordo com as cidades:  Presidente Venceslau (SP)  A Etec de Presidente Venceslau realizará um novo processo seletivo para cadastros reservas de professores de ensino médio e técnico.  Segundo o edital, as oportunidades são para procedimentos de enfermagem, saúde mental, assistência de enfermagem em UTI e unidades especializadas, semiótica e enfermagem. Para concorrer, é necessário que os candidatos possuam licenciatura ou equivalente;  O profissional contratado deverá cumprir jornada de até 200 horas semanais, com remuneração de R$ 20,19 por hora/aula.  Os interessados na vaga de procedimentos de enfermagem podem se inscrever até o dia 11 de maio.  Já para enfermagem em saúde mental, as inscrições vão até dia 17 de maio.  As oportunidades para assistência de enfermagem em UTI e unidades especializadas e semiótica em enfermagem podem se inscrever até dia 22 de maio.  Adamantina (SP)  A Etec Engenheiro Herval Bellusci anunciou a realização de três processos seletivos, que tem como objetivo o cadastro reserva destinado a contratação temporária de professores de ensino médio-técnico.  Há chances para os cargos na área da Tecnologia da Informação Aplicada a Administração; Administração da Produção e Serviços (para a Habilitação Administração) e Teoria Geral de Processo, na disciplina de Serviços Jurídicos.  Os interessados devem ter idade mínima de 18 anos e possuir escolaridade em nível superior de licenciatura, com habilitação equivalente à área do cargo pleiteado.  Ao ser contratado, o docente deverá receber R$ 20,19 a cada hora-aula ministrada.  As inscrições para as áreas administrativas podem ser feitas até o dia 15 de maio. Já para os interessados em ministrar aulas na disciplina de Serviços Jurídicos devem se cadastrar até o dia 23 de maio.  Osvaldo Cruz (SP)  A Etec Amim Jundi anunciou a realização de três processos seletivos que pretende realizar cadastro reserva de professores do ensino médio e técnico.  As oportunidades disponíveis são para as seguintes áreas: Edital nº 027/06/2023: Normalização em Segurança do Trabalho (Segurança do Trabalho);Edital nº 027/07/2023: Fundamentos da Saúde e Segurança no Trabalho (Segurança do Trabalho);Edital nº 027/08/2023: Gestão de Conteúdo Web I (Informática para Internet Integrado ao Ensino Médio (MTec - Programa Novotec Integrado) - Parceria SEE). Para concorrer, é necessário ter idade mínima de 18 anos, escolaridade em nível superior de licenciatura, bacharelado ou de tecnologia, com habilitação equivalente à área do cargo.  Os interessados podem se inscrever até o dia 17 de maio, através do site.  Teodoro Sampaio (SP)  A Etec Professora Nair Luccas Ribeiro irá realizar cinco processos seletivos, que tem como objetivo a formação de cadastro reserva de professores de ensino médio e técnico.  As oportunidades estão disponíveis entre as seguintes áreas, conforme os editais: Edital nº 156/05/2023: Fundamentos da Saúde e Segurança no (do) Trabalho(Segurança do Trabalho);Edital nº 156/06/2023: Bioquímica dos Alimentos (Agroindústria);Edital nº 156/07/2023: Tecnologia de Carnes e Produtos Cárneos (Agroindústria);Edital nº 156/08/2023: Planejamento dos Processos Comerciais (Administração);Edital nº 156/09/2023: Desenvolvimento de Modelos de Negócios (Administração). Para concorrer a uma das oportunidades oferecidas, é necessário que o candidato possua idade mínima de 18 anos, além de escolaridade em nível superior de licenciatura, bacharelado ou de tecnologia, com habilitação equivalente à área do cargo pleiteado.  Os professores serão remunerados em R$ 20,19 a cada hora-aula ministrada.  Para participar, os interessados devem se inscrever até o dia 16 de maio. Unesp A Universidade Estadual Paulista (Unesp) irá realizar dois concursos públicos para contratar profissionais de nível superior em Presidente Prudente (SP).  Confira as oportunidades de acordo com os editais: Edital nº 69/2023: Professor Titular no Departamento de Física da Faculdade de Ciências e Tecnologia (1);Edital nº 51/2023: Professor Titular no Departamento de Educação Física, na disciplina de Medidas e Avaliação em Educação Física (1); As inscrições para todos os concursos devem ser feitas pela internet. A taxa de inscrição custa de R$ 86 a R$ 254.  As remunerações mensais variam de R$ 8.370,30 a R$ 19.855,85.  Confira os prazos de inscrições de acordo com cada edital: Edital nº 69/2023: até o dia 3 de julho; eEdital nº 63/2023: até o dia 4 de julho.Conselho Tutelar O Conselho Municipal dos Direitos da Criança e do Adolescente (CMDCA) está com processos seletivos abertos a fim de contratar profissionais de diversas cidades do Oeste Paulista. Confira:  Presidente Prudente (SP)  O CMDCA de Presidente Prudente anunciou um novo processo seletivo destinado à contratação temporária de cinco Conselheiros Tutelares.  Os interessados devem possuir ensino médio completo e idade superior a 21 anos.  Aos profissionais efetivados, o salário ofertado equivale a R$ 5.233,40 e deverá cumprir jornada de trabalho de 40 horas semanais para o exercícios das funções estipuladas ao cargo.  As inscrições serão recebidas até esta quarta-feira (10) das 8h às 12h e das 13h às 16h, exclusivamente de forma presencial, na sede da Fundação Inova Prudente, localizada na Rodovia Alberto Bonfliglioli, nº 2.700, Jardim Itaipu.  Iepê (SP)  O Conselho Municipal dos Direitos da Criança e do Adolescente (CMDCA) de Iepê está com um novo processo seletivo com cinco vagas.  As oportunidades são para membros do Conselho Tutelar no período de 2024 a 2027, com idade superior a 21 anos e que possuem ensino superior completo. Além disso, os interessados devem residir em Iepê.  Os profissionais deverão irão cumprir carga horária de 40 horas semanais com plantões noturnos, feriados e finais de semana. Eles serão beneficiados com remuneração de R$ 2.133,90, além de cartão alimentação de R$ 547,63.  Para concorrer, os candidatos devem se inscrever até dia 14 de maio, exclusivamente pela internet.  Monte Castelo (SP)  O Conselho Tutelar de Monte Castelo está com vagas abertas para membros.  De acordo com a documentação (Retificação I), as inscrições que anteriormente estavam previstas para serem realizadas no período de 17 de abril a 15 de maio passaram a ser previstas para ocorrer entre 10 de abril e 14 de maio.  Os profissionais admitidos deverão desempenhar atividades em carga horária de 40 horas semanais com escala de sobreaviso semanal noturno, nos finais de semana e feriados.  A remuneração será de R$ 1.378,76.  Os interessados devem se inscrever pela internet, até dia 14 de maio.  Junqueirópolis (SP)  O Conselho Municipal dos Direitos da Criança e do Adolescente de Junqueirópolis divulgou um novo processo seletivo para contratar conselheiro tutelar.  De acordo com o edital, serão preenchidas cinco vagas, com carga horária de 40 horas semanais, com escalas de plantões noturnos, feriados e finais de semana.  O salário será no valor de R$ 2.175,81.  Para concorrer, os candidatos devem ter idade mínima de 21 anos, comprovar escolaridade de ensino médio, residir no município e entre outros requisitos.  As inscrições podem ser feitas pela internet, até dia 15 de maio.  Presidente Epitácio (SP)  O Conselho Tutelar de Presidente Epitácio está com um novo processo seletivo aberto para contratar cinco membros do conselho tutelar.  Segundo o edital, as oportunidades são para os seguintes cargos de conselheiros tutelares: Advogado;Psicólogo;Assistente Social;Pedagogo; eConselheiro Tutelar. Os conselheiros vão desempenhar funções durante carga horária de 40 horas semanais e terão remuneração de R$ 2.702,10.  Para concorrer, os candidatos devem ter idade mínima de 21 anos, comprovar escolaridade de ensino médio, residir no município e entre outros requisitos.  Os interessados podem se inscrever até o dia 15 de maio, pelo site da instituição. Prefeitura de Presidente Epitácio  A Prefeitura de Presidente Epitácio divulgou a abertura de um novo concurso público que tem como objetivo a contratação de profissionais com níveis fundamental, médio, técnico e superior.  De acordo com o edital, serão preenchidas 35 vagas além da formação de cadastro reserva distribuídas entre os cargos:  Agente Comunitário de Saúde (4); Assistente Social (1); Auxiliar de Consultório Dentário; Auxiliar de Desenvolvimento Infantil; Auxiliar de Serviços Gerais (1); Coveiro; Bioquímico; Dentista; Desenhista; Enfermeiro; Escriturário (4); Farmacêutica; Fiscal Municipal; Fisioterapeuta; Mecânico; Médico Cardiologista (1); Médico Dermatologista; Médico do Trabalho (1); Médico Ginecologista/Obstetra (1); Médico Neurologista (1); Médico Ortopedista (1); Médico Otorrinolaringologista; Médico Pediatra (1); Médico Psiquiatra (1); Merendeira (3); Motorista (3); Nutricionista; Operador de Máquinas (6); Técnico de Enfermagem; Técnico de Farmácia; Terapeuta Ocupacional (1); Técnico em Informática (3); Assessor de Comunicação (1) e Analista Técnico em Tecnologia da Informação (1).  Os profissionais contratados para o cargo de Agente Comunitário de Saúde deverão atuar nas unidades: ESF Campinal; ESF Lagoinha; ESF Vila Gerônimo; ESF Vila Palmeira; ESF Vila Maria; ESF Jardim Real; ESF Jardim Real II; ESF Alto do Mirante; ESF Tibiriçá; ESF Vila Esperança; ESF Jardim Santa Rosa e PACS.  Os profissionais admitidos deverão cumprir a carga horária de 100 a 200 horas mensais. Os salários variam entre R$ 1.090,10 a R$ 5.404,21 ao mês.  Para concorrer a uma das oportunidades, os candidatos deverão comprovar a escolaridade exigida, bem como o registro no conselho de classe, idade mínima de 18 anos, CNH na categoria \"C\" e \"D\", residir na área de atuação, dentre outros requisitos que constam no edital.  Os interessados devem se inscrever até o dia 6 de junho, através do site. VÍDEOS: Tudo sobre a região de Presidente Prudente Veja mais notícias em g1 Presidente Prudente e Região.',
        'sentimento': 1
    },
    {
        'texto': 'Foi enterrado, em São Paulo, o corpo da cozinheira e apresentadora Palmirinha. Ela morreu neste domingo (7), aos 91 anos. Fãs, amigos e parentes participaram da despedida no Cemitério do Morumbi. O enterro foi restrito à família.  Palmirinha ensinou receitas culinárias por mais de 20 anos em programas de televisão. Ela estava internada desde o dia 11 de abril com problemas renais crônicos.  Veja também: Palmirinha: veja repercussão da morte da apresentadora e cozinheiraÍcone da TV, cozinheira foi a vovó de gerações de fãs e "amiguinhos"; veja perfil de Palmirinha',
        'sentimento': 0
    },
    {
        'texto': 'O vazamento de gás de um botijão provocou um incêndio em uma empresa alimentícia no bairro Jardim Montanhês, na Região Noroeste de Belo Horizonte, nesta sexta-feira (12).  Segundo o Corpo de Bombeiros, o incêndio foi registrado no segundo andar da empresa. Duas mulheres ficaram feridas. Uma sofreu queimaduras no rosto e, a outra, grávida, na perna.  O Serviço de Atendimento Móvel de Urgência (Samu) foi acionado. Veja os vídeos mais assistidos do g1 Minas:',
        'sentimento': 0
    },
    {
        'texto': 'Um homem foi esfaqueado, na madrugada desta quinta-feira (11), na Vila Maria, Região Nordeste de Belo Horizonte. A suspeita pelo crime é a própria mulher dele, que o teria ferido após uma briga.  De acordo com a Polícia Militar (PM), a vítima, de 47 anos, discutiu com ela em casa e foi ferido por, pelo menos, duas facadas. O homem foi socorrido para o Hospital Odilon Behrens, no bairro São Cristóvão, na Região Noroeste, com duas perfurações no peito e uma nas costas. Ele foi encaminhado direto para o bloco cirúrgico.  A suspeita pelo crime, de 41 anos, foi presa em flagrante. Ela não quis dar informações aos militares. Segundo o boletim de ocorrência, ela já tem passagem por outra tentativa de homicídio.  A faca utilizada no crime foi apreendida pela PM. A mulher foi conduzida à Delegacia de Plantão I (Deplan I), no bairro Floresta. Confira os vídeos mais assistidos do g1 Minas:',
        'sentimento': 0
    },
    {
        'texto': 'Os atores Alexandre Borges e Marcelo Drummond desembarcam em Belo Horizonte neste fim de semana na apresentação do espetáculo "Esperando Godot".  A peça fica em cartaz no sábado (13) e domingo (14), em curta temporada.  O espetáculo conta a história de Estragão e Vladimir, dois palhaços que se encontram no fim do mundo, na encruzilhada entre a paralisia e a tomada da ação.  Enquanto esperam Godot, embora não saibam quem ou o que é, a dupla se encontra com as personagens que passam pela estrada: Pozzo – O Domador, Felizardo – A Fera e O Mensageiro, que traz notícias inquietantes que podem determinar se terão que aguaradar Godot para sempre, ou se ficarão livres da espera.  Os ingressos custam a partir de R$ 30 e estão disponíveis na internet. Confira os vídeos mais vistos no g1 Minas:',
        'sentimento': 1
    },
    {
        'texto': 'Um jovem de 19 anos morreu, em Campo Grande, após resistir a abordagem policial realizada nos bairros Margarida e Giocondo Orsi na madrugada desta sexta-feira (12). O suspeito, identificado como Odair José Cézar Rodrigues, foi socorrido até o pronto Socorro da Santa Casa, mas não resistiu aos ferimentos causados por dois disparos.  A perícia foi acionada e os armamentos utilizados na abordagem apreendidos, assim como o revólver utilizado pelo jovem, de marca não aparente e com numeração raspada, foram apreendidos. O caso foi registrado no Centro Especializado de Polícia Integrada (Cepol).  Conforme relato policial, a Força Tática do 9º Batalhão estava em patrulhamento na região após várias ocorrências de crimes contra o patrimônio, principalmente por roubo e furto nas imediações de uma empresa de telefonia, quando a equipe avistou o jovem \"tentando esconder algum volume\".  Ao se deparar com a polícia e a aproximação da viatura, a equipe relatou que o jovem demonstrou nervosismo, tentando esconder a face e sair do local. A partir daí, a Força Tática começou o procedimento de abordagem, com ordem para que o suspeito colocasse a mão na cabeça e virasse de costas, pedido que foi ignorado. \"No momento em que os policiais se aproximaram o autor sacou da cintura um revólver e apontou em direção a equipe policial, não restando alternativa para os policiais, sendo realizado pela equipe dois disparos contra o suspeito para vencer a resistência imposta\", declarou em nota. Após aproximação de desarme do jovem, foi constatado que ele tinha sido atingido por dois disparos, um no tórax e outro na lateral direita, próxima a costela.  O suspeito foi socorrido e encaminhado ao pronto Socorro da Santa Casa, passando por diversos procedimentos, como injeção de adrenalina, ventilação mecânica, RCP e uso de desfibrilador, porém, morreu cerca de 20 minutos após dar entrada no Hospital.  Segundo informações da Polícia, Odair José Cézar Rodrigues apresentava passagem por roubo, roubo majorado, ameaça, violação de domicílio, tentativa de latrocínio, furto, tráfico de drogas e era um dos principias suspeito pelo roubo na região da Vila Margarida. Veja vídeos de Mato Grosso do Sul',
        'sentimento': 0
    }
    # Adicione mais exemplos de treinamento aqui
]

def criar_dataset_manual(exemplos):
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

    input_ids = []
    attention_masks = []
    labels = []

    for exemplo in exemplos:
        texto = exemplo['texto']
        sentimento = exemplo['sentimento']

        encoding = tokenizer.encode_plus(
            texto,
            add_special_tokens=True,
            max_length=512,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        input_ids.append(encoding['input_ids'].squeeze())
        attention_masks.append(encoding['attention_mask'].squeeze())
        labels.append(sentimento)

    dataset = torch.utils.data.TensorDataset(
        torch.stack(input_ids),
        torch.stack(attention_masks),
        torch.tensor(labels)
    )

    return dataset

# Carregar o tokenizer e o modelo BERT pré-treinado para análise de sentimento
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased')

dataset_treinamento = criar_dataset_manual(exemplos_treinamento)

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
    
    # Configurando o serviço do navegador Chrome
    chrome_path = "Caminho/para/o/executável/do/chrome"
    chrome_service = ChromeService(executable_path=chrome_path)

    # Configurando as opções do navegador Chrome
    chrome_options = webdriver.ChromeOptions()
    # Adicione quaisquer opções extras do Chrome, se necessário

    # Criando a instância do navegador Chrome
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    
    try:
        # Construindo a URL da busca no G1
        url = f"https://g1.globo.com/busca/?q={capital}"
        
         # Abrindo a página de busca no navegador Chrome
        driver.get(url)
        
        # Esperando até que as notícias sejam carregadas dinamicamente
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "widget--info__text-container")))
        
        conteudo = driver.page_source
        
        batch_size = 16
        epochs = 5
        learning_rate = 2e-5
        
        # Criar o dataloader para o dataset de treinamento manual
        train_loader = DataLoader(dataset_treinamento, batch_size=batch_size, shuffle=True)
        
        # Definir o otimizador e a função de perda
        optimizer = AdamW(model.parameters(), lr=learning_rate)
        loss_fn = torch.nn.CrossEntropyLoss()
        
        # Função de treinamento
        def train(model, dataloader, optimizer, loss_fn):
            model.train()
            total_loss = 0.0
            
            for batch in dataloader:
                optimizer.zero_grad()
                input_ids = batch[0].to(device)
                attention_mask = batch[1].to(device)
                labels = batch[2].to(device)
                
                outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
                loss = outputs.loss
                total_loss += loss.item()
                
                loss.backward()
                optimizer.step()
                
            avg_loss = total_loss / len(dataloader)
            return avg_loss
        
        # Loop de treinamento
        for epoch in range(epochs):
            loss = train(model, train_loader, optimizer, loss_fn)
            print(f'Epoch {epoch+1}/{epochs}, Loss: {loss}')

        # Realizando a requisição HTTP
        #resposta = requests.get(url)

        # Verificando se a requisição foi bem-sucedida
        #if resposta.status_code != 200:
         #   return jsonify({'error': 'Não foi possível obter as notícias.'}), 500

        # Obtendo o conteúdo da página
        #conteudo = resposta.content

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
            
            driver.get(f"https:{link}")

            # Esperando até que o título da notícia seja carregado
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "content-head__title")))

            # Obtendo o conteúdo da página da notícia
            conteudo_noticia = driver.page_source
            
            #url_noticia = f"https:{link}"
            #resposta_noticia = requests.get(url_noticia)

            #if resposta_noticia.status_code != 200:
             #   return jsonify({'error': 'Não foi possível obter as notícias.'}), 500

            #conteudo_noticia = resposta_noticia.content
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
                noticias_completas.append({'titulo': titulo, 'subtitulo': subtitulo, 'noticia': texto, 'capital': capital, 'ano': ano, 'sentimento': sentimento})
            
        return jsonify(noticias_completas)
    
    finally:
        # Fechando o navegador Chrome
        driver.quit()

if __name__ == '__main__':
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    app.run()