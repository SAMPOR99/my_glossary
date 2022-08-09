import scrapy

PHRASE = '//h1[@class="flex-1"]/a/text()'
DEFINITION = '//*[@id="ud-root"]/main/div/div[2]/section/div[1]/div/div[2]/'
EXAMPLE = '//*[@id="ud-root"]/main/div/div[2]/section/div[1]/div/div[3]/'
NOTFOUND = '//*[@id="ud-root"]/main/div/div[2]/section/div/div[2]/text()'
URL = 'https://www.urbandictionary.com/'

def zipper(list_one, list_two):
    my_list = []
    counter=0
    while counter < max(len(list_one), len(list_two)):
        if counter < len(list_one):
            my_list.append(list_one[counter])
        if counter < len(list_two):
            my_list.append(list_two[counter])
        counter += 1
    return my_list

class Collins(scrapy.Spider):
    name = 'urban'
    start_urls = [
        URL
    ]
    custom_settings = {
        #'DONT_FILTER' : True,
        'CONCURRENT_REQUESTS': 24,
        'MEMUSAGE_LIMIT_MB': 2048,
        'MEMUSAGE_NOTIFY_MAIL': ['dsmisantiago@hotmail.com'],
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'ElSanti',
        'FEED_EXPORT_ENCODING': 'utf-8'
    }
    
    def parse(self, response):
        phrase = input("what phrase are you looking for: ")
        phrase = phrase.split()
        phrase = "+".join(phrase)
        yield response.follow(URL + phrase, callback=self.parse_phrase)
    
    def parse_phrase(self, response):
        title = response.xpath(PHRASE).get()
        
        plaintext = response.xpath(DEFINITION + "text()").getall()
        atext = response.xpath(DEFINITION + "a/text()").getall()

        example_text = response.xpath(EXAMPLE + "text()").getall()
        example_a = response.xpath(EXAMPLE + "a/text()").getall()

        if response.xpath(DEFINITION + "node()").get().__contains__("<a"):
            concatenated = zipper(atext, plaintext)
        else:    
            concatenated = zipper(plaintext, atext)
    
        if response.xpath(EXAMPLE + "node()").get().__contains__("<a"):
            concatenated_example = zipper(example_a, example_text)
        else:
            concatenated_example = zipper(example_text, example_a)

        
        with open("./mySlangWords.txt", "a", encoding="utf-8") as f:
            f.write(title.upper() + "\n")
            f.write("DEFINITION: " + "".join(concatenated))
            f.write("\n")
            f.write("Example: " + "".join(concatenated_example))
            f.write("\n")
            f.write("\n")

        another_phrase = input("what another_phrase are you looking for: ")
        another_phrase = another_phrase.split()
        another_phrase = "+".join(another_phrase)
        yield response.follow(URL + another_phrase, callback=self.parse_phrase)

