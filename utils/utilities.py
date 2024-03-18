import pandas as pd
from numpy import nan
from datetime import datetime as dt
from itertools import chain
from re import sub
from typing import Union


def adjust_for_inflation(dollars: Union[float, int], cpi_start_year: Union[str, int, float], cpi_target_year: Union[str, int, float]) -> float:
    '''present_value = (dollars * cpi_target_year) / cpi_start_year'''

    cpi = pd.read_csv('data/input/inflation_cpi_history.csv', dtype={'Year': int, 'CPI': float})

    if isinstance(cpi_start_year, float):
        cpi_start_year = int(cpi_start_year)
    
    if isinstance(cpi_target_year, float):
        cpi_target_year = int(cpi_target_year)

    if isinstance(cpi_start_year, str):
        if cpi_start_year.isdigit():
            cpi_start_year = int(cpi_start_year)
        else:
            raise ValueError(f'cpi_start_year {cpi_start_year} must be an integer or a string of an integer.')
    if isinstance(cpi_target_year, str):
        if cpi_target_year.isdigit():
            cpi_target_year = int(cpi_target_year)
        else:
            raise ValueError(f'cpi_target_year {cpi_target_year} must be an integer or a string of an integer.')
    
    ## temporarily cap max year at 2023 b/c it is the last year in the cpi data atm.
    if cpi_target_year > cpi['Year'].max():
        cpi_target_year = cpi['Year'].max() 
    if cpi_start_year > cpi['Year'].max():
        cpi_start_year = cpi['Year'].max()

    ## temporarily cap min year at 1921 b/c it is the first year in the cpi data atm.
    if cpi_target_year < cpi['Year'].min():
        cpi_target_year = cpi['Year'].min() 
    if cpi_start_year < cpi['Year'].min():
        cpi_start_year = cpi['Year'].min()
        
    cpi = cpi.set_index('Year')
    present_value = (dollars * cpi.loc[cpi_target_year]).div(cpi.loc[cpi_start_year]).round(2).item()
    return present_value


def get_now() -> str:
    '''Returns the current date and time. Used in logging.'''
    return dt.now().strftime('%Y-%m-%d - %H:%M:%S')


def get_unique_items_from_many_cols(frame: pd.DataFrame, cols: str) -> set:
    '''Get the unique items from many cols.
    cols : str
        Regular expression to match the columns. 'col1|col2|col3'
        Ex: 'genre1|genre2|genre3' will return the unique count of all unique values in those columns.
    '''
    res = set(chain.from_iterable([frame[_].unique() for _ in frame.filter(regex=cols)]))
    res.discard(nan)
    return res


def get_unique_count_from_many_cols(frame: pd.DataFrame, cols: str) -> int:
    '''Get the unique count from many cols.
    cols : str
        Regular expression to match the columns. 'col1|col2|col3'
        Ex: 'genre|director|actor' will return the unique count of all unique values in those columns.
    '''
    # return len(set(chain.from_iterable([frame[_].unique() for _ in frame.filter(regex=cols)])))
    res = get_unique_items_from_many_cols(frame, cols)
    res.discard(nan)
    return len(res)


def dummy_all_genres(frame: pd.DataFrame) -> pd.DataFrame:
    dct = {}
    dummies = pd.get_dummies(frame.filter(regex='genre1|genre2|genre3'))

    for col in get_unique_items_from_many_cols(frame, 'genre1|genre2|genre3'):
        dct.update({col: dummies.filter(like=col).any(axis=1)})
    
    assert frame.shape[0] == dummies.shape[0], 'The shape of the frame and dummies must be the same.'
    return pd.concat([frame, dummies.rename(lambda col: f"genre_{col}", axis=1)], axis=1)


def dummy_all_stars(frame: pd.DataFrame) -> pd.DataFrame:
    dct = {}
    dummies = pd.get_dummies(frame.filter(regex='star1|star2|star3|star4'))

    for col in get_unique_items_from_many_cols(frame, 'star1|star2|star3|star4'):
        dct.update({col: dummies.filter(like=col).any(axis=1)})
    
    assert frame.shape[0] == dummies.shape[0], 'The shape of the frame and dummies must be the same.'
    return pd.concat([frame, dummies.rename(lambda col: f"star_{col}", axis=1)], axis=1)


def clean_film_name(film: str) -> str:
    '''removes punctuation and converts to lowercase for easier comparison.
    Output: str
        'the godfather pt.2' -> 'thegodfather2'
        This func's output is used for comparison, not display. 
        It will still be 'The Godfather Pt. 2' in the DataFrame and UI.
    '''
    ## consider removing numbers for comparison too? Avoids '2' vs 'two' vs 'II' issues.
    ## but then also results in Godfather == Godfather2 == Godfather3 b/c the numbers are removed.
    film = film.strip().lower()
    film = sub(r'(\&a?m?p?;?)', 'and', film)   # replace '&' or '&amp;' with 'and'
    film = sub(r'\'n\s', 'and', film) # replace 'n with "and"
    film = sub(r'\s?((T|t)he)\s', '', film) # remove 'the' from the title
    film = sub(r'(p?a?rt)', '', film) # remove 'part' or 'pt' from the title
    film = sub(r'[\'\,\-\:\.\!\"\?\·]+', '', film) # remove punctuation
    film = sub(r'(\s| )+', '', film) # finally, remove spaces
    return film