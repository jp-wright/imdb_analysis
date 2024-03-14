



'''analyze the movie data in the data/output/metacritic_and_imdb_top_films.csv to learn the fields in the csv file and the create tables using Pandas showing the average gross per film, the average "combo" rating per genre and per decade and per director, and which actors have the most appearances and highest grosses and highest combo rating'''

import pandas as pd


def show_top_n_films(frame: pd.DataFrame, col: str, n: int=10) -> pd.DataFrame:
    '''Show top n films by column'''
    return frame.nlargest(n, col)

def show_bottom_n_films(frame: pd.DataFrame, col: str, n: int=10) -> pd.DataFrame:
    '''Show bottom n films by column'''
    return frame.nsmallest(n, col)

def show_avg_gross_per_genre(frame: pd.DataFrame) -> pd.DataFrame:
    '''Show average gross per film'''
    return frame['gross'].mean()

def show_avg_combo_rating_per_primary_genre(frame: pd.DataFrame) -> pd.Series:
    '''Show average combo rating per genre'''
    return frame.groupby('genre1')['combo'].mean().sort_values(ascending=False).round(1)

def show_avg_combo_rating_per_decade(frame: pd.DataFrame) -> pd.Series:
    '''Show average combo rating per decade'''
    return frame.groupby(frame['year'].astype(str).str[:3] + '0s')['combo'].mean().sort_values(ascending=False).round(1)

def show_avg_combo_rating_per_director(frame: pd.DataFrame) -> pd.Series:
    '''Show average combo rating per director'''
    return frame.groupby('director')['combo'].mean().sort_values(ascending=False).round(1)

def show_most_common_actors(frame: pd.DataFrame, n: int=10) -> pd.Series:
    '''Show most common actors and number of appearances'''
    return frame.filter(like='star').melt().drop('variable', axis=1).value_counts().head(n)

def show_highest_grossing_actors(frame: pd.DataFrame, n: int=10) -> pd.Series:
    '''Show highest grossing actors'''
    return frame.filter(like='star').melt().value_counts().head(n)

def show_highest_combo_rating_actors(frame: pd.DataFrame, n: int=10) -> pd.Series:
    '''Show highest combo rating actors'''
    return frame.filter(like='star').melt().drop('variable', axis=1).value_counts().head(n)



## make list: frame.filter(like='star').apply(lambda row: '_'.join(row.values.astype(str)), axis=1).str.split('_')