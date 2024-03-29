import streamlit as st
import pandas as pd
from plotly import graph_objects as go
import plotly.express as px
from utils.streamlit_utilities import gradient, local_css, init_to_null, plot_xy_radio_buttons, set_frame
from utils.palettes import blue_bath1, fft_knight_male

# import pickle




class PageBoxOffice():
    """Layout class for Box Office page.
    """
    
    def __init__(self):
        st.set_page_config(page_title="IMDb Lists", layout="wide", page_icon='🎥', initial_sidebar_state="expanded")
        # local_css("style/style.css")
        self.initialize_state()
        # st.cache_data.clear() ## change to use button to clear cache....?  Punt for now.
        self.df = set_frame(load_demo=True)
        self.page_header()
        self.show_page()





    def show_page(self):

        if self.df['gross'].sum() == 0:
            st.markdown(f"#### <font color={fft_knight_male[5]}>WARNING:</font> No film 'gross' data available.", unsafe_allow_html=True)  
            st.markdown("Please check out other pages that aren't dealing with gross revenue.")
            return
        
        self.intro_text()
        st.markdown('***')
        self.data_insights_text()
        st.markdown('***')
        self.table_top_grossing_films(self.df)
        st.markdown('***')
        self.table_average_scores_top_bottom_grossing_films(self.df)
        self.remarks_top_and_bottom_grossing_films()
        self.plot_gross_by_rating_plotly(self.df)
        st.markdown('***')        
        self.plot_gross_over_time_plotly(self.df)
        self.remarks_gross_over_time()
        st.markdown('***')
        self.table_grid_top_genres_over_time(self.df)
        self.remarks_top_genres_over_time()
        st.markdown('***')
        self.plot_gross_by_genre_plotly(self.df)
        self.remarks_gross_by_genre()
        st.markdown('***')
        self.plot_gross_by_director_plotly(self.df)
        self.remarks_gross_by_director()
        st.markdown('***')

    def initialize_state(self):
        state = st.session_state
        init_to_null(state, 'show_more_info', False)
        init_to_null(state, 'df', None)
        init_to_null(state, 'df_cache', None)

    def element_header(self, text: str, header_tag: str='h4', color: str=blue_bath1[1]):
        return st.markdown(f"<{header_tag} align=center><font color={color}>{text}</font></{header_tag}>", unsafe_allow_html=True)

    def page_header(self):
        gradient(grad_clr1=blue_bath1[1], grad_clr2=blue_bath1[3], title_clr=blue_bath1[5], subtitle_clr='#fcfbfb', title=f"💰 Box Office", subtitle="Break down films by their box office returns", subtitle_size=27)
        st.markdown("<br><br>", unsafe_allow_html=True)

    def intro_text(self):
        self.element_header("Introduction")
        st.markdown("""Understanding how a film performed at the box office isn't always as simple as merely looking at ticket sales. The biggest factor in making comparisons across times is inflation.  A film that made \$100 million in 1980 is not the same as a film that made \$100 million in 2020.  This is why we adjust for inflation.  We can also look at how films performed by decade, genre, director, and rating.  This page will help you understand how to analyze box office returns and how to compare films across different time periods.  We will also look at the top grossing films by decade and how they compare to each other.""") 

        if not st.session_state.show_more_info:
            st.button('Show More', key='show_more_button', on_click=lambda: st.session_state.update(show_more_info=True))
        
        def show_more_info():
            # st.markdown(f"<h5><font color={blue_bath1[1]}>Home Video and Streaming</font></h5>", unsafe_allow_html=True)
            self.element_header("Home Video and Streaming")
            st.markdown("""Another factor is that the advent of home video (see: a thing called [VHS](https://en.wikipedia.org/wiki/VHS), kiddies. You even had to rewind the tapes! 😱) in the 1980s meant that the theater wasn't the only place to see a film.  As that progressed into DVDs it meant that box office sales weren't possible to make perfect one-to-one comparisons with.  Someone could pay $25 for a DVD and watch the film repeatedly, but that wouldn't be captured in the box office data, of course.""")  
            
            st.markdown("""Some films became cult classics which gained popularity primarily in the home video market after a tepid theatrical run.  Those films are now beloved and have been seen countless times, but their luke warm box office success belies such popularity. Home video data isn't readily available and means this page is focused strictly on the revenue generated on the big screen.  How are we to compare the box office success of a film like "The Big Lebowski" to "The Avengers"?""")  
            
            st.markdown("""In modern day, we have streaming services like Netflix, Hulu, HBO Max, and Amazon Prime, which have made it even more difficult to compare box office success across time. A film like "The Irishman" was released in theaters for a short time before being available on Netflix.  How do we evaluate the box office success of a film like "The Irishman" to "The Godfather"?  Or Dune (2021, Villaneuve) to Dune (1984, Lynch)?  Or, for that matter, even Dune (2021) to itself, as it was released *simultaneously* in the theater and on streaming (largely as a holdover for COVID precautions)?  How many people didn't go to the theater for it, despite being made for IMAX, because they could just watch it at home immediately?""")

            # st.markdown(f"<h5><font color={blue_bath1[1]}>Theaters and Technology</font></h5>", unsafe_allow_html=True)
            self.element_header("Theaters and Technology")
            st.markdown("""Last, theater ticket prices have themselves changed a great deal over time, and the number of theaters has changed as well.  The number of films released each year has also changed.  There were periods of "price amplification" due to somewhat gimmicky '3D' glasses and projectors which cost much more than standard tickets.  And while IMAX theaters can provide phenomenal experiences for movies made for the technologically advanced screens, like Oppenheimer or Dune, these theaters weren't around for Gone with the Wind, Jaws, or the original Star Wars.  How different would their revenue be?  Maybe a lot?  Maybe not much?  All of these factors make it difficult to compare box office success across time.  That level of analysis is beyond the scope of this project.  The best we can do is adjust for inflation and look at the data in a variety of ways to try to understand the box office success of a film.""")

        if st.session_state.show_more_info:
            show_more_info()
            st.button('Show Less', key='show_less_button', on_click=lambda : st.session_state.update(show_more_info=False))

        st.markdown("""Okay, let's get started!""")  
        
        # st.write('<BR><BR>', unsafe_allow_html=True)

    def data_insights_text(self):
        self.element_header("Insights From Your List")
        st.markdown("""Here are some insights from your list of films.  This is a great place to start to understand the data you have.  You can see the top grossing films, the average gross by genre, and the average gross by director.  You can also see how the gross of films has changed over time.  This will help you understand the data you have and how to compare films across different time periods.""")

        st.markdown(f"""<font color={blue_bath1[1]}>Tables are sortable and charts are interactive.  Hover over the charts to see more information.  Click and drag to zoom in on the charts.  Click on the legend to hide or show data.</font>""", unsafe_allow_html=True)

    def table_top_grossing_films(self, df: pd.DataFrame=pd.DataFrame()):
        self.element_header("Top Grossing Films From Your List")
        
        n, sorter = plot_xy_radio_buttons(x_label='Select Number of Films', x_buttons=[5, 25, 'All'], xindex=0, y_label='Select Box Office Revenue', y_buttons=['gross', 'gross_adj_2023'], xkey='x_top_grossing_films_table_radio', ykey='y_top_grossing_table_radio', y_format=lambda label: 'raw gross' if label == 'gross' else 'inflation adj.', col_spacing=[.5, .25, .25], horizontal=True)

        @st.cache_data
        def transform_frame(df: pd.DataFrame, n: str, sorter: str):
            # Sort the dataframe by gross in descending order
            df = df.sort_values(sorter, ascending=False)

            # Get the top n grossing films of each decade
            if sorter == 'gross': 
                cols = ['title', 'year', 'gross_rk', 'gross', 'gross_adj_2023_rk', 'gross_adj_2023', 'combo_score', 'imdb_score', 'metacritic_score']  
            else: 
                cols = ['title', 'year', 'gross_adj_2023_rk', 'gross_adj_2023', 'gross_rk', 'gross', 'combo_score', 'imdb_score', 'metacritic_score']

            top_films = df[cols].head(int(n) if n != 'All' else df.shape[0])\
                .set_index('title')\
                .assign(gross=lambda f: f['gross'].div(1000000).map("${:,.1f} M".format),
                        gross_adj_2023=lambda f: f['gross_adj_2023'].div(1000000).map("${:,.1f} M".format), 
                        year=lambda f: f['year'].astype(int).map("{:d}".format))\
                .rename(columns={'gross_adj_2023_rk': 'inflation_adj_rk', 'gross_adj_2023': 'inflation_adj'})
            return top_films
        
        top_films = transform_frame(df, n, sorter)

        st.dataframe(top_films, use_container_width=False)

        st.markdown("Sorting by the 'inflation_adj_rk' column will show the top grossing films after adjusting for inflation.  This can be a more accurate way to compare the box office success of films across different time periods. The 'combo_score' column is a weighted average of the IMDb and Metacritic scores.")

    def table_average_scores_top_bottom_grossing_films(self, df: pd.DataFrame=pd.DataFrame()):
        """Average scores for the top and bottom grossing films."""
        
        self.element_header("Are Top Grossing Films Better Rated?")
        
        _, col2, _, col4 = st.columns([.15, .3, .1, .45])
        with col2:
            n = int(st.slider('Select Number of Films', 10, 100, 10, 10, help='Shows the N top films and N bottom films average gross and scores.', key='top_bottom_slider'))
        with col4:
            gross = st.radio('Select Box Office Revenue', ['gross', 'gross_adj_2023'], index=0, key='y_top_bottom_radio', format_func=lambda label: 'raw gross' if label == 'gross' else 'inflation adj.', horizontal=True)

        @st.cache_data
        def transform_frame(df: pd.DataFrame, n: int, gross: str):
            df = df[df['metacritic_score']>0].sort_values(gross, ascending=False) # Remove films with no metacritic score
            top_films = df.head(n)
            bottom_films = df.tail(n)

            top_metacritic_avg = top_films['metacritic_score'].mean()
            top_imdb_avg = top_films['imdb_score'].mean()
            top_imdb_votes_avg = top_films['imdb_votes'].mean()
            bottom_metacritic_avg = bottom_films['metacritic_score'].mean()
            bottom_imdb_avg = bottom_films['imdb_score'].mean()
            bottom_imdb_votes_avg = bottom_films['imdb_votes'].mean()
            top_gross_avg = top_films[gross].mean()
            bottom_gross_avg = bottom_films[gross].mean()

            avg_scores_df = pd.DataFrame({
                'Avg. Gross': [top_gross_avg, bottom_gross_avg],
                'Avg. Metacritic Score': [top_metacritic_avg, bottom_metacritic_avg],
                'Avg. IMDb Score': [top_imdb_avg, bottom_imdb_avg],
                'Avg. IMDb Votes': [top_imdb_votes_avg, bottom_imdb_votes_avg]}, 
                index=[f'Top Grossing {n} Films', f'Bottom Grossing {n} Films'])
            
            # Add a row for the difference between the first two rows
            diff_row = avg_scores_df.iloc[0] - avg_scores_df.iloc[1]
            avg_scores_df.loc[avg_scores_df.shape[0]] = diff_row
            avg_scores_df = avg_scores_df.rename(index={avg_scores_df.shape[0]-1: 'Difference'})
            return avg_scores_df
        
        avg_scores_df = transform_frame(df, n, gross).style.format({
                    'Avg. Gross': "${:,.0f}",
                    'Avg. Metacritic Score': "{:.1f}",
                    'Avg. IMDb Score': "{:.1f}",
                    'Avg. IMDb Votes': "{:,.0f}"
                })
        
        _, col2 = st.columns([.15, .85])
        with col2:
            st.dataframe(avg_scores_df, use_container_width=False)

    def remarks_top_and_bottom_grossing_films(self):
        """Remarks about the top and bottom grossing films."""

        st.markdown("<BR>", unsafe_allow_html=True)
        st.markdown("""Depending on your dataset, there may be some interesting insights to be had from the top- and bottom-grossing films.  For large enough lists of movies that have a wide spread between the top and bottom N grossing films, it's possible to see that the *very* bottom-grossing movies (bottom 10 or 30) are significantly lower rated than the equivalent top-grossing films.  But once there is a larger sample (~70+), it's possible to see that the bottom-grossing films are not significantly lower rated than the top-grossing films.  This is because the bottom-grossing films are likely to be more obscure and less well-known, and therefore less likely to be rated.  As such, the number of ratings for each film, and not just the average rating, can be informative.""")
        st.markdown("<BR><BR>", unsafe_allow_html=True)

    def plot_gross_by_rating_plotly(self, df: pd.DataFrame=pd.DataFrame()):
        # self.element_header(f"Gross by Rating Score")

        c1, c2, _, c4 = st.columns([.35, .25, .15, .25])
        with c1:
            x = st.radio('Select Rating System', ('metacritic_score', 'imdb_score', 'combo_score'), index=1,key='x_gross_by_rating_radio', format_func=lambda label: label.replace('_score', ''), horizontal=True)
        with c2:
            chosen_genre = st.selectbox('Select Genre', ['All'] + list(df['genre1'].unique()))
            st.markdown(f"<div align=center>{df[df['genre1']==chosen_genre].shape[0]} {chosen_genre} films</div>" if chosen_genre != 'All' else '', unsafe_allow_html=True)
        with c4:
            y = st.radio('Select Box Office Revenue', ['gross', 'gross_adj_2023'], key='y_gross_by_rating_radio', format_func=lambda label: 'raw gross' if label == 'gross' else 'inflation adj.', horizontal=True)

        @st.cache_data
        def transform_frame(df: pd.DataFrame, x: str):
            return df[df[x]>0].assign(score_decile=pd.cut(df[x], 10, labels=False, duplicates='drop')).sort_values(x, ascending=False)

        df_plot = transform_frame(df, x)
        genre_mask = (df_plot['genre1'] == chosen_genre) if chosen_genre != 'All' else (df_plot['genre1'] == df_plot['genre1'])
        colors = 5 * px.colors.qualitative.Pastel

        def plot_unchosen_genre(fig: go.Figure, df_plot: pd.DataFrame):
            for decile in df_plot['score_decile'].unique():
                data_grey = df_plot[(df_plot['score_decile'] == decile) & ~genre_mask]
                
                fig.add_trace(go.Scatter(
                    x=data_grey[x],
                    y=data_grey[y],
                    mode='markers',
                    name=f"{decile}0th pct.",
                    marker=dict(color='grey', size=9, opacity=.4, line=dict(color='black', width=1)),
                    hoverinfo='skip',
                    showlegend=False,
                ))

        def plot_chosen_genre(fig: go.Figure, df_plot: pd.DataFrame):
            for idx, decile in enumerate(df_plot['score_decile'].unique()):
                data_clr = df_plot[(df_plot['score_decile'] == decile) & genre_mask]

                fig.add_trace(go.Scatter(
                    x=data_clr[x],
                    y=data_clr[y],
                    mode='markers',
                    name=f"{decile}0th pct.",
                    marker=dict(color=colors[idx], size=12 if chosen_genre != 'All' else 11, opacity=1 if chosen_genre != 'All' else .8, line=dict(color='black', width=1)),
                    hovertemplate='<b>Title</b>: ' + data_clr['title'] + ' (' + data_clr['year'].astype(str) +') ' + '<br><b>Gross</b>: ' + data_clr[y].div(1000000).map("${:,.1f} M".format) + '<br><b>Rating</b>: ' + data_clr[x].map('{:.1f}'.format).astype(str) + '<extra></extra>',
                    showlegend=True,
                ))

        fig = go.Figure()
        plot_unchosen_genre(fig, df_plot) ## add grey first so that the colored points are on top
        plot_chosen_genre(fig, df_plot)

        # fig.update_xaxes(tick0=0, dtick=10)
        fig.update_layout(
            xaxis_title=x,
            yaxis_title='Gross',
            # xaxes=dict(tick0=0, dtick=10),
            width=1000,
            height=500
        )

        st.plotly_chart(fig)

        st.markdown("""Also, note that if a film has a Metacritic score of 0, it means that it has not been rated on Metacritic.  This is not the same as a film having a Metacritic score of 0.  The same goes for IMDb scores. As such, those films have been removed from the plot to avoid skewing the visualization.""")

    def plot_gross_over_time_plotly(self, df: pd.DataFrame=pd.DataFrame()):
        """Plot the gross over Time."""

        self.element_header(f"Film Gross over Time")
        
        c1, c2, _, c4 = st.columns([.35, .25, .15, .25])
        with c1:
            x = st.radio('Select Timeframe', ['year', 'decade'], index=1, key='x_gross_by_year_radio', format_func=lambda label: label.replace('_score', ''), horizontal=True)
        with c2:
            chosen_genre = st.selectbox('Select Genre', ['All'] + list(df['genre1'].unique()), key='genre_over_time_radio')
            st.markdown(f"<div align=center>{df[df['genre1']==chosen_genre].shape[0]} {chosen_genre} films</div>" if chosen_genre != 'All' else '', unsafe_allow_html=True)
        with c4:
            y = st.radio('Select Box Office Revenue', ['gross', 'gross_adj_2023'], key='y_gross_by_year_radio', format_func=lambda label: 'raw gross' if label == 'gross' else 'inflation adj.', horizontal=True)


        @st.cache_data  # Cache the function so it doesn't run every time the user changes the radio buttons
        def transform_frame(df):
            return df[df['decade']>0].sort_values('decade', ascending=False)
        df_plot = transform_frame(df)
        genre_mask = (df_plot['genre1'] == chosen_genre) if chosen_genre != 'All' else (df_plot['genre1'] == df_plot['genre1'])
        size = 11 if x == 'year' else 9

        ## TODO: There are some movies that have 'decade' == 0.  Need to manually add their correct data in 'specific_fixes' in the imdb_acquisition.py file.  Until then, must drop them here.

        colors = 5 * px.colors.qualitative.Pastel

        def plot_unchosen_genre(fig: go.Figure, df_plot: pd.DataFrame):
            for decade in df_plot['decade'].unique():
                data_grey = df_plot[(df_plot['decade'] == decade) & ~genre_mask]
                
                fig.add_trace(go.Scatter(
                    x=data_grey[x],
                    y=data_grey[y],
                    mode='markers',
                    name=f"{decade}0s.",
                    marker=dict(color='grey', size=9, opacity=.4, line=dict(color='black', width=1)),
                    hoverinfo='skip',
                    showlegend=False,
                ))

        def plot_chosen_genre(fig: go.Figure, df_plot: pd.DataFrame):
            for idx, decade in enumerate(df_plot['decade'].unique()):
                data_clr = df_plot[(df_plot['decade'] == decade) & genre_mask]

                fig.add_trace(go.Scatter(
                    x=data_clr[x],
                    y=data_clr[y],
                    mode='markers',
                    name=f"{decade}s",
                    marker=dict(color=colors[idx], size=12 if chosen_genre != 'All' else 11, opacity=1 if chosen_genre != 'All' else .8, line=dict(color='black', width=1)),
                    hovertemplate='<b>Title</b>: ' + data_clr['title'] + ' (' + data_clr['year'].astype(str) +') ' + '<br><b>Gross</b>: ' + data_clr[y].div(1000000).map("${:,.1f} M".format) + '<br><b>Rating</b>: ' + data_clr[x].map('{:.1f}'.format).astype(str) + '<extra></extra>',
                    showlegend=True,
                ))

        fig = go.Figure()
        plot_unchosen_genre(fig, df_plot) ## add grey first so that the colored points are on top
        plot_chosen_genre(fig, df_plot)

        fig.update_layout(width=1000,
                          height=500
                        # title={'font_color': blue_bath1[1], 'font_size': 23, # 'font_family': "Times New Roman", 'text': "Gross over Time", 'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'}
                        )
                            
        st.plotly_chart(fig)
        self.table_top_decades_by_gross_per_film(self.df, y=y)

    def remarks_gross_over_time(self):
        st.markdown("""The top grossing films by decade can be intereseting!  Depending on your dataset, there might be very distinct trends which differ from others.  One thing to keep in mind is the increase in both number of theaters and average ticket price as time goes on.  This means that the top grossing films of the 2010s might not be as impressive as the top grossing films of the 1970s, for example.  This is why we adjust for inflation.  It's also why we look at the average gross per film, and not just the total gross of the top films.  The average gross per film can give us a better idea of how profitale films were in a given decade.  Last, most people won't have many films from the 1930s, 1940s, or 1950s, so the data might not be as reliable for those decades.  In theory, it would be great to have at least, say, the top 50 films from each decade to make a comparison.""")

    def table_grid_top_genres_over_time(self, df: pd.DataFrame=pd.DataFrame()):
        self.element_header("Highest Grossing Genres Over Time")
        
        genre, gross = plot_xy_radio_buttons(x_label='Select Genre', x_buttons=('genre1', 'genre2'), x_format=lambda label: 'Primary' if label == 'genre1' else 'Secondary', xkey='x_top_gross_genre_radio', y_label='Select Box Office Revenue', y_buttons=['gross', 'gross_adj_2023'], ykey='y_top_gross_genre_radio', y_format=lambda label: 'raw gross' if label == 'gross' else 'inflation adj.', col_spacing=[.5, .25, .25], horizontal=True)

        @st.cache_data
        def transform_frame(df: pd.DataFrame, decade: int):
            tmp = df.groupby(['decade', genre])[gross].agg(['mean', 'count'])\
                    .sort_values(by=['decade', 'mean'], ascending=False)\
                    .groupby('decade').head()\
                    .assign(**{f"{decade}s": lambda f: f.groupby('decade')['mean'].rank(ascending=False, method='dense')})\
                    .assign(mean=lambda f: f['mean'].div(1000000).map("${:,.1f} M".format))\
                    .reset_index(level=1).loc[decade]\
            ## if there's only one genre per decade after grouping, even if there are multiple films in that decade 
            ## but all are the same genre (admittedly unlikely with > 10 films per decade, but still has to be accounted for)
            ## then pandas will return a series after we index via .loc[decade], not a dataframe, so we have to convert 
            ## it to a dataframe.  Ugly, but it works. (I'm sure there's a smoother way to do this.)
            if isinstance(tmp, pd.Series):
                tmp = tmp.to_frame().T
            return tmp.reset_index()\
                .rename(columns={'mean': 'Avg. Gross', 'count': 'Film Count', 'genre1': 'Primary', 'genre2': 'Secondary', 'index': 'decade'})\
                .set_index(f"{decade}s")
                
        frames = [transform_frame(df, decade).drop('decade', axis=1) for decade in sorted(df['decade'].unique())]

        # Print the tables in a grid, 3 per row, one table per decadde
        for idx in range(len(frames)):
            if idx % 3 == 0:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.dataframe(frames[idx], use_container_width=False)
                with col2:
                    if idx+1 < len(frames):
                        st.dataframe(frames[idx+1], use_container_width=False)
                with col3:
                    if idx+2 < len(frames):
                        st.dataframe(frames[idx+2], use_container_width=False)

    def remarks_top_genres_over_time(self):
        st.markdown('<BR>', unsafe_allow_html=True)
        st.markdown("""The top grossing genres can be revealing.  Depending on your dataset, there might be very distinct trends which differ from others.  Adjusting for inflation is likely a good choice for evaluating the top grossing genres.  Acknowledging that different genres (Drama, Action, Adenture...) tend to have many more films than others (Western, War, Musical...) is important and should be noted with your specific dataset. Assuming substantial samples of each decade and genre, it's most interesting to remark on the genres that are consistently top grossing across time (Action, Adventure, Animation), and, conversely, those that seem to have distinct eras (Film-Noir, Western, War, Sci-Fi...)""")
        st.markdown('<BR>', unsafe_allow_html=True)

    def plot_gross_by_genre_plotly(self, df: pd.DataFrame=pd.DataFrame(), x: str='genre1', y: str='gross'):
        """Plot the gross by genre."""

        self.element_header(f"Gross by Genre")
        def xlabel(label):
            if label == 'genre1': lab = 'primary genre'
            elif label == 'genre2': lab = 'secondary genre'
            elif label == 'genre3': lab = 'third genre'
            return lab

        x, y = plot_xy_radio_buttons(x_label='Select Genre', y_label='Select Box Office Revenue', x_buttons=['genre1', 'genre2', 'genre3'], y_buttons=['gross', 'gross_adj_2023'], xkey='x_gross_by_genre_radio', ykey='y_gross_by_genre_radio', x_format=xlabel, y_format=lambda label: 'raw gross' if label == 'gross' else 'inflation adj.', col_spacing=[.45, .3, .25], horizontal=True)
        
        @st.cache_data
        def transform_frame(df: pd.DataFrame, x: str, y: str, power: float=0.8, lower: int=12, upper: int=80):
            ## create a 'count_plot' column for the size of the bubble and bound it to a minimum of 12 and a maximum of 80
            avg_gross_by_genre = df.groupby(x)[y].agg(['mean', 'count'])\
                .reset_index()\
                .rename(columns={'mean': 'avg_gross'})\
                .assign(count_plot=lambda f: f['count'].pow(power).clip(upper=upper).clip(lower=lower)) 
            return avg_gross_by_genre.sort_values(x, ascending=True)
        
        df_plot = transform_frame(df, x, y, power=1 if x == 'genre3' else 0.8)
        colors = 3 * px.colors.qualitative.Pastel ## extend the color palette if there are more genres than default palette   

        fig = go.Figure()
        for idx, genre in enumerate(df_plot[x].unique()):
            data = df_plot[df_plot[x]==genre]
            
            fig.add_trace(go.Scatter(
                x=data[x], 
                y=data['avg_gross'], 
                mode='markers', 
                marker=dict(line=dict(color='black', width=0.5), color=colors[idx], size=data['count_plot']),
                hovertemplate='<b>Genre</b>: ' + data[x] + '<br><b>Gross</b>: ' + data['avg_gross'].div(1000000).map("${:,.1f} M".format)  + '<br><b>Count</b>: ' + data['count'].astype(str) + '<extra></extra>',
                showlegend=False)
                )
        
        fig.update_layout(width=1000)
        st.plotly_chart(fig)

    def remarks_gross_by_genre(self):
        st.markdown('<BR>', unsafe_allow_html=True)
        st.markdown("""This interactive chart is meant to give some idea of the relative categorical sizes of the genres in your list through bubble size, and, further helps show how adjusting for inflation can alter the average gross by genre.  This change can be quite substantial and shows how genre popularity has changed over time.""")

    def table_top_decades_by_gross_per_film(self, df: pd.DataFrame=pd.DataFrame(), y: str='gross'):
        # self.element_header("Top Decades by Gross per Film")
        
        @st.cache_data
        def transform_frame(df: pd.DataFrame):
            decade_stats = df.groupby('decade')[y].mean()
            decade_stats = decade_stats.div(1000000).map("${:,.0f} M".format)
            return decade_stats.to_frame().sort_index(axis=1).rename(columns={y: 'Avg. Gross per Film'})
        
        decade_stats = transform_frame(df).T.rename(columns=lambda col: f"{col}s")
        
        col1, _ = st.columns([.98, .02])
        with col1:
            st.dataframe(decade_stats, use_container_width=True)

    def plot_gross_by_director_plotly(self, df: pd.DataFrame=pd.DataFrame()):
        self.element_header(f"Gross by Director")

        def set_default_indices(df: pd.DataFrame):
            '''Set the default indices for the radio buttons b/c in small frames most options will display an empty chart.'''
            if df.shape[0] > 100:
                thresh_idx = 3 ## $100M
            elif df.shape[0] > 50:
                thresh_idx = 1 ## $20M
            else:
                thresh_idx = 0

            minfilms_idx = 1 if df.shape[0] > 50 else 0
            return thresh_idx, minfilms_idx

        thresh_idx, minfilms_idx = set_default_indices(df)

        def xlabel(label):
            if label == 'All':
                return 'All Directors'
            elif int(label) < 1000000000:
                lab = int(label) // 1000000
                denom = 'M'
            else:
                lab = int(label) // 1000000000
                denom = 'B'
            return f"${lab:,d} {denom}"
        
        col1, _, col2, col3 = st.columns([.35, .07, .33, .25])
        with col1:
            thresh = st.radio('Avg. Gross Threshold', ['All', '20000000', '50000000', '100000000', '300000000', '500000000', '1000000000'], index=thresh_idx, help='Minimum avg. gross per film by director', key='x_gross_by_director_radio', format_func=xlabel, horizontal=True)
        with col2:
            minfilms = st.radio("Min. Number of Films", [1, 2, 3], index=minfilms_idx, help='Minimum number of films by director. Helps weed out one-hit wonders', key='min_films_by_director_radio', horizontal=True)
        with col3:
            y = st.radio('Select Box Office Revenue', ['gross', 'gross_adj_2023'], key='y_gross_by_director_radio', format_func=lambda label: 'raw gross' if label == 'gross' else 'inflation adj.', horizontal=True)
        
        @st.cache_data
        def transform_frame(df: pd.DataFrame, x: str, y: str, thresh: int, power: float=0.8, lower: int=12, upper: int=80):
            ## create a 'count_plot' column for the size of the bubble and bound it to a minimum of 12 and a maximum of 80
            avg_gross_by_director = df.groupby(x)[y].agg(['mean', 'count'])\
                .reset_index()\
                .rename(columns={'mean': 'avg_gross'})\
                .query(f"avg_gross >= @thresh")\
                .assign(count_plot=lambda f: f['count'].pow(power).clip(upper=upper).clip(lower=lower)) 
            return avg_gross_by_director.sort_values('avg_gross', ascending=True)

        df_plot = transform_frame(df, 'director', y, int(thresh) if thresh != 'All' else 0)
        colors = 50 * px.colors.qualitative.Pastel ## extend the color palette

        fig = go.Figure()
        for idx, genre in enumerate(df_plot['director'].unique()):
            data = df_plot[(df_plot['director']==genre) & (df_plot['count'] >= int(minfilms))]
            # data = df_plot[df_plot['director']==genre]
            
            fig.add_trace(go.Scatter(
                x=data['director'], 
                y=data['avg_gross'], 
                mode='markers', 
                marker=dict(line=dict(color='black', width=0.5), color=colors[idx], size=data['count_plot']),
                hovertemplate='<b>Genre</b>: ' + data['director'] + '<br><b>Gross</b>: ' + data['avg_gross'].div(1000000).map("${:,.1f} M".format)  + '<br><b>Films</b>: ' + data['count'].astype(str) + '<extra></extra>',
                showlegend=False)
                )

        fig.update_layout(width=1000)
        st.plotly_chart(fig)

    def remarks_gross_by_director(self):
        st.markdown('<BR>', unsafe_allow_html=True)
        st.markdown("""The key takeaway from this chart (depending on your dataset) is that the number of directors with *ONE* big hit are more numerous than you might expect, but to have multiple is really challenging.  Setting the limit of number of films to 2 or 3 can help weed out the one-hit wonders.  Some, like Peter Jackson or (slightly less so) George Lucas, had one franchise they rode to massive success. Others, like Christopher Nolan or Steven Spielberg, have had multiple films that have been very successful.  Again, adjusting for inflation probably offers the fairest comparison.  Though not implemented here, it might also be worth adding a feature that allows the user to compare only the top N grossing films of a director's catalog, as opposed to all of them.""")
        st.markdown('<BR>', unsafe_allow_html=True)




if __name__ == "__main__":
    PageBoxOffice()

    