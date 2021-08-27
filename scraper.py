from bs4 import BeautifulSoup
import requests


class ScraperManager:
  def __init__(self, schools, scrape_limit):
    self.schools = schools
    self.schools_sorted = []
    self.scrape_limit = scrape_limit

    self.__sort_schools_based_on_priority()


  def __get_schools_with_priority(self, priority_str):
    scraped_schools = []
    unscraped_schools = []
    for _, school in self.schools.items():
      if priority_str in school.priority:
        if school.last_scraped_status == '':
          unscraped_schools.append(school)
        else:
          scraped_schools.append(school)
    return scraped_schools, unscraped_schools


  def __sort_schools_based_on_priority(self):
    _, highest_priority_schools = self.__get_schools_with_priority('Highest Priority')
    _, high_priority_schools = self.__get_schools_with_priority('High Priority')
    _, medium_priority_schools = self.__get_schools_with_priority('Medium Priority')
    _, not_priority_schools = self.__get_schools_with_priority('Not A Priority')
    _, unknown_priority_schools = self.__get_schools_with_priority('Priority Unknown')
    _, private_schools = self.__get_schools_with_priority('Private (Needs Approval)')

    self.schools_sorted = highest_priority_schools + high_priority_schools + medium_priority_schools + not_priority_schools + unknown_priority_schools + private_schools


  def scrape(self):
    if self.scrape_limit > len(self.schools_sorted):
      self.scrape_limit = len(self.schools_sorted)

    count = 1
    for school in self.schools_sorted:
      if count > self.scrape_limit:
        break

      query = school.get_query_string()
      print('[{0} / {1}] Querying "{2}". Priority: "{3}'.format(
        count, self.scrape_limit, query, school.priority)
      )
      count = count + 1

      wiki_link = GoogleSearchResultWikipediaScraper.get_wikipedia_link(query)
      if wiki_link is None:
        school.last_scraped_status = False
        school.last_scraped_message = '[FAILED at Google Search Result] Unable to find the Wikipedia link'
        print(school.last_scraped_message + '\n')
        continue

      color = WikipediaSchoolColorScraper.get_color(wiki_link)
      if color is None:
        school.last_scraped_status = False
        school.last_scraped_message = '[FAILED at Wikipedia] Unable to find color in the Wikipedia page'
      else:
        if color in ['', ' ', '  ']:
          color = WikipediaSchoolColorScraper.get_hex_color(wiki_link)
          color = WikipediaSchoolColorScraper.standardize_color_text(color)
        school.color = color
        school.last_scraped_status = True
        school.last_scraped_message = '[SUCCESS] Color is {0}'.format(color)
      print(school.last_scraped_message + '\n')


class WikipediaSchoolColorScraper:
  @staticmethod
  def get_color(url):
    html_text = requests.get(url)
    soup = BeautifulSoup(html_text.content, 'html.parser')
    info = soup.find_all('th', class_ = 'infobox-label')
    for element in info:
      if ('Color(s)' in element):
        color = element
        color = color.find_next_sibling('td').text
        color = WikipediaSchoolColorScraper.standardize_color_text(color)
        return color
    return None


  @staticmethod
  def get_hex_color(url):
    html_text = requests.get(url)
    soup = BeautifulSoup(html_text.content, 'html.parser')
    info = soup.find_all('th', class_ = 'infobox-label')
    text_color = 'No color found'
    for element in info:
      if ('Color(s)' in element):
        color = element            
        text_color = color.find_next_sibling('td')
        text_color = text_color.find_all('span')
        new_hex = []
        join = ''
        join_final = ' '
        for item in text_color:
          new_item = str(item)
          color = []
          if ('background-color:' in new_item):
            x = new_item.find('background-color')
            y = x + 16
            hex = []
            while new_item[y + 1] != ';':
              hex.append(new_item[y + 1])
              y = y + 1
            color = str(join.join(hex))
            new_hex.append(color + '  ')
          
          if (new_item.find('background-color:') == -1) and (new_item.find('background:') > -1):
            x = new_item.find('background:')
            y = x + 10
            hex = []
            while new_item[y + 1] != ';':
              hex.append(new_item[y + 1])
              y = y + 1
            color = str(join.join(hex)) 
            new_hex.append(color + '  ')
        break
    return join_final.join(new_hex)


  @staticmethod
  def remove_preceding_and_following_whitespaces(color):
    first_index_of_char = 0
    last_index_of_char = 0
    for i in range(len(color)):
      if 65 <= ord(color[i]) <= 90 or 97 <= ord(color[i]) <= 122 or 48 <= ord(color[i]) <= 57 or 35 == ord(color[i]):
        first_index_of_char = i
        break

    for i in range(len(color) - 1, -1, -1):
      if 65 <= ord(color[i]) <= 90 or 97 <= ord(color[i]) <= 122 or 48 <= ord(color[i]) <= 57 or 35 == ord(color[i]):
        last_index_of_char = i
        break
    
    if first_index_of_char == 0 and last_index_of_char == 0:
      return ''
    return color[first_index_of_char:last_index_of_char + 1]


  @staticmethod
  def standardize_color_text(color):
    text = color
    # Replace multi-whitespaces (more than 1 whitespaces consecutively) with comma
    new_text = ''
    i = 0
    while i < len(text):
      if (text[i] == ' ' or text[i] == '\t' or text[i] == '\n'):
        if i + 1 < len(text) and (text[i + 1] == ' ' or text[i + 1] == '\t' or text[i + 1] == '\n'):
          new_text = new_text + ','
          while i < len(text) and (text[i] == ' ' or text[i] == '\t' or text[i] == '\n'):
            i = i + 1
        else:
          new_text = new_text + text[i]
          i = i + 1
      else:
        new_text = new_text + text[i]
        i = i + 1

    # Replace and, & with comma
    new_text = new_text.lower()
    new_text = new_text.replace('and', ',')
    new_text = new_text.replace('&', ',')
    tmp = ''
    for char in new_text:
      if char.isalnum() or char == ',' or char == ' ' or char == '#':
        tmp = tmp + char
    new_text = tmp

    # Build up the new text
    text_components = new_text.split(',')
    new_text = ''
    for component in text_components:
      component = WikipediaSchoolColorScraper.remove_preceding_and_following_whitespaces(component)
      if component != '':
        component = component.title()
        new_text = new_text + component + ', '

    return new_text[:-2]


class GoogleSearchResultWikipediaScraper:
  @staticmethod
  def get_wikipedia_link(query):
    headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
    }

    keyword = query.replace(' ', '+')
    g_link = 'https://www.google.com/search?q={0}+wikipedia+en'.format(keyword)
    html = requests.get(g_link, headers=headers).text
    soup = BeautifulSoup(html, 'lxml')

    for container in soup.findAll('div', class_='tF2Cxc'):
      link = container.find('a')['href']
      if (link.startswith('https://en.wikipedia.org/wiki/')):
        return link
    return None

if __name__ == '__main__':
  url = 'https://en.wikipedia.org/wiki/A%26M_Consolidated_High_School'
  WikipediaSchoolColorScraper.get_color(url)

  # text = 'Red and #CFBA12'
  # print(WikipediaSchoolColorScraper.standardize_color_text(text))
