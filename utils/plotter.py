import pandas as pd
import plotly.express as px


# # Read the CSV file
# df = pd.read_csv('data/output/metacritic_and_imdb_top_films.csv')


# Create a scatter plot of ratings vs. box office gross
def ratings_vs_gross(df: pd.DataFrame) -> None:
    '''Create a scatter plot of ratings vs. box office gross'''
    fig = px.scatter(df, x='Rating', y='BoxOffice', hover_data=['Title'], title='Ratings vs. Box Office Gross')
    fig.show()


# Create a bar chart of genres and their average ratings
def genre_ratings(df: pd.DataFrame) -> None:
    '''Create a bar chart of genres and their average ratings'''
    genre_ratings = df.groupby('Genre')['Rating'].mean().reset_index()
    fig = px.bar(genre_ratings, x='Genre', y='Rating', title='Average Ratings by Genre')
    fig.show()


# Create a pie chart of the distribution of ratings
def rating_distribution(df: pd.DataFrame) -> None:
    '''Create a pie chart of the distribution of ratings'''
    rating_counts = df['Rating'].value_counts().reset_index()
    rating_counts.columns = ['Rating', 'Count']
    fig = px.pie(rating_counts, values='Count', names='Rating', title='Rating Distribution')
    fig.show()
