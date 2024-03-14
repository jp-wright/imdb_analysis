# st.write('WFF https://www.imdb.com/list/ls528069836/')
# st.write('big list https://www.imdb.com/list/ls040479474/?st_dt=&mode=detail&page=1&sort=list_order,asc')



def DEMO_cool_state_persistence_code(self):
    state = st.session_state

    if "dict_options" not in state:
        state.dict_options = {}

    if "submitted" not in state:
        state.submitted = False

    options = ["option1", "option2", "option3", "option4"]

    col1, col2, _ = st.columns(3)

    with col1.form("my_form"):
        new_country = st.text_input("New country")
        submit_button = st.form_submit_button(
            label="Add new country", on_click=lambda: state.update(submitted=True)
        )

    if state.submitted:
        state.dict_options[new_country] = col2.multiselect(
            f"Select the options you want for {new_country}",
            options,
            default=options[:2],
        )
        col2.write(state.dict_options)

        


def plot_gross_by_genre_plotly_DUMMY_GENRES(self, df: pd.DataFrame=pd.DataFrame(), x: str='genre1', y: str='gross'):
    """Plot the gross by genre."""

    self.element_header(f"Gross by Genre")

    x, y = plot_xy_radio_buttons(x_label='Select Genre', y_label='Select Raw Value or Adj. for Inflation', x_buttons=['genre1', 'all genres'], y_buttons=['avg_gross', 'gross_adj_2023'], xkey='x_gross_by_genre_radio', ykey='y_gross_by_genre_radio', x_format=lambda label: 'primary genre' if label == 'genre1' else 'all applicable genres',y_format=lambda label: 'raw gross' if label == 'avg_gross' else 'inflation adj.', xhelp='primary genre for each film OR up to the three most applicable genres for each film will count it in a given genre', horizontal=True)

    @st.cache_data
    def transform_frame():
        avg_gross_by_genre = df.groupby(x)['gross'].agg(['mean', 'count']).reset_index().rename(columns={'mean': 'avg_gross'}).assign(count_plot=lambda f: f['count'].pow(.8).clip(upper=80).clip(lower=12)) ## create a column for the size of the bubble and bound it to a minimum of 12 and a maximum of 80
        return avg_gross_by_genre.sort_values('avg_gross', ascending=False)
    
    df = transform_frame()
    st.write(df.head())

    # fig = px.scatter(avg_gross_by_genre, x=x, y='mean', size='count', color=x, title=f'Average Gross by {x}', hover_data=[x, 'count'], color_discrete_sequence=px.colors.qualitative.Pastel)

    def get_genres():
        """Get the unique genres from the dataframe and keep resuling sort based on selected Y col."""
        genres = get_unique_items_from_many_cols(df, 'genre1|genre2|genre3')
        genres = sorted(genres, key=lambda genre: df[df[x]==genre][y].mean(), reverse=True)
        return genres
    genres = get_genres()
    

    colors = 3*px.colors.qualitative.Pastel if len(genres) > len(px.colors.qualitative.Pastel) else px.colors.qualitative.Pastel
        
    # size = 7 if x == 'year' else 9
    
    fig = go.Figure()

    for idx, genre in enumerate(genres):
        # data = df[(df['genre1']==genre) | (df['genre2']==genre)]
        data = df[df[f"genre_{genre}"]==genre]
        
        fig.add_trace(go.Scatter(
            x=data[x], 
            y=data[y], 
            mode='markers', 
            marker=dict(line=dict(color='black', width=0.5), color=colors[idx], size=data['count_plot']),
            hovertemplate='<b>Genre</b>: ' + data[x] + '<br><b>Gross</b>: ' + data[y].div(1000000).map("${:,.1f} M".format)  + '<br><b>Count</b>: ' + data['count'].astype(str) + '<extra></extra>',
            showlegend=False)
            )
    
    fig.update_layout(width=1000)
    st.plotly_chart(fig)
