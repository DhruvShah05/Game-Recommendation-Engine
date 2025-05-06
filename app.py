import streamlit as st
from auth import authenticate_user
from db import get_or_create_user, get_user_purchases, update_user_purchases
from recommender import get_content_based_recommendations
import pandas as pd
import numpy as np

# Load the game library data
@st.cache_data
def load_game_library():
    return pd.read_csv('/Users/dhruvshah/Desktop/Blog/archive-3/project/df_processed.csv')

# Load the media data
@st.cache_data
def load_media_data():
    return pd.read_csv('/Users/dhruvshah/Desktop/Blog/archive-3/steam_media_data.csv')

def main():
    st.title('Steam-like Game Recommendation Engine')

    # Login Page
    if 'email' not in st.session_state:
        st.subheader('Login')
        if st.button('Login with Google'):
            email = authenticate_user()
            st.session_state['email'] = email
            st.rerun()
    else:
        email = st.session_state['email']
        st.success(f'Logged in as {email}')

        # Homepage
        user = get_or_create_user(email)
        purchases = get_user_purchases(email)

        # Load media data
        game_media = load_media_data()

        if len(purchases) < 3:
            st.subheader('Most Popular Games')
            df = load_game_library()
            df['total_reviews'] = df['positive_ratings'] + df['negative_ratings']
            filtered_df = df[df['total_reviews'] >= 50]
            filtered_df['review_score'] = filtered_df['positive_ratings'] / filtered_df['total_reviews']
            filtered_df['popularity_score'] = filtered_df['review_score'] * np.log(filtered_df['total_reviews'])
            popular_games = filtered_df.sort_values(by='popularity_score', ascending=False)
            top_10 = popular_games[['appid', 'name', 'review_score', 'total_reviews', 'popularity_score']].head(10)
            display_recommended_games(top_10, game_media)
        else:
            recs = get_content_based_recommendations(purchases)
            display_recommended_games(recs, game_media)

        # Game Library
        # Pagination and Search
        items_per_page = 10
        search_query = st.text_input('Search for a game:')

        # Filter games based on search query
        game_library = load_game_library()
        if search_query:
            game_library = game_library[game_library['name'].str.contains(search_query, case=False, na=False)]

        # Calculate total pages
        total_games = len(game_library)
        total_pages = (total_games // items_per_page) + (1 if total_games % items_per_page > 0 else 0)

        # Select page
        def get_page_number():
            if 'page_number' not in st.session_state:
                st.session_state['page_number'] = 1
            return st.session_state['page_number']

        page_number = get_page_number()

        # Display games for the current page
        start_idx = (page_number - 1) * items_per_page
        end_idx = start_idx + items_per_page

        st.subheader('Game Library')
        for idx, row in game_library.iloc[start_idx:end_idx].iterrows():
            media_row = game_media[game_media['steam_appid'] == row['appid']]
            col1, col2 = st.columns([1, 3])
            with col1:
                if not media_row.empty:
                    image_url = media_row.iloc[0]['header_image']
                    st.image(image_url, width=100)
            with col2:
                st.write(row['name'])
                if row['appid'] not in purchases:
                    if st.button(f"Buy {row['name']}", key=row['appid']):
                        update_user_purchases(email, [row['appid']])
                        st.success(f"Purchased {row['name']}!")
                        st.rerun()

        # Pagination controls
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button('Previous', key='prev_page') and page_number > 1:
                st.session_state['page_number'] -= 1
                st.rerun()
        with col3:
            if st.button('Next', key='next_page') and page_number < total_pages:
                st.session_state['page_number'] += 1
                st.rerun()

        st.write(f'Page {page_number} of {total_pages}')

# Function to display recommended games with a horizontal slider
def display_recommended_games(recs, game_media):
    if not recs.empty:
        st.subheader('Recommended Games')
        if 'current_game_index' not in st.session_state:
            st.session_state['current_game_index'] = 0
        current_game_index = st.session_state['current_game_index']
        total_games = len(recs)

        # Display current game
        row = recs.iloc[current_game_index]
        media_row = game_media[game_media['steam_appid'] == row['appid']]
        if not media_row.empty:
            image_url = media_row.iloc[0]['header_image']
            st.image(image_url, caption=row['name'], use_column_width=True)
            if 'score' in row:
                st.write(f"Score: {row['score']:.4f}")

        # Navigation buttons
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button('Previous') and current_game_index > 0:
                st.session_state['current_game_index'] -= 1
                st.rerun()
        with col3:
            if st.button('Next') and current_game_index < total_games - 1:
                st.session_state['current_game_index'] += 1
                st.rerun()

    else:
        st.write('No recommendations available.')

if __name__ == '__main__':
    main() 