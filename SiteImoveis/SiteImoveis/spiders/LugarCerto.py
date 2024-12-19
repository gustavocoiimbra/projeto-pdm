import scrapy

class LugarCertoSpider(scrapy.Spider):
  name = "LugarCerto"
  all_dominains = ['www.lugarcerto.com.br']
  start_urls = ['https://www.lugarcerto.com.br/busca/aluguel']
  max_page = '5000'

  # Criando um padrão de como os links serão capturados e acessados
  def parse(self, response):
    #links é uma lista de seletores que recebe todo link de imovel
    links = response.css('div[class="col-sxs-10 col-xs-6 pull-right"] a::attr(href)').getall()

    #Passando link por link
    for link in links:
      yield response.follow(link, self.extract_data)

    #Definimos onde o BOT pode encontrar o link da próxima página e fazer uma extração automatrizada
    next_page = response.css('li[class="pull-right-768"] a::attr(href)').get()
    #Definimos onde o BOT pode encontrar o número da página, assim, é possível encerrar na página que definimos
    number_page = response.css('li[class="hidden-xs"] input::attr(value)').get()

    #Definimos quantas páginas o BOT deverá raspar
    if number_page == self.max_page:
      scrapy.CloseSpider("Finalizei a extração")
    else:
      #Passando o link da próxima página
      yield scrapy.Request(
              url = response.urljoin(next_page),
              callback=self.parse
        )

  #Criando um padrão de como o BOT deve extrair e salvar os dados da página
  def extract_data(self, response):
    import re

    #Definindo as variavéis para extrair o código, endereço e título do anúncio
    cod = response.css('span[class="codigo_imovel"]::text').get()
    titulo = response.css('div[class="row"] div[class="col-sxs-12 col-xs-12 margin-bottom-15"] h1::text').get()
    endereco = response.css('div[class="row"] div[class="col-sxs-12 col-xs-12 margin-bottom-15"] span::text').get()
    #cidade = re.split(r',', endereco)

    #Definindo a variavel para extrair o preço
    preco = response.css('.text-gray-dark::text').get().strip()
    #conv = re.findall('[0-9]+', preco_string)
    #del conv[-1]
    #preco_list = [''.join(conv)]

    #Definindo as variavéis para extrair o anunciante e as características básicas do imóvel
    anunciante = response.css('div[class="col-sxs-12 col-xs-12"] a::attr(title)').get()

    # Vamos pegar as característícas do ímovel
    caract = response.css('span[class="item-descricao text-bold clearfix"]::text').getall()
    desc_caract = response.css('span[class="item-descricao-conteudo margin-right-5"]::text').getall()
    desc = [item for item in desc_caract if item.strip()]

    area_string = [desc_caract[i] for i, x in enumerate(caract) if re.search('ÁREA', x)]
    #area = [0 if not area_string else re.findall('[0-9]+', area_string[0])]
    quartos = [desc_caract[i] for i, x in enumerate(caract) if re.search('QUARTO', x)]
    banheiros = [desc_caract[i] for i, x in enumerate(caract) if re.search('BANHEIRO', x)]
    vagas = [desc_caract[i] for i, x in enumerate(caract) if re.search('VAGA', x)]
    suite = [desc_caract[i] for i, x in enumerate(caract) if re.search('SUÍTE', x)]
    desc_imovel = response.css('div[class="descricao__imovel"] p::text').getall()


    yield {
        "codigo" : cod,
        "titulo" : titulo,
        "localizacao" : endereco,
        #"cidade" : cidade[-1].strip(),
        #"bairro": cidade[-2].strip(),
        "price" : preco,
        "quartos" : quartos,
        "banheiros" : banheiros,
        "vagas" : vagas,
        "suite" : suite,
        "area" : area_string,
        "anunciante" : anunciante,
        "descricao_imovel": desc_imovel,
        "link": str(response),
        "tipo_anuncio": "aluguel"
      }