import scrapy
class ChavesNaMaoSpider(scrapy.Spider):
    name = "ChavesNaMao"
    allowed_domains = ["www.chavesnamao.com.br"]
    start_urls = ["https://www.chavesnamao.com.br/imoveis-a-venda/sp-sao-paulo/"]
    max_page = 50

    def parse(self, response):
      # Rastrear todos os links das páginas
      links = response.css('span[class="link"] ::attr(href)').getall()

      for link in links:
        yield response.follow(link, self.extract_data)


      if self.max_page != 0:
        self.max_page -= 1
        yield scrapy.Request(
              url = response.urljoin(f'https://www.chavesnamao.com.br/imoveis-a-venda/sp-sao-paulo/?pg={self.max_page}'),
              callback=self.parse)

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
          'area': area
      }