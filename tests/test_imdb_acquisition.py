import unittest
from utils.imdb_acquisition import IMDB
import pandas as pd

class TestIMDBScraper(unittest.TestCase):
    def setUp(self):
        self.url = "https://www.imdb.com/list/ls040479474/?sort=list_order,asc&st_dt=&mode=detail&page=1"
        self.imdb = IMDB(self.url)

    def test_get_url_stem(self):
        url = "https://www.imdb.com/list/ls040479474/?sort=list_order,asc&st_dt=&mode=detail&page=1"
        expected_url_stem = "https://www.imdb.com/list/ls040479474/"
        self.assertEqual(self.imdb.get_url_stem(url), expected_url_stem)

    def test_get_list_id(self):
        url = "https://www.imdb.com/list/ls040479474/?sort=list_order,asc&st_dt=&mode=detail&page=1"
        expected_list_id = "ls040479474"
        self.assertEqual(self.imdb.get_list_id(url), expected_list_id)

    def test_get_pages_in_list(self):
        soup = self.imdb.get_soup(self.url)
        expected_pages = 2
        self.assertEqual(self.imdb.get_pages_in_list(soup), expected_pages)

    def test_get_title(self):
        soup = self.imdb.get_soup(self.url)
        expected_title = "IMDb_film_list"
        self.assertEqual(self.imdb.get_title(soup), expected_title)

    def test_get_films(self):
        soup = self.imdb.get_soup(self.url)
        films = self.imdb.get_films(soup)
        self.assertTrue(len(films) > 0)

    def test_get_all_attributes(self):
        text = '<div class="lister-item-content">\n<h3 class="lister-item-header">\n<span class="lister-item-index unbold text-primary">1.</span>\n<a href="/title/tt0111161/">The Shawshank Redemption</a>\n<span class="lister-item-year text-muted unbold">(1994)</span>\n</h3>\n<p class="text-muted">\n<span class="certificate">R</span>\n<span class="ghost">|</span>\n<span class="runtime">142 min</span>\n<span class="ghost">|</span>\n<span class="genre">\nDrama            </span>\n</p>\n<div class="ratings-bar">\n<div class="inline-block ratings-imdb-rating" name="ir" data-value="9.3">\n<span class="global-sprite rating-star imdb-rating"></span>\n<strong>9.3</strong>\n</div>\n<div class="inline-block ratings-metascore" name="ms" data-value="80">\n<span class="metascore favorable">80        </span>\n        Metascore\n</div>\n</div>\n<p class="">\nTwo imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.\n</p>\n<p class="text-muted">\nDirector:\n<a href="/name/nm0001104/">Frank Darabont</a>\n<span class="ghost">|</span>\nStars:\n<a href="/name/nm0000209/">Tim Robbins</a>,\n<a href="/name/nm0000151/">Morgan Freeman</a>,\n<a href="/name/nm0006669/">Bob Gunton</a>,\n<a href="/name/nm0006667/">William Sadler</a>\n</p>\n</div>'
        expected_attributes = {
            'title': 'The Shawshank Redemption',
            'year': '1994',
            'metacritic_rk': '1',
            'metacritic_score': '80',
            'imdb_score': '9.3',
            'certificate': 'R',
            'runtime_mins': '142',
            'genre': 'Drama',
            'director': 'Frank Darabont',
            'description': 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.'
        }
        self.assertEqual(self.imdb.get_all_attributes(text), expected_attributes)

    def test_get_stars(self):
        text = '<p class="text-muted">\nDirector:\n<a href="/name/nm0001104/">Frank Darabont</a>\n<span class="ghost">|</span>\nStars:\n<a href="/name/nm0000209/">Tim Robbins</a>,\n<a href="/name/nm0000151/">Morgan Freeman</a>,\n<a href="/name/nm0006669/">Bob Gunton</a>,\n<a href="/name/nm0006667/">William Sadler</a>\n</p>'
        expected_stars = ['Tim Robbins', 'Morgan Freeman', 'Bob Gunton', 'William Sadler']
        self.assertEqual(self.imdb.get_stars(text), expected_stars)

    def test_create_frame(self):
        all_films = {
            'title': ['The Shawshank Redemption', 'The Godfather'],
            'year': ['1994', '1972'],
            'metacritic_rk': ['1', '2'],
            'metacritic_score': ['80', '100'],
            'imdb_score': ['9.3', '9.2'],
            'certificate': ['R', 'R'],
            'runtime_mins': ['142', '175'],
            'genre': ['Drama', 'Crime'],
            'director': ['Frank Darabont', 'Francis Ford Coppola'],
            'description': ['Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.', 'The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.']
        }
        expected_frame = pd.DataFrame(all_films)
        self.assertEqual(self.imdb.create_frame(all_films), expected_frame)

    def test_process_frame(self):
        frame = pd.DataFrame({
            'title': ['The Shawshank Redemption', 'The Godfather'],
            'year': ['1994', '1972'],
            'metacritic_rk': ['1', '2'],
            'metacritic_score': ['80', '100'],
            'imdb_score': ['9.3', '9.2'],
            'certificate': ['R', 'R'],
            'runtime_mins': ['142', '175'],
            'genre': ['Drama', 'Crime'],
            'director': ['Frank Darabont', 'Francis Ford Coppola'],
            'description': ['Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.', 'The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.']
        })
        expected_frame = pd.DataFrame({
            'title': ['The Shawshank Redemption', 'The Godfather'],
            'year': [1994, 1972],
            'decade': [1990, 1970],
            'combo_score': [9.3, 9.2],
            'combo_rk': [1, 2],
            'metacritic_score': [80, 100],
            'metacritic_rk': [1, 2],
            'imdb_score': [9.3, 9.2],
            'imdb_rk': [1, 2],
            'certificate': ['R', 'R'],
            'runtime_mins': [142, 175],
            'genre1': ['Drama', 'Crime'],
            'director': ['Frank Darabont', 'Francis Ford Coppola'],
            'description': ['Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.', 'The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.']
        })
        self.assertEqual(self.imdb.process_frame(frame), expected_frame)

    def test_split_stars(self):
        frame = pd.DataFrame({
            'title': ['The Shawshank Redemption', 'The Godfather'],
            'star': ['Tim Robbins, Morgan Freeman, Bob Gunton, William Sadler', 'Marlon Brando, Al Pacino, James Caan, Diane Keaton']
        })
        expected_frame = pd.DataFrame({
            'title': ['The Shawshank Redemption', 'The Godfather'],
            'star1': ['Tim Robbins', 'Marlon Brando'],
            'star2': ['Morgan Freeman', 'Al Pacino'],
            'star3': ['Bob Gunton', 'James Caan'],
            'star4': ['William Sadler', 'Diane Keaton']
        })
        self.assertEqual(self.imdb.split_stars(frame), expected_frame)

    def test_split_genres(self):
        frame = pd.DataFrame({
            'title': ['The Shawshank Redemption', 'The Godfather'],
            'genre': ['Drama, Crime', 'Crime, Drama']
        })
        expected_frame = pd.DataFrame({
            'title': ['The Shawshank Redemption', 'The Godfather'],
            'genre1': ['Drama', 'Crime'],
            'genre2': ['Crime', 'Drama']
        })
        self.assertEqual(self.imdb.split_genres(frame), expected_frame)

    def test_scale_imdb_rating_and_add_combo_col(self):
        frame = pd.DataFrame({
            'title': ['The Shawshank Redemption', 'The Godfather'],
            'imdb_score': [9.3, 9.2],
            'metacritic_score': [80, 100]
        })
        expected_frame = pd.DataFrame({
            'title': ['The Shawshank Redemption', 'The Godfather'],
            'imdb_score': [93, 92],
            'metacritic_score': [80, 100],
            'combo_score': [86.5, 95.5]
        })
        self.assertEqual(self.imdb.scale_imdb_rating_and_add_combo_col(frame), expected_frame)

    def test_add_rank_cols(self):
        frame = pd.DataFrame({
            'title': ['The Shawshank Redemption', 'The Godfather'],
            'imdb_score': [9.3, 9.2],
            'metacritic_score': [80, 100],
            'combo_score': [86.5, 95.5],
            'gross': [1000000, 2000000]
        })
        expected_frame = pd.DataFrame({
            'title': ['The Shawshank Redemption', 'The Godfather'],
            'imdb_score': [9.3, 9.2],
            'metacritic_score': [80, 100],
            'combo_score': [86.5, 95.5],
            'gross': [1000000, 2000000],
            'imdb_rk': [1, 2],
            'metacritic_rk': [1, 2],
            'combo_rk': [1, 2],
            'gross_rk': [2, 1]
        })
        self.assertEqual(self.imdb.add_rank_cols(frame), expected_frame)

    def test_create_col_decade(self):
        frame = pd.DataFrame({
            'title': ['The Shawshank Redemption', 'The Godfather'],
            'year': [1994, 1972]
        })
        expected_frame = pd.DataFrame({
            'title': ['The Shawshank Redemption', 'The Godfather'],
            'year': [1994, 1972],
            'decade': [1990, 1970]
        })
        self.assertEqual(self.imdb.create_col_decade(frame), expected_frame)

    def test_clean_frame(self):
        frame = pd.DataFrame({
            'title': ['The Shawshank Redemption', 'The Godfather'],
            'year': ['1994', '1972'],
            'decade': ['1990', '1970'],
            'combo_score': [9.3, 9.2],
            'combo_rk': [1, 2],
            'metacritic_score': [80, 100],
            'metacritic_rk': [1, 2],
            'imdb_score': [9.3, 9.2],
            'imdb_rk': [1, 2],
            'certificate': ['R', 'R'],
            'runtime_mins': ['142', '175'],
            'genre': ['Drama', 'Crime'],
            'director': ['Frank Darabont', 'Francis Ford Coppola'],
            'description': ['Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.', 'The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.']
        })
        expected_frame = pd.DataFrame({
            'title': ['The Shawshank Redemption', 'The Godfather'],
            'year': [1994, 1972],
            'decade': [1990, 1970],
            'combo_score': [9.3, 9.2],
            'combo_rk': [1, 2],
            'metacritic_score': [80, 100],
            'metacritic_rk': [1, 2],
            'imdb_score': [9, 9],
            'imdb_rk': [1, 2],
            'certificate': ['R', 'R'],
            'runtime_mins': [142, 175],
            'genre': ['Drama', 'Crime'],
            'director': ['Frank Darabont', 'Francis Ford Coppola'],
            'description': ['Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.', 'The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.']
        })
        self.assertEqual(self.imdb.clean_frame(frame), expected_frame)

    def test_create_col_gross_adj(self):
        frame = pd.DataFrame({
            'title': ['The Shawshank Redemption', 'The Godfather'],
            'year': ['1994', '1972'],
            'gross': ['1000000', '2000000']
        })
        expected_frame = pd.DataFrame({
            'title': ['The Shawshank Redemption', 'The Godfather'],
            'year': [1994, 1972],
            'gross': [1000000, 2000000],
            'gross_adj_2023': [1230000, 2460000],
            'gross_adj_2023_rk': [2, 1]
        })
        self.assertEqual(self.imdb.create_col_gross_adj(frame), expected_frame)

    def test_order_cols(self):
        frame = pd.DataFrame({
            'title': ['The Shawshank Redemption', 'The Godfather'],
            'year': [1994, 1972],
            'decade': [1990, 1970],
            'combo_score': [9.3, 9.2],
            'combo_rk': [1, 2],
            'metacritic_score': [80, 100],
            'metacritic_rk': [1, 2],
            'imdb_score': [9, 9],
            'imdb_rk': [1, 2],
            'certificate': ['R', 'R'],
            'runtime_mins': [142, 175],
            'genre1': ['Drama', 'Crime'],
            'director': ['Frank Darabont', 'Francis Ford Coppola'],
            'description': ['Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.', 'The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.']
        })
        expected_frame = pd.DataFrame({
            'title': ['The Shawshank Redemption', 'The Godfather'],
            'year': [1994, 1972],
            'decade': [1990, 1970],
            'combo_score': [9.3, 9.2],
            'combo_rk': [1, 2],
            'metacritic_score': [80, 100],
            'metacritic_rk': [1, 2],
            'imdb_score': [9, 9],
            'imdb_rk': [1, 2],
            'certificate': ['R', 'R'],
            'runtime_mins': [142, 175],
            'genre1': ['Drama', 'Crime'],
            'director': ['Frank Darabont', 'Francis Ford Coppola'],
            'description': ['Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.', 'The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.']
        })
        self.assertEqual(self.imdb.order_cols(frame), expected_frame)

if __name__ == '__main__':
    unittest.main()