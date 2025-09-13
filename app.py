import streamlit as st
import pickle
import pandas as pd
import requests # To make API calls
from thefuzz import process

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CUSTOM STYLING ---
st.markdown("""
<style>
    /* Main background color */
    .stApp {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    /* Title style */
    h1 {
        color: #e63946; /* A vibrant red */
    }
    /* Selectbox styling */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #333333;
        color: #ffffff;
    }
    /* Button styling */
    .stButton > button {
        background-color: #e63946;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
    }
    .stButton > button:hover {
        background-color: #f1faee;
        color: #1d3557;
    }
    /* Recommendation card styling */
    .movie-card {
        background-color: #2b2b2b;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        margin-bottom: 20px;
    }
    .movie-title {
        font-size: 16px;
        font-weight: bold;
        color: #f1faee;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)


# --- DATA LOADING AND FUNCTIONS ---

API_KEY = "876da4e3af6fba7088031847fc5090d8" # IMPORTANT: Replace with your TMDb API key

@st.cache_data
def load_data():
    """Loads the movie data and similarity matrix from pickle files."""
    movies_df = pd.DataFrame(pickle.load(open('movies.pkl', 'rb')))
    similarity_matrix = pickle.load(open('similarity.pkl', 'rb'))
    return movies_df, similarity_matrix

def fetch_poster(movie_id):
    """Fetches the movie poster URL from the TMDb API."""
    try:
        response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US")
        response.raise_for_status() # Raise an exception for bad status codes
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching poster: {e}")
    return "https://placehold.co/500x750/2b2b2b/f1faee?text=No+Poster" # Fallback image

def recommend(movie_title, n=5):
    """
    Recommends movies based on fuzzy matching.
    Returns a list of recommended movie titles and their posters.
    """
    all_titles = new_df['title'].tolist()
    best_match = process.extractOne(movie_title, all_titles)
    
    if best_match[1] < 75: # Confidence threshold
        return None, None, f"Sorry, couldn't find a close match for '{movie_title}'."

    matched_title = best_match[0]
    movie_index = new_df[new_df['title'] == matched_title].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:n+1]
    
    recommended_movies = []
    recommended_posters = []
    for i in movies_list:
        movie_id = new_df.iloc[i[0]].movie_id
        recommended_movies.append(new_df.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))
        
    return matched_title, recommended_movies, recommended_posters

# Load the data
new_df, similarity = load_data()


# --- STREAMLIT USER INTERFACE ---

st.title('Movie Recommender System')
st.markdown("### Find your next favorite movie!")

# Create a select box for the user to choose a movie
selected_movie_name = st.selectbox(
    'Type or select a movie you like from the dropdown:',
    new_df['title'].values,
    index=None, # No default selection
    placeholder="Choose a movie..."
)

# Add a "Recommend" button
if st.button('Get Recommendations'):
    if selected_movie_name:
        with st.spinner('Finding recommendations for you...'):
            found_title, rec_movies, rec_posters = recommend(selected_movie_name, n=5)
        
        if rec_movies:
            st.subheader(f"Because you watched '{found_title}', you might like:")
            
            # Create 5 columns for the 5 recommendations
            cols = st.columns(5)
            for i in range(5):
                with cols[i]:
                    st.markdown(f"""
                    <div class="movie-card">
                        <img src="{rec_posters[i]}" style="width:100%; border-radius: 7px;">
                        <p class="movie-title">{rec_movies[i]}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning(found_title) # Display the "not found" message
    else:
        st.warning("Please select a movie first.")
