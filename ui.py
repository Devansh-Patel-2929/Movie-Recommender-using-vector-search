import streamlit as st
from typing import List, Dict, Any, Tuple
import vector_search
import os

# UI COMPONENTS

def create_rating_stars(rating):
    full_stars = int(rating / 2)
    half_star = 1 if (rating / 2 - full_stars) >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star
    
    stars_html = "★" * full_stars
    if half_star:
        stars_html += "★"
    stars_html += "☆" * empty_stars
    
    return stars_html

def display_movie_card(movie: Dict[str, Any], col):
    with col:
        # unique key for each movie's flip state
        flip_state_key = f"flip_state_{movie['id']}"
        if flip_state_key not in st.session_state:
            st.session_state[flip_state_key] = False
            
        # unique key for view state
        summary_state_key = f"summary_state_{movie['id']}"
        if summary_state_key not in st.session_state:
            st.session_state[summary_state_key] = False
            
        # Determine which side to show
        is_flipped = st.session_state[flip_state_key]
        show_summary = st.session_state[summary_state_key]
        
        # Flip card container
        if is_flipped:
            # BACK SIDE - Show details with toggle between rating/synopsis and summary
            if show_summary:
                # SUMMARY VIEW
                st.markdown(f"""
                    <div class="flip-card-back">
                        <div class="back-content">
                            <h3>{movie['title']}</h3>
                            <div class="content-section full-height">
                                <h4>📖 Summary</h4>
                                <div class="scrollable-content">
                                    <p class="summary-text">{movie['plot_synopsis']}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Button to show rating & synopsis
                summary_button_key = f"summary_btn_{movie['id']}"
                if st.button("📊 Show Rating & Synopsis", key=summary_button_key, use_container_width=True):
                    st.session_state[summary_state_key] = False
                    st.rerun()
                    
            else:
                # RATING & SYNOPSIS VIEW
                st.markdown(f"""
                    <div class="flip-card-back">
                        <div class="back-content">
                            <h3>{movie['title']}</h3>
                            <div class="rating-section">
                                <div class="back-rating">
                                    <div class="rating-stars">{create_rating_stars(movie['rating'])}</div>
                                    <div class="rating-score">{movie['rating']}/10</div>
                                </div>
                            </div>
                            <div class="synopsis-section">
                                <h4>🎭 Synopsis</h4>
                                <div class="scrollable-content synopsis-scroll">
                                    <p class="synopsis-text">{movie['plot_summary']}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Button to show summary
                summary_button_key = f"summary_btn_{movie['id']}"
                if st.button("📖 View Summary", key=summary_button_key, use_container_width=True):
                    st.session_state[summary_state_key] = True
                    st.rerun()
            
            # Button to flip back to front
            back_button_key = f"back_btn_{movie['id']}"
            if st.button("🎬 Back to Movie", key=back_button_key, use_container_width=True):
                st.session_state[flip_state_key] = False
                st.session_state[summary_state_key] = False  # Reset summary state
                st.rerun()
                
        else:
            # FRONT SIDE - Show basic info
            st.markdown(f"""
                <div class="flip-card-front">
                    <div class="movie-info">
                        <h3>{movie['title']}</h3>
                        <div class="movie-meta">
                            <span class="year">{movie['year']}</span>
                        </div>
                        <div class="genres">
                            {''.join([f'<span class="genres-tag">{genres}</span>' for genres in movie['genres']])}
                        </div>
                        <div class="rating-stars">
                            {create_rating_stars(movie['rating'])}
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Button to flip to back side
            flip_button_key = f"flip_btn_{movie['id']}"
            if st.button("📖 View Details", key=flip_button_key, use_container_width=True):
                st.session_state[flip_state_key] = True
                st.rerun()

def load_css():
    """Load external CSS file"""
    css_file = os.path.join(os.path.dirname(__file__), 'css', 'styles.css')
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def search_movie_titles(query: str, movie_titles: List[str], max_results: int = 5) -> List[str]:
    """Search for movie titles that match the query"""
    if not query:
        return []
    
    query = query.lower().strip()
    matches = []
    
    for title in movie_titles:
        if query in title.lower():
            matches.append(title)
    
    # Sort by how early the query appears in the title
    matches.sort(key=lambda x: x.lower().find(query))
    
    return matches[:max_results]

# sample list of movie titles
MOVIE_TITLES = [
    "The Shawshank Redemption", "The Godfather", "The Dark Knight", "Pulp Fiction", 
    "Forrest Gump", "Inception", "The Matrix", "Goodfellas", "The Lord of the Rings", 
    "Fight Club", "Star Wars", "The Avengers", "Titanic", "Jurassic Park", 
    "The Lion King", "Back to the Future", "The Silence of the Lambs", "Casablanca",
    "Psycho", "The Godfather Part II", "The Empire Strikes Back", "The Social Network",
    "Parasite", "Spirited Away", "Interstellar", "The Departed", "Whiplash",
    "Gladiator", "The Prestige", "Django Unchained", "The Shining", "Alien",
    "Avengers: Endgame", "The Dark Knight Rises", "Inglourious Basterds",
    "Saving Private Ryan", "The Green Mile", "American Beauty", "The Usual Suspects",
    "Leon: The Professional", "The Pianist", "City of God", "Once Upon a Time in Hollywood",
    "Joker", "1917", "Parasite", "Get Out", "La La Land", "Mad Max: Fury Road"
]

# MAIN STREAMLIT APP

def main_app():
    st.set_page_config(
        page_title="CineAI - Intelligent Movie Recommendations",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    
    #external css
    load_css()
    
    # APP STATE INITIALIZATION
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = []
        st.session_state.mode = "welcome"
        st.session_state.search_term = ""
        st.session_state.current_filters = {
            'year_range': (1920, 2024),
            'rating_range': (0.0, 10.0),
            'selected_genres': []
        }
        st.session_state.selected_movie = ""
    
    # sample list of genres
    PREDEFINED_GENRES = [
        "Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary", 
        "Drama", "Family", "Fantasy", "History", "Horror", "Music", "Mystery",
        "Romance", "Science Fiction", "TV Movie", "Thriller", "War", "Western"
    ]
    
    # Year range 
    MIN_YEAR = 1920
    MAX_YEAR = 2024

    # HEADER
    st.markdown("""
        <div class="main-header">
            <div style="text-align: center;">
                <h1 style="font-size: 3.5rem; font-weight: 800; margin: 0; background: linear-gradient(135deg, #fff 0%, #e0e7ff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">CineAI</h1>
                <p style="font-size: 1.25rem; color: #e0e7ff; margin: 0.5rem 0 0 0;">Intelligent Movie Recommendations Powered by Azure AI</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # SEARCH SECTION
    st.markdown("### 🎯 Find Your Perfect Movie")
    st.markdown("Discover movies using AI-powered search or find similar titles")
    
    active_tab = st.radio(
        "Choose search type:",
        ["🧠 AI Mood Search", "🔍 Find Similar Movies"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # Initialize variables
    prompt = ""
    movie_name = ""
    num_recs = 3
    
    # Display the appropriate search interface based on active tab
    if active_tab == "🧠 AI Mood Search":
        st.markdown("**Describe what you're in the mood for**")
        search1, button_Prompt_slider = st.columns([2,1],gap="medium")
        with button_Prompt_slider:
            num_recs = st.slider(
                "Number of recommendations", 
                1, 6, 3, 
                key="prompt_slider",
                help="Select how many movies you want to see"
            )
        with search1:
            prompt = st.text_input(
                "Movie mood description:",
                placeholder="e.g., a mind-bending sci-fi thriller with plot twists and philosophical themes...",
                key="rag_input",
                label_visibility="collapsed"
            )
        
    else:  # "🔍 Find Similar Movies"
        st.markdown("**Find movies similar to ones you love**")
        search2, button_similar_slider = st.columns([2,1],gap="medium")
        with button_similar_slider:
            num_recs = st.slider(
                "Number of recommendations", 
                1, 6, 3, 
                key="similar_slider",
                help="Select how many movies you want to see"
            )
        with search2:
            # Movie search with autocomplete
            search_query = st.text_input(
                "Search for a movie:",
                placeholder="Start typing to search for movies... and press ENTER",
                key="similar_input",
                label_visibility="collapsed"
            )
            
            # Search for matching movies
            if search_query:
                matching_movies = search_movie_titles(search_query, MOVIE_TITLES, max_results=5)
                
                if matching_movies:
                    st.markdown("**🔍 Matching Movies:**")
                    
                    # Create columns for the movie buttons
                    movie_cols = st.columns(len(matching_movies))
                    
                    for idx, movie_title in enumerate(matching_movies):
                        with movie_cols[idx]:
                            if st.button(
                                f"🎬 {movie_title}", 
                                key=f"movie_btn_{idx}",
                                use_container_width=True,
                                type="secondary" if st.session_state.selected_movie != movie_title else "primary"
                            ):
                                st.session_state.selected_movie = movie_title
                                st.rerun()
                    
                    # Show selected movie
                    if st.session_state.selected_movie:
                        st.success(f"✅ Selected: **{st.session_state.selected_movie}**")
                        movie_name = st.session_state.selected_movie
                else:
                    st.info("🔍 No matching movies found. Try a different search term.")
            else:
                st.info("💡 Start typing to search for movies...")

    # FILTERS SECTION
    filter_col1, filter_col2, filter_col3 = st.columns(3, gap="large")
    
    with filter_col1:
        st.markdown("**🎬 Year Range**")
        year_range = st.slider(
            "Select year range:",
            min_value=MIN_YEAR,
            max_value=MAX_YEAR,
            value=st.session_state.current_filters['year_range'],
            key="year_slider",
            label_visibility="collapsed"
        )
        st.markdown(f"**Selected:** {year_range[0]} - {year_range[1]}")
    
    with filter_col2:
        st.markdown("**⭐ Rating Range**")
        rating_range = st.slider(
            "Select rating range:",
            min_value=0.0,
            max_value=10.0,
            value=st.session_state.current_filters['rating_range'],
            step=0.5,
            key="rating_slider",
            label_visibility="collapsed"
        )
        st.markdown(f"**Selected:** {rating_range[0]} - {rating_range[1]}")
    
    with filter_col3:
        st.markdown("**🎭 Genres**")
        selected_genres = st.multiselect(
            "Select genres:",
            options=PREDEFINED_GENRES,
            default=st.session_state.current_filters['selected_genres'],
            key="genre_multiselect",
            label_visibility="collapsed"
        )
        st.markdown(f"**Selected:** {', '.join(selected_genres) if selected_genres else 'All genres'}")

    # Update current filters
    st.session_state.current_filters = {
        'year_range': year_range,
        'rating_range': rating_range,
        'selected_genres': selected_genres
    }

    # SINGLE ACTION BUTTON SECTION
    st.markdown("### 🚀 Generate Recommendations")
    
    # Determine button label and type based on active tab
    if active_tab == "🧠 AI Mood Search":
        button_label = "✨ Generate AI Recommendations"
        button_type = "primary"
    else:
        button_label = "🔍 Find Similar Movies"
        button_type = "primary"
    
    # Single dynamic button
    if st.button(button_label, use_container_width=True, type=button_type):
        if active_tab == "🧠 AI Mood Search":
            # AI Mood Search 
            if prompt:
                with st.spinner("🔮 Analyzing your vibe with Azure AI..."):
                    st.session_state.recommendations = vector_search.search_with_filtersAndPrompt(
                        query_text=prompt,
                        top_k=num_recs,
                        year_range=st.session_state.current_filters['year_range'],
                        rating_range=st.session_state.current_filters['rating_range'],
                        genre=st.session_state.current_filters['selected_genres']
                    )
                    st.session_state.mode = "rag"
                    st.session_state.search_term = f'for "{prompt}"'
                    # Reset all flip states when new recommendations come
                    for movie in st.session_state.recommendations:
                        st.session_state[f"flip_state_{movie['id']}"] = False
                        st.session_state[f"summary_state_{movie['id']}"] = False
            else:
                st.warning("Please describe what you're in the mood for!")
                
        else:  # "🔍 Find Similar Movies"
            if st.session_state.selected_movie:
                movie_name = st.session_state.selected_movie
                with st.spinner("📡 Searching vector database..."):
                    st.session_state.recommendations = vector_search.find_similar(
                        movie_name=movie_name,
                        top_k=num_recs,
                        year_range=st.session_state.current_filters['year_range'],
                        rating_range=st.session_state.current_filters['rating_range'],
                        genre=st.session_state.current_filters['selected_genres']
                    )
                    st.session_state.mode = "similar"
                    st.session_state.search_term = f'similar to "{movie_name}"'
                    # Reset all flip states when new recommendations come
                    for movie in st.session_state.recommendations:
                        st.session_state[f"flip_state_{movie['id']}"] = False
                        st.session_state[f"summary_state_{movie['id']}"] = False
            else:
                st.warning("Please select a movie from the search results!")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # RESULTS DISPLAY
    if st.session_state.recommendations:
        st.markdown(f"""
            <h2 style="color: white; margin: 2rem 0 1rem 0;">
                🎉 Recommendations {st.session_state.search_term}
            </h2>
        """, unsafe_allow_html=True)
        
        # Show active filters
        active_filters = []
        if st.session_state.current_filters['year_range'] != (MIN_YEAR, MAX_YEAR):
            active_filters.append(f"Years: {st.session_state.current_filters['year_range'][0]}-{st.session_state.current_filters['year_range'][1]}")
        
        if st.session_state.current_filters['rating_range'] != (0.0, 10.0):
            active_filters.append(f"Rating: {st.session_state.current_filters['rating_range'][0]}-{st.session_state.current_filters['rating_range'][1]}")
        
        if st.session_state.current_filters['selected_genres']:
            active_filters.append(f"Genres: {', '.join(st.session_state.current_filters['selected_genres'])}")
        
        if active_filters:
            st.info(f"📊 Active filters: {', '.join(active_filters)}")
        
        num_movies = len(st.session_state.recommendations)
        cols = st.columns(min(num_movies, 3))
        
        for i, movie in enumerate(st.session_state.recommendations):
            display_movie_card(movie, cols[i % 3])
    
    elif st.session_state.mode != "welcome":
        st.warning("🤷 No movies found matching your search criteria and filters. Try adjusting your search or filters.")

    # FOOTER
    st.markdown("""
        <div style="text-align: center; margin-top: 4rem; padding: 2rem; color: #6b7280; border-top: 1px solid rgba(255,255,255,0.1);">
            <p>Powered by Azure AI • 🎬 CineAI Movie Recommender</p>
            <p style="font-size: 0.875rem;">© 2025 CineAI.</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == '__main__':
    main_app()