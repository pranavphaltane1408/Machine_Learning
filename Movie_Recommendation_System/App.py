import streamlit as st
import pickle
import pandas as pd
import requests

# Function to fetch movie poster
def fetch_poster(id):
    try:
        # Using the provided API key
        api_key = '00f80ced9a15fd5f9f6a120b6f80def6'
        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{id}?api_key={api_key}"
        )
        data = response.json()
        
        # Check if 'poster_path' exists
        if 'poster_path' in data and data['poster_path']:
            return f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
        else:
            return "https://via.placeholder.com/500x750?text=No+Image+Available" 
    except Exception as e:
        return "https://via.placeholder.com/500x750?text=Error+Fetching+Image"

# Load pre-saved data
movies_dict = pickle.load(open('Movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))

# Verify columns in the DataFrame
print(movies.columns)  

# Recommendation function
def recommend(movie):
    try:
        # Get index of the selected movie
        movie_index = movies[movies['title'] == movie].index[0]
        
        # Get distances from the similarity matrix
        distances = similarity[movie_index]
        
        # Get the top 5 similar movies (avoid out of range errors by making sure there are enough recommendations)
        movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        
        # Check if there are enough recommendations
        if len(movie_list) < 5:
            movie_list = movie_list + [(0, 0)] * (5 - len(movie_list))  
        
        recommend_movies = []
        recommend_movies_poster = []
        
        # Iterate over the movie list to fetch the movie titles and posters
        for i in movie_list:
            movie_id = movies.iloc[i[0]]['id'] 
            if movie_id is not None:
                recommend_movies.append(movies.iloc[i[0]].title)
                recommend_movies_poster.append(fetch_poster(movie_id))
            else:
                recommend_movies.append('Unknown Movie')
                recommend_movies_poster.append('https://via.placeholder.com/500x750?text=No+Image+Available')

        return recommend_movies, recommend_movies_poster
    except IndexError:
        return ["Movie not found in the database."], []
    except KeyError as e:
        return [f"Key Error: {e}"], []
    except Exception as e:
        return [f"An error occurred: {e}"], []

# Streamlit app
st.title('Movie Recommendation System')

# Dropdown for movie selection
selected_movie_name = st.selectbox(
    "Select a Movie",
    movies['title'].values
)

# Button to generate recommendations
if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)
    
    if len(names) == 1 and names[0] == "Movie not found in the database.":
        st.error(names[0])
    else:
        st.subheader("Recommended Movies:")
        cols = st.columns(5)  # Create 5 columns for the 5 recommendations
        for idx, col in enumerate(cols):
            with col:
                st.text(names[idx])
                st.image(posters[idx])
