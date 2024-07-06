import streamlit as st
import sklearn
from sklearn.neighbors import NearestNeighbors
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
    movie_idx = movies_list[movies_list['title'] == movie].index[0]
    movie_vector = vectors[movie_idx].reshape(1, -1)  # Ensure the input is a 2D array
    
    distances, indices = knn.kneighbors(movie_vector)
    
    # Exclude the first result which is the movie itself
    movie_indices = indices[0][1:]

    recommended = []
    recommended_movie_poster = []

    for i in movie_indices:
        movie_id = movies_list.iloc[i]['id']
        recommended.append(movies_list.iloc[i].title)
        
        # Fetch poster     
        poster_url = fetch_movie_poster(movie_id)
        recommended_movie_poster.append(poster_url)
    
    return recommended, recommended_movie_poster

# Load the movie list and similarity matrix
movies_list = pickle.load(open('dependencies/movies.pkl', 'rb'))
movies_list = pd.DataFrame(movies_list)

vectors = pickle.load(open('dependencies/vectors.pkl', 'rb'))

# Load the knn object
knn = pickle.load(open('dependencies/knn.pkl', 'rb'))

# Streamlit app
st.set_page_config(page_title="Movie Recommender System", layout="wide", initial_sidebar_state="expanded")
st.title('🎬 Movie Recommender System')
st.markdown("""
    Welcome to the Movie Recommender System! 🎥🍿
    Select a movie from the dropdown below, and top 5 similar movies are recommended for you to enjoy.
""")

st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(135deg, #003366, #000000);  /* Dark Blue to Black Gradient */
        color: #ffffff;  /* White text color for contrast */
    }
    .sidebar .sidebar-content {
        background: #1a1a1a;  /* Dark Gray background for sidebar */
        color: #ffffff;  /* White text color for sidebar */
    }
    </style>
    """,
    unsafe_allow_html=True
)

selected_movie_name = st.selectbox(
    'Select a movie:',
    movies_list['title'].values,
    index=0  # Set default selected movie
)

if st.button("Get Recommendations"):
    with st.spinner('Fetching movie recommendations...'):
        names, posters = recommend(selected_movie_name)
    
    # Display recommendations
    st.subheader(f"Top 5 recommendations based on '{selected_movie_name}':")

    cols = st.columns(5, gap="large")
    for i in range(5):
        with cols[i]:
            st.image(posters[i], width=150)
            st.write(f"**{names[i]}**")
