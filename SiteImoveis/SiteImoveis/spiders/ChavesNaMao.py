import scrapy
class ChavesNaMaoSpider(scrapy.Spider):
    name = "ChavesNaMao"
    allowed_domains = ["www.chavesnamao.com.br"]
    # start_urls = ["https://www.chavesnamao.com.br/imoveis-a-venda/sp-sao-paulo/"]
    # max_pages = 50

    def __init__(self, estado="sp", cidade="sao-paulo", max_pages=50, *args, **kwargs):
      self.estado = estado
      self.cidade = cidade
      self.max_pages = int(max_pages)
      self.pag = 0
      self.start_urls = [f"https://www.chavesnamao.com.br/casas-a-venda/{self.estado}-{self.cidade}/"]
                        # https://www.chavesnamao.com.br/imoveis-para-alugar/sp-sao-paulo/
                        # https://www.chavesnamao.com.br/apartamentos-a-venda/sp-sao-paulo/
                        # https://www.chavesnamao.com.br/casas-a-venda/sp-sao-paulo/


    def parse(self, response):
      # Rastrear todos os links das páginas
      links = response.css('span[class="link"] ::attr(href)').getall()

      for link in links:
        yield response.follow(link, self.extract_data)


      if self.pag != self.max_pages:
        self.pag += 1
        yield scrapy.Request(
              url=f'https://www.chavesnamao.com.br/casas-a-venda/{self.estado}-{self.cidade}/?pg={self.pag}',
              callback=self.parse,
              errback=self.error_parse)

    # Exrair os dados dos imovéis
    def extract_data(self, response):

      # Título do anúncio
      title = response.css('h1[class="userTitle"] b::text').get()
      # Localização (Bairro - Cidade)
      location = response.css('span[class="location"] b::text').get()
      # Estado
      estado = response.css('ul[class="breadcrumb__Container-o5juxr-0 ebscCD"] ::text').getall()[3]
      # Valor do imóvel no anúncio
      price = response.css('div[class="price"] b::text').get()
      # Retorna um lista com os items da descrição
      desc = response.css('div[class="pdBox"] ul[class="mainlist"] ::text').getall()
      desc = [item for item in desc if item.strip()]

      descricao = response.css('p[id="dsc"] ::text').getall()


      quartos = [desc[i-1] for i, item in enumerate(desc) if "Quartos" in item]
      banheiros = [desc[i-1] for i, item in enumerate(desc) if "Banheiros" in item]
      vagas = [desc[i-1] for i, item in enumerate(desc) if "Garagens" in item]
      suite = [desc[i-1] for i, item in enumerate(desc) if "Suíte" in item]
      area = [item for item in desc if "m²" in item]

      yield {
          'titulo': title,
          'localizacao': location,
          'estado': estado,
          'price': price, # Target
          'quartos': quartos,
          'banheiros': banheiros,
          'vagas': vagas,
          'suite': suite,
          'area': area,
          'descricao_anuncio': descricao,
          'tipo_anuncio': 'compra_venda'
      }

    def error_parse(self, failure):
      # Registrar erro
      self.logger.error(f"Erro ao acessar: {failure.request.url}")

      if failure.check(scrapy.exceptions.HttpError):
        response = failure.value.response
        self.logger.error(f"Erro HTTP {response.status} ao acessar {response.url}")

      elif failure.check(scrapy.exceptions.DNSLookupError):
        request = failure.request
        self.logger.error(f"Erro de DNS ao acessar {request.url}")

      elif failure.check(scrapy.exceptions.TimeoutError):
        request = failure.request
        self.logger.error(f"Timeout ao acessar {request.url}")