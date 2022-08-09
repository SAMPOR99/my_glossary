import scrapy
URL = 'https://www.wordsmyth.net/?level=3&ent='
WORD = '//h3[@class="headword syl" or @class="headword"]/text()'
DEFINITION = '//tr[@class="definition"]//td[@class="data"]/text()'
PRONUNCIATION = '//*[@id="main_frm"]/fieldset/div/table/tbody/tr[3]/td/table/tbody/tr[2]/td[2]/div/dl/dd/span/node()'

AVAILABLE_OPTIONS = '//*[@id="main_frm"]/fieldset/div/table/tbody/tr[3]/td/table/tbody/tr[2]/td[2]/div[1]/text()'
FIRST_OPTION = '//*[@id="main_frm"]/fieldset/div/table/tbody/tr[3]/td/table/tbody/tr[2]/td[2]/div/table/tbody/tr[1]/td[1]/a/@href'

OPTIONS_NAME = '//td[@class="data_column"]//a/text()'
OPTIONS_LINK = '//td[@class="data_column"]//a/@href'

def zipper(options_name, options_link, response):
    names = response.xpath(options_name).getall()
    links = response.xpath(options_link).getall()
    return dict(zip(names, links))


def there_options(availble_options, response):
    options = response.xpath(availble_options).get()
    if options.__contains__("Did you mean this word?"):
        return True
    return False


class WordsSpider(scrapy.Spider):
    name = 'words' 
    start_urls = [
        URL
    ]

    custom_settings = {
		# 'FEED_URI': 'words.json', 
        # 'FEED_FORMAT': 'json',
        'FEEDS' : {
			'words.jl' : { #edit: uri needs to be absolute path
				'format' : 'jl',
				'store_empty' : True,
				'indent': 4,
			}
		},		
        'CONCURRENT_REQUESTS': 24,
        'MEMUSAGE_LIMIT_MB': 2048,
        'MEMUSAGE_NOTIFY_MAIL': ['dsmisantiago@hotmail.com'],
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'ElSanti',
        'FEED_EXPORT_ENCODING': 'utf-8'
    }

    def parse(self, response):
        word = input("What word are you looking for: ")
        yield response.follow(URL + word, callback=self.parse_word, cb_kwargs={"word": word})


    def parse_word(self, response, **kwargs): 

        if not there_options(AVAILABLE_OPTIONS, response):
            link_definitions = response.xpath(FIRST_OPTION).get()
        else:
            options = zipper(OPTIONS_NAME, OPTIONS_LINK, response)
            print("Did you mean this options?")
            for key in options.keys():
                print(key)
            my_option = input('type in which option do you want or press Enter to search other word: ')
            my_option = my_option.strip()

            if my_option in options.keys():
                link_definitions = options[my_option]
            else: 
                link_definitions = "another_request"

        #Scraping the title if it's available
        title = response.xpath(WORD).get()
        if title:
            word = title
            word = word.replace("·","")
        elif kwargs:
            word = kwargs["word"]

        if link_definitions == "#":

            #Scraping pronunciation data and formatting it.
            pronunciation = response.xpath(PRONUNCIATION).getall()
            for i, v in enumerate(pronunciation):
                if v.__contains__("schwa"):
                    pronunciation[i] = "ə"
            pronunciation = "".join(pronunciation)
            
            #Scraping definitions data, and parse it into a list.
            definitions = response.xpath(DEFINITION).getall()
            definitions = [meaning for meaning in definitions if not meaning.__contains__("\n")]
            

            # In case you want to add arguments to scrapy
            quantity = getattr(self, "quantity", None)
            if quantity:
                quantity = int(quantity)
                definitions = definitions[:quantity]
            

            #Export the scraped data to a file.
            with open("./myglossary.txt", "a", encoding="utf-8") as f:
            #with open("./pragmaticglossary.txt", "a", encoding="utf-8") as f:
                f.write("\n")
                f.write(f"{word.upper()} -- pronunciation: {pronunciation}")
                f.write("\n")
                for value, definition in enumerate(definitions):
                    value += 1
                    f.write(f"definition {value}: {definition}")
                    f.write("\n")
            yield {
                'word': word.upper(),
                'pronunciation': pronunciation,
                'definitions': definitions,
            }


            #Making a new request
            new_request = input("another one?: ")
            yield scrapy.Request(URL+new_request, callback=self.parse_word,  cb_kwargs={"word": new_request})
        
        elif link_definitions == "another_request":
            new_request = input("another one?: ")
            yield scrapy.Request(URL+new_request, callback=self.parse_word,  cb_kwargs={"word": new_request})
        
        else:
            yield response.follow(link_definitions, callback=self.parse_word, cb_kwargs={"word": word})
