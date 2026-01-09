# TODO: Debug and Fix Movie Recommendation System

## Backend Fixes (main.py)
- [x] Fix Pydantic field: Change "Overview" to "overview" in TMDBMovieDetails
- [x] Update tmdb_get_trailer_url: Accept both "Trailer" and "Teaser" types
- [x] Add error handling in startup event for pickle loading to prevent startup failures

## Frontend Fixes (app.py)
- [x] Update trailer section: Use st.video(trailer_url) instead of iframe
- [x] Safe video ID extraction: Handle '&' in URL properly
- [x] Add fallback message: "Trailer not available" when trailer_url is null

## Testing
- [ ] Test backend startup: uvicorn main:app --reload
- [ ] Test frontend: streamlit run app.py
- [ ] Verify trailer shows correctly and fallback works
