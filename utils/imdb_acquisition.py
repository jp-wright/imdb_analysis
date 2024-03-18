#!/opt/anaconda3/envs/imdb/bin/python

## IMDB allows you to export an entire list of films (incl. user-made ones, like this one) to CSV, but does not
## include the Metacritic Rating or other good info in it (dunno why).  This fixes that.

import time
import requests
import re
import logging
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
# logging.basicConfig(level=logging.INFO, filename='logs/imdb_acquisition.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
from bs4 import BeautifulSoup
from pandas import DataFrame, read_csv, concat, cut, qcut
from numpy import where
from streamlit import write, error
from utils.utilities import get_now, adjust_for_inflation
from utils.reference_info import gross_dct


class IMDB():
    def __init__(self, url: str) -> None:
        self.ATTRS = dict(title=r'href="/title/.*">(.+)</',
                        title_id=r'href="/title/(tt[\w\d]+)/',
                        year=r'class="lister-item-year text-muted unbold">.*\s?\((\d+)\)',
                        metacritic_rk=r'class="lister-item-index unbold text-primary">(\d+)',
                        metacritic_score=r'metascore\s\w+">(\d+)',
                        imdb_score=r'class="ipl-rating-star__rating">(\d\.?\d?)',
                        certificate=r'class="certificate">([a-zA-Z0-9\-]+)',  
                        runtime_mins=r'class="runtime">(\d+)',
                        genre=r'class="genre">\n?(.+)</',
                        director=r'Directors?:\n?<a href="/name/.*">(.+)</a>',
                        gross=r'Gross:</span>\n?<span\s.*data-value="([0-9\,]+)"',
                        imdb_votes=r'Votes:</span>\n?<span data-value="(\d+)',    
                        description=r'<p class="">\n?(.+)</p>',                   
                        )
        
        self.url = url
        self.df = self.scrape_list(url)

    def get_url_stem(self, url):
        '''Get url stem for list.  This is the URL without the page number.  This is used to scrape the entire list.
        '''
        user_list = re.search(r"(?P<URL>.*ls\d+)/?\??", url)
        watch_list = re.search(r"(?P<URL>.*ur\d+/watchlist)/?\??", url)
        if user_list:
            return user_list.group("URL")
        elif watch_list:
            logging.error(f"Provided URL {url} is an IMDb user 'Watchlist'. This type of list is not currently acquirable for this app.")
            error(f"🚨 Provided URL {url} is an IMDb user 'Watchlist'. This type of list is not currently acquirable for this app.")
            raise ValueError(f"Provided URL {url} is an IMDb user 'Watchlist'. This type of list is not currently acquirable for this app.")
            # return watch_list.group("URL")
        else:
            logging.error(f"Provided URL {url} not of an IMDb list.")
            error(f"🚨Provided URL {url} not of an IMDb list.")
            raise ValueError(f"Provided URL {url} not of an IMDb list.")

    def get_list_id(self, url):
        """Get the list_id from the URL.  This is used to name the CSV file."""
        match = re.search(r".*((list|user)/(?P<list_id>(ls|ur)\d+))/?\??", url)
        if match:
            return match.group("list_id")
        else:
            logging.error(f'No list_id found in {url}')
            raise ValueError(f'No list_id found in {url}')

    def get_pages_in_list(self, soup):
        try:
            tot_films = re.search(r'([\d,]+) titles', str(soup.find('div', attrs={'class': 'desc lister-total-num-results'}))).group(1)
            tot_films = int(tot_films.replace(',', ''))  ## remove commas for list of 1,000+
        except (AttributeError, IndexError, TypeError) as e:
            error(f"🚨 {e}: Number of pages in IMDb list not found.  Will not be able to acquire full list at this time.")
            tot_films = 0

        ## if less than 100 films, set to 100 so we can iterate through pages downstream
        if tot_films < 100: tot_films = 100

        return int(tot_films/100)
         
    def get_soup(self, url):
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        if 'This list is not public'.lower() in soup.text.lower():
            error("🚨 This list is not public.  Please make it public in 'EDIT' (top right of list) then 'SETTINGS' on IMDb and try again.")
            raise Exception("List acquisition failed.  List is not public.")
        return soup

    def get_list_title(self, soup):
        '''Get title of list for later CSV output.'''
        title = soup.find('h1', attrs={'class': 'header list-name'})
        if title:
            return title.text
        else:
            return "IMDb_film_list"

    def get_films(self, soup):
        '''each item in resulting list should be a single film'''
        return soup.find_all('div', attrs={'class': 'lister-item-content'})

    def get_all_attributes(self, text):
        dct = {}
        for attr, pat in self.ATTRS.items():
            try:
                res = re.search(pat, text).group(1)
            except (AttributeError, IndexError):
                print(attr, re.search(pat, text))
                res = 'N/A' if attr in ['director', 'description'] else '0'        
            dct.update({attr: res})
            if attr == 'title':
                print("Acquiring:", res)
        return dct

    def get_stars(self, text):
        if 'Stars:' in text:
            section = text[text.index('Stars:'): ]
            # section = text[text.index('Stars:'): text.index('Gross:')]  ## this might fail if no Gross....
            actors = re.findall('href="/name/.*">(.+)</a>', section)
        else: 
            actors = ['N/A'] * 4
        return actors

    def create_frame(self, all_films):
        return DataFrame(all_films).T

    def process_frame(self, frame):
        """Process the frame to clean it up and add new columns."""
        frame = self.specific_fixes(frame)
        frame = self.split_genres(frame)
        frame = self.split_stars(frame)
        frame = self.scale_imdb_rating_and_add_combo_col(frame)
        frame = self.add_critic_vs_ppl_col(frame)
        frame = self.add_rank_cols(frame)
        frame = self.create_col_decade(frame)
        frame = self.clean_frame(frame)
        frame = self.create_col_gross_adj(frame)
        frame = self.order_cols(frame)
        return frame

    def split_stars(self, frame):
        _ = DataFrame(frame['star'].to_list(), index=frame.index)
        _ = _.rename(columns={c: f'star{int(c)+1}' for c in _.columns})
        return concat([frame.drop('star', axis=1), _], axis=1)

    def split_genres(self, frame):
        _ = frame['genre'].str.split(',', expand=True)
        _ = _.rename(columns={c: f'genre{c+1}' for c in _.columns})
        for col in _:
            _[col] = _[col].str.strip()
        return concat([frame.drop('genre', axis=1), _], axis=1)

    def scale_imdb_rating_and_add_combo_col(self, frame, mc_wt=0.55):
        '''Scale IMDB rating to 100 and add to Metacritic rating, take weighted average.  Add as new column.'''
        imdb_wt = 1 - mc_wt

        ## accounts for films with no Metacritic score by setting combo_score to 0
        ## since they haven't been reviewd by Metacritic, their combo_score is would not be a combination of the two scores
        ## and would be misleading to include in the ranking.  Metacritic score 0 = film has not been reviewed by Metacritic.
        frame = frame.assign(imdb_score=frame['imdb_score'].astype(float) * 10, 
                            metacritic_score=frame['metacritic_score'].astype(float))\
                .assign(combo_score=lambda f: where(f['metacritic_score']>0, f['imdb_score'].mul(imdb_wt).add(f['metacritic_score'].mul(mc_wt)), 0))
        return frame

    def add_critic_vs_ppl_col(self, frame):
        '''Add column for difference between Metacritic and IMDb scores'''
        return frame.assign(critic_vs_ppl=lambda f: where(f['metacritic_score'].astype(int) > 0, f['metacritic_score'].sub(f['imdb_score']), 0))\
                    .assign(critic_vs_ppl_bin=lambda f: cut(f['critic_vs_ppl'].astype(float), 5, 
                                                             labels=['vlow', 'low', 'avg', 'high', 'vhigh']))

    def add_rank_cols(self, frame):
        '''Add rank columns for each rating type, and for combo rating'''
        for col in ['imdb_score', 'metacritic_score', 'combo_score', 'gross', 'critic_vs_ppl']:
            frame = frame.assign(**{f"{col.replace('score', 'rk') if col != 'gross' else col+'_rk'}": frame[col].astype(str).str.replace(',', '').astype(float).rank(ascending=False, method='dense')})
        return frame

    def create_col_decade(self, frame: DataFrame) -> DataFrame: 
        frame = frame.assign(decade=frame['year'].astype(str).str.replace(',', '').astype(int) // 10 * 10)#\
                    # .assign(decade_clr= lambda f: f['decade'].astype(str))
        return frame    
    
    def clean_frame(self, frame):
        '''Clean up frame for output'''
        return frame.drop_duplicates(subset=['title', 'year', 'director'])\
                .dropna(subset=['title', 'year', 'director'])\
                .assign(combo_score=lambda f: f['combo_score'].round(2))\
                .assign(combo_rk=lambda f: f['combo_rk'].astype(int))\
                .assign(metacritic_score=lambda f: f['metacritic_score'].astype(int))\
                .assign(metacritic_rk=lambda f: f['metacritic_rk'].astype(int))\
                .assign(imdb_score=lambda f: f['imdb_score'].astype(int))\
                .assign(imdb_rk=lambda f: f['imdb_rk'].astype(int))\
                .assign(year=lambda f: f['year'].astype(str).str.replace(',', '').astype(int))\
                .assign(decade=lambda f: f['decade'].astype(str).str.replace(',', '').astype(int))\
                .assign(gross=lambda f: f['gross'].astype(str).str.replace(',', '').astype(int))\
                .assign(gross_rk=lambda f: f['gross_rk'].astype(int).astype(str).str.replace(',', '').astype(int))\
                .assign(imdb_votes=lambda f: f['imdb_votes'].astype(str).str.replace(',', '').astype(int))\
                .assign(title=lambda f: f['title'].str.replace(r'&amp;', r'&'))

    def create_col_gross_adj(self, frame: DataFrame):
        '''adjust gross for inflation in 2023 dollars.  Add as new column *after* clean_frame() enforces 'gross' col to be int.  Extra logic handles films with missing years by setting their adj_gross to 0.  These are commonly TV Movies.  It is possible their years are available on IMDb, but I'll have to adjust the scraper and add extra logic.  Passing for now.'''
        frame = frame.assign(gross=lambda f: f['gross'].astype(str).str.replace(',', '').astype(int))
        mask = (frame['year'].isnull()) | (frame['year'] == 0)
        frame.loc[mask, 'gross_adj_2023'] = 0
        frame[~mask] = frame[~mask].assign(gross_adj_2023=lambda f: f.apply(lambda row: adjust_for_inflation(row['gross'], row['year'], 2023), axis=1))
        ## assign full col to int after mask, so we don't get NaNs/floats in non-masking rows
        return frame.assign(gross_adj_2023=lambda f: f['gross_adj_2023'].astype(int)).assign(gross_adj_2023_rk=lambda f: f['gross_adj_2023'].rank(ascending=False, method='dense').astype(int))
         
    def specific_fixes(self, frame):
        """Fixes for specific films.  Will be added to over time.
            Gross is for USA, not worldwide, when possible.
        """
        ### gross_dct structure: {film: [gross, year]}
        for film, data in gross_dct.items():
            title_mask = (frame['title'].str.lower() == film.lower())
            year_mask = (frame['year'].astype(str) == str(data[1]))
            if not frame[title_mask & year_mask].empty:
                frame.loc[title_mask & year_mask, 'gross'] = where(frame.loc[title_mask & year_mask, 'gross'].astype(str) == '0', str(gross_dct[film][0]), frame.loc[title_mask & year_mask, 'gross'])
        return frame

    def order_cols(self, frame):
        cols = ['title', 'year', 'decade', 'combo_score', 'combo_rk', 'metacritic_score', 'metacritic_rk', 'imdb_score', 'imdb_rk', 'critic_vs_ppl', 'critic_vs_ppl_bin', 'certificate', 'runtime_mins']\
            + [c for c in frame.columns if 'genre' in c]\
            + ['director']\
            + [c for c in frame.columns if 'star' in c]\
            + ['gross', 'gross_rk', 'gross_adj_2023', 'gross_adj_2023_rk', 'imdb_votes', 'title_id', 'description']
        assert len(cols) == len(frame.columns), 'Missing columns in order_cols()'
        return frame[cols].sort_values(['combo_rk', 'year', 'title'])

    def scrape_list(self, url: str):
        all_films = {}
        url_stem = self.get_url_stem(url)

        ## always want to get entire list, even if URL is for a specific page, so get the stem
        logging.info(f'{get_now()} Acquiring {url_stem}')
        soup = self.get_soup(url_stem)
        self.title = self.get_list_title(soup)

        def churn_non_watchlist(soup):
            """Scrape all pages of list.  New page every 100 films. If list has more than 100 films, scrape all pages.  If less than 100, scrape just the first page.  This is because the URL for the first page of a list is the same as the URL for the entire list.  If the list has more than 100 films, the URL for the first page will have a query string with a page number.  This is the only way to scrape the entire list."""
            pages = self.get_pages_in_list(soup)
            dur = f"{(pages+1)*18} seconds" if pages < 5 else f"{((pages+1)*18/60):.1f} minutes"
            write(f"ETA: ~{dur}")
            for page, url in enumerate([f'{url_stem}?sort=list_order,asc&st_dt=&mode=detail&page={p}' for p in range(1, pages+2)], 1):
                ## skip re-souping first page, already souped
                if page > 1:
                    logging.info("Sleeping 15 seconds.\n")
                    time.sleep(15)  ## don't want to get blocked
                    logging.info(f'{get_now()} Acquiring {url}')
                    soup = self.get_soup(url)

                logging.info(f'{get_now()} Acquiring {page}')

                for film in self.get_films(soup):
                    data = self.get_all_attributes(str(film))
                    data.update({'star': self.get_stars(str(film))})
                    all_films.update({data['title']: data})
            return all_films

        def churn_watchlist(soup):
            """So far as I can tell, user 'Watchlist's do not have pages, even if they eclipse 100 films. This might be a problem if a user has more than 100 films on their watchlist.  I'll have to test this. ...unsure if page loads all 100+ films without a user scrolling..."""
            for film in self.get_films(soup):
                write(film)
                data = self.get_all_attributes(str(film))
                data.update({'star': self.get_stars(str(film))})
                all_films.update({data['title']: data})
            return all_films  

        if 'watchlist' in url_stem:
            all_films = churn_watchlist(soup)
        elif 'list' in url_stem:
            all_films = churn_non_watchlist(soup)
        
        frame = self.create_frame(all_films)
        frame = self.process_frame(frame)

        list_id = self.get_list_id(url)
        frame.to_csv(f'data/output/imdb_list_{list_id}.csv', index=None)
        logging.info(f'{get_now()} imdb_list_{list_id}.csv saved to data/output')
        logging.info(f"{get_now()} Acquisition complete: {url_stem}")
        print(f"imdb_{list_id}.csv saved to data/output")
        print(f"Acquisition complete: {url_stem}")
        return frame.reset_index(drop=True)








if __name__ == '__main__':
    pass
    