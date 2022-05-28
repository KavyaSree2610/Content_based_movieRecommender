#importing the required libraries
import streamlit as st
import pandas as pd
import pickle
import json
import requests
from PIL import Image

#Loading the data files
movies = pickle.load(open('movies_dict.pkl','rb'))
similarity = pickle.load(open('similarity_by_movie.pkl','rb'))
cosine_sim= pickle.load(open('similarity_by_genre.pkl','rb'))
movie_list = pd.DataFrame(movies)


#setting page title
img=Image.open('Images/page_icon.jpg')
st.set_page_config(page_title="Movie Recommender", page_icon=img, layout="wide")
st.markdown('''<h1 style='text-align: center; color: #d73b5c;'>Movie Recommender</h1>''',
                unsafe_allow_html=True)
#To hide the footer in streamlit
hide_menu_style ="""
                    <style>
                    footer {visibility :hidden;}
                    </style>"""
st.markdown(hide_menu_style,unsafe_allow_html=True)



#Fetching movie poster from rapidapi
def fetch_poster(movie):
    url = "https://online-movie-database.p.rapidapi.com/auto-complete"
    querystring = {"q": movie}
    headers = {
        "X-RapidAPI-Host": "online-movie-database.p.rapidapi.com",
        "X-RapidAPI-Key": "390fda9ce9msh43220b144a74b85p1ae7f7jsn5d145c610b9d"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.text



#Recommending movies based on similarity matrix
def recommend(movie,df):
    index = movie_list[movie_list['title'] == movie].index[0]
    distances = sorted(list(enumerate(df[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:
        # fetch the movie poster,names of top 5 movies  and appending them in a list
        recommended_movie_posters.append(fetch_poster(movie_list.iloc[i[0]].title))
        recommended_movie_names.append(movie_list.iloc[i[0]].title)

    return recommended_movie_names,recommended_movie_posters


#Function to find the the top rated movies according to imdb
mean_vote = movie_list['vote_average'].mean()
min_votes = movie_list['vote_count'].quantile(0.9)

def weighted_rating(x, m=min_votes, C=mean_vote):
    v = x['vote_count']
    R = x['vote_average']
    return (v/(v+m) * R) + (m/(m+v) * C)

#Function to show the movie names and posters on the web page
def show(recommended_movie_names, recommended_movie_posters):
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.write(recommended_movie_names[0])
        st.text("")
        h = json.loads(recommended_movie_posters[0])
        st.image((((h)["d"][0])["i"])["imageUrl"])

    with col2:
        st.text(recommended_movie_names[1])
        st.text("")
        h = json.loads(recommended_movie_posters[1])
        st.image((((h)["d"][0])["i"])["imageUrl"])

    with col3:
        st.write(recommended_movie_names[2])
        st.text("")
        h = json.loads(recommended_movie_posters[2])
        st.image((((h)["d"][0])["i"])["imageUrl"])
    with col4:
        st.write(recommended_movie_names[3])
        st.text("")
        h = json.loads(recommended_movie_posters[3])
        st.image((((h)["d"][0])["i"])["imageUrl"])
    with col5:
        st.write(recommended_movie_names[4])
        st.text("")
        h = json.loads(recommended_movie_posters[4])
        st.image((((h)["d"][0])["i"])["imageUrl"])

with st.sidebar:
    option = st.selectbox(
        'How would you like to recommend :',
        ("--Select--",
         "Movie name",
        "Movie Genre",
        # "Director",
        "Popular",
        "Top 5")
    )
# st.markdown(f"# Currently Selected {option}")


#Shows recommendations based on movie overview,crew,cast,genre,keywords
if option =="Movie name":
    selected_movie = st.selectbox(
        "Type or select a movie from the dropdown",
        movie_list['title'].values
    )
    if st.button('Show Recommendation'):
        recommended_movie_names,recommended_movie_posters = recommend(selected_movie,similarity)
        show(recommended_movie_names,recommended_movie_posters)



#Shows recommendations based on movie genre
if option == "Movie Genre":
    selected_movie = st.selectbox(
        "Type or select a movie from the dropdown",
        movie_list['title'].values
    )
    if st.button('Show Recommendation'):
        recommended_movie_names,recommended_movie_posters = recommend(selected_movie,cosine_sim)
        show(recommended_movie_names, recommended_movie_posters)


#Shows recommendations based on popularity
if option == "Popular":
    popular_movies = movie_list.sort_values('popularity', ascending=False)
    recommended_movie_names = []
    recommended_movie_posters=[]
    recommended_movie_names=(popular_movies['title'].head(10).values)
    for i in recommended_movie_names[0:5]:
        recommended_movie_posters.append(fetch_poster(i))
    show(recommended_movie_names, recommended_movie_posters)


#Shows recommendations based on ratings in the imdb
if option == "Top 5":
    top_movies = movie_list.copy().loc[movie_list['vote_count'] >= min_votes]
    top_movies['score'] = top_movies.apply(weighted_rating, axis=1)
    top_movies = top_movies.sort_values('score', ascending=False)
    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_names = (top_movies['title'].head(10).values)
    for i in recommended_movie_names[0:5]:
        recommended_movie_posters.append(fetch_poster(i))
    show(recommended_movie_names, recommended_movie_posters)