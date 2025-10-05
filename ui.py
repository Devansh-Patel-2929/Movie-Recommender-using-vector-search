import streamlit as st
from typing import List, Dict, Any
import app
import os

# UI COMPONENTS

def create_rating_stars(rating_str):
    rating = float(rating_str)
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
    
    tab1, tab2 = st.tabs(["🧠 AI Mood Search", "🔍 Find Similar Movies"])
    
    with tab1:
        st.markdown("**Describe what you're in the mood for**")
        col1, col2 = st.columns([3, 1])
        with col1:
            prompt = st.text_input(
                "Movie mood description:",
                placeholder="e.g., a mind-bending sci-fi thriller with plot twists and philosophical themes...",
                key="rag_input",
                label_visibility="collapsed"
            )
        with col2:
            num_recs = st.slider("Number of recommendations", 1, 6, 3, key="rag_slider")
        
        if st.button("✨ Generate AI Recommendations", use_container_width=True, type="primary"):
            if prompt:
                with st.spinner("🔮 Analyzing your vibe with Azure AI..."):
                    st.session_state.recommendations = app.vector_search(prompt, num_recs)
                    st.session_state.mode = "rag"
                    st.session_state.search_term = f'for "{prompt}"'
                    # Reset all flip states when new recommendations come
                    for movie in st.session_state.recommendations:
                        st.session_state[f"flip_state_{movie['id']}"] = False
                        st.session_state[f"summary_state_{movie['id']}"] = False
            else:
                st.warning("Please describe what you're in the mood for!")
    
    with tab2:
        st.markdown("**Find movies similar to ones you love**")
        col1, col2 = st.columns([3, 1])
        with col1:
            movie_name = st.text_input(
                "Enter a movie title:",
                placeholder="e.g., Inception, The Shawshank Redemption...",
                key="similar_input",
                label_visibility="collapsed"
            )
        with col2:
            num_similar = st.slider("Number of similar movies", 1, 6, 3, key="similar_slider")
        
        if st.button("🔍 Find Similar Movies", use_container_width=True, type="primary"):
            if movie_name:
                with st.spinner("📡 Searching vector database..."):
                    st.session_state.recommendations = app.find_similar(movie_name, num_similar)
                    st.session_state.mode = "similar"
                    st.session_state.search_term = f'similar to "{movie_name}"'
                    # Reset all flip states when new recommendations come
                    for movie in st.session_state.recommendations:
                        st.session_state[f"flip_state_{movie['id']}"] = False
                        st.session_state[f"summary_state_{movie['id']}"] = False
            else:
                st.warning("Please enter a movie title!")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # RESULTS DISPLAY
    if st.session_state.recommendations:
        st.markdown(f"""
            <h2 style="color: white; margin: 2rem 0 1rem 0;">
                🎉 Recommendations {st.session_state.search_term}
            </h2>
        """, unsafe_allow_html=True)
        
        num_movies = len(st.session_state.recommendations)
        cols = st.columns(min(num_movies, 3))
        
        for i, movie in enumerate(st.session_state.recommendations):
            display_movie_card(movie, cols[i % 3])

    # FOOTER
    st.markdown("""
        <div style="text-align: center; margin-top: 4rem; padding: 2rem; color: #6b7280; border-top: 1px solid rgba(255,255,255,0.1);">
            <p>Powered by Azure AI • 🎬 CineAI Movie Recommender</p>
            <p style="font-size: 0.875rem;">© 2025 CineAI.</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == '__main__':
    main_app()