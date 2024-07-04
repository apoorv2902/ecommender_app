import streamlit as st
import pickle
import pandas as pd
import requests
import time

# Function to fetch movie poster URL
def fetch_movie_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5YTQ4NGQ1NTJjNjJhNTljNTAwZGRhZDE4ZTc0M2Y4MyIsIm5iZiI6MTcyMDAyMzc4MC42NTAzNTYsInN1YiI6IjY2ODU3OGZlOWRmY2ExZjJhNjFhNDU3NiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.8iGCaMkfCJuX_Y8RGsHzd7_xMJ_VgSVgOvzZCvy6RFs"
    }
    retries = 3  # Number of retries
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Check for HTTP errors
            data = response.json()
            return f'https://image.tmdb.org/t/p/w500/{data["poster_path"]}'
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                time.sleep(2)  # Wait before retrying
                continue
            st.error(f"Error fetching poster for movie ID {movie_id}: {e}")
            return 'https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg'


# Function to recommend top 5 movies based on similarity
def recommend(movie):
    """
    Function to return top 5 recommended movies
    """
    movie_index = movies_list[movies_list['title'] == movie].index[0]
    distances = similarity[movie_index]
    recon_movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended = []
    recommended_movie_poster = []

    for i in recon_movies_list:
        movie_id = movies_list.iloc[i[0]]['id']
        recommended.append(movies_list.iloc[i[0]].title)
        
        # Fetch poster     
        poster_url = fetch_movie_poster(movie_id)
        recommended_movie_poster.append(poster_url)
    
    return recommended, recommended_movie_poster

# Load the movie list and similarity matrix
movies_list = pickle.load(open('dependencies/movies.pkl', 'rb'))
movies_list = pd.DataFrame(movies_list)

similarity = pickle.load(open('dependencies/similarity.pkl', 'rb'))

# Streamlit app
st.title('Movie Recommender System')

selected_movie_name = st.selectbox(
    'Select a movie:',
    movies_list['title'].values
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)
    # Create columns for the images
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.subheader(names[i])
            st.image(posters[i])
