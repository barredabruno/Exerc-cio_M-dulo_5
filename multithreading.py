import requests
import time
import csv
import random
import concurrent.futures
from bs4 import BeautifulSoup

# global headers to be used for requests
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'}

MAX_THREADS = 10

def extract_movie_details(movie_link):
    time.sleep(random.uniform(0, 0.2))
    response = requests.get(movie_link, headers=headers)
    movie_soup = BeautifulSoup(response.content, 'html.parser')

    if movie_soup is not None:
        title = None
        date = None
        
        # Encontrando a seção específica
        page_section = movie_soup.find('section', attrs={'class': 'ipc-page-section'})
        
        if page_section is not None:
            # Encontrando todas as divs dentro da seção
            divs = page_section.find_all('div', recursive=False)
            
            if len(divs) > 1:
                target_div = divs[1]

                title_tag = movie_soup.find('span', class_='hero__primary-text')
                if title_tag:
                    title = title_tag.get_text()

                # Encontrando a data de lançamento
                date_tag = target_div.find('a', href=lambda href: href and 'releaseinfo' in href)
                if date_tag:
                    date = date_tag.get_text().strip()

                # Encontrando a classificação do filme
                rating_tag = movie_soup.find('a', class_='ipc-link ipc-link--baseAlt ipc-link--inherit-color')
                if rating_tag:
                    rating = rating_tag.get_text().strip()

                # Encontrando a sinopse do filme
                plot_tag = movie_soup.find('span', attrs={'data-testid': 'plot-xs_to_m'})
                if plot_tag:
                    plot_text = plot_tag.get_text().strip()

                with open('movies.csv', mode='a', newline='', encoding='utf-8') as file:
                    movie_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    if all([title, date, rating, plot_text]):
                        print(title, date, rating, plot_text)
                        movie_writer.writerow([title, date, rating, plot_text])


def extract_movies(soup):
    # Localiza a lista de filmes usando o novo seletor informado
    movies_table = soup.select_one(
        '#__next > main > div > div.ipc-page-content-container.ipc-page-content-container--center > section > div > div.ipc-page-grid.ipc-page-grid--bias-left > div > ul')

    if not movies_table:
        print("Não foi possível encontrar a lista de filmes. Verifique o seletor.")
        return

    # Busca os itens da lista de filmes
    movies_table_rows = movies_table.find_all('li')
    movie_links = ['https://imdb.com' + movie.find('a')['href'] for movie in movies_table_rows if movie.find('a')]

    threads = min(MAX_THREADS, len(movie_links))
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(extract_movie_details, movie_links)


def main():
    start_time = time.time()

    # IMDB Most Popular Movies - 100 movies
    popular_movies_url = 'https://www.imdb.com/chart/moviemeter/?ref_=nv_mv_mpm'
    response = requests.get(popular_movies_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Main function to extract the 100 movies from IMDB Most Popular Movies
    extract_movies(soup)

    end_time = time.time()
    print('Total time taken: ', end_time - start_time)

if __name__ == '__main__':
    main()
