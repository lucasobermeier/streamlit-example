import streamlit as st
import pandas as pd
import random

# Global Variables
users = []  # List to store registered user names
race_results = []  # List to store results of each race

points_dict = {
    1: 15, 2: 12, 3: 10, 4: 8, 5: 7, 6: 6, 7: 5, 8: 4, 9: 3, 10: 2, 11: 1, 12: 0
} 

def add_bg_and_custom_css():
    # Adjusting the background image and text container styles with an updated overlay setup
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://pliki.ppe.pl/storage/39653022149bea4f5935/39653022149bea4f5935-1200w.jpg");
            background-size: cover;
            background-position: center;
            position: relative;  /* Essential for the overlay to work correctly */
        }

        /* Correcting the overlay to ensure it does not cover content */
        .stApp:before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(255, 255, 255, 0.5);  /* Semi-transparent white overlay */
            z-index: -1;  /* Setting z-index to 0 or below content z-index */
        }

        .text-container {
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            position: relative;  /* Ensure the text container is above the overlay */
            z-index: 1;  /* Ensuring content is above the overlay */
        }
        </style>
        """,
        unsafe_allow_html=True
    )



def welcome_screen():
    add_bg_and_custom_css()
    st.title('Mario Kart: The Ranking App')
    
    # Using Streamlit's markdown with unsafe_allow_html to embed HTML for styling
    st.markdown("""
        <div class="text-container">
            <p>Welcome to the <strong>Mario Kart: The Ranking App</strong>! This interactive application allows you to set up races, register players, and track race results in real-time. Here’s what you can do:</p>
            <ul>
                <li><strong>Register Players:</strong> Add participants to the race and manage your player list.</li>
                <li><strong>Record Race Results:</strong> After each race, input the results to see who's leading.</li>
                <li><strong>View Leaderboard:</strong> Check out the leaderboard to see rankings and find out who's on top in the Mario Kart championship.</li>
            </ul>
            <p>Whether you're hosting a Mario Kart tournament or just having fun with friends, this app will make managing and displaying results easy and fun. Get started by registering players and let the races begin!</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button('Go to Registration'):
        st.session_state.current_screen = 'register'
        
def register_user(username):
    if username not in st.session_state.users:
        st.session_state.users.append(username)
        return True
    else:
        st.error(f"Error: A user with the username '{username}' already exists.")
        return False

def register_user_screen():
    add_bg_and_custom_css()  # Ensure this calls the function that sets the background image
    
    st.title('Register a New User')
    new_username = st.text_input("Enter a new username to register:")
    register_button = st.button("Register")
    start_racing_button = st.button("Let's start racing")

    if register_button:
        if register_user(new_username):
            st.success("User registered successfully")
    
    # Display registered users table only once and always
    if st.session_state.users:
        st.write("Registered Users:")
        user_df = pd.DataFrame(st.session_state.users, columns=["Username"])
        st.table(user_df)

    # Allow moving to the next screen only if there are users registered
    if start_racing_button:
        if st.session_state.users:
            st.session_state.current_screen = 'add_results'
        else:
            st.error("Please register at least one user before starting the race.")

def add_race_result_screen():
    add_bg_and_custom_css()
    st.title('Race Results:')

    # Setting up the number of races with a confirmation button
    if 'total_races' not in st.session_state:
        # This initial setup will only ask for the number of races if not yet defined
        races_input = st.number_input("Enter number of races", min_value=1, max_value=10, value=3, step=1)
        if st.button('Start Racing'):
            st.session_state.total_races = races_input
            st.session_state.current_race = 1  # Initializing the current race here after confirmation
        return  # Return early to avoid executing further logic until 'Start Racing' is clicked

    # Ensuring current_race is defined before trying to access it
    if 'current_race' in st.session_state and st.session_state.current_race <= st.session_state.total_races:
        race_number = st.session_state.current_race
        st.header(f'Race {race_number}: Results')

        # User placement inputs
        placements = {user: st.selectbox(f"Select place for {user}:", range(1, 13), key=f"{user}_{race_number}") for user in st.session_state.users}
        
        if st.button(f'Submit Results for Race {race_number}'):
            # Store results for each user
            for user, placement in placements.items():
                st.session_state.race_results.append({
                    'race_number': race_number,
                    'username': user,
                    'position': placement,
                    'points': points_dict[placement]
                })
            st.success(f"Results for Race {race_number} submitted successfully.")
            
            # Move to the next race or finish
            if race_number < st.session_state.total_races:
                st.session_state.current_race += 1
            else:
                st.session_state.current_screen = 'view_leaderboard'
    else:
        st.error("Please set the total number of races first.")

    if st.button('View Leaderboard'):
        st.session_state.current_screen = 'view_leaderboard'

# Initialize session state for race results if not already done
if 'race_results' not in st.session_state:
    st.session_state.race_results = []

def calculate_total_points():
    if st.session_state.race_results:  # Ensure there is data to process
        df = pd.DataFrame(st.session_state.race_results)
        if 'username' in df.columns and 'points' in df.columns:  # Ensure the expected columns are present
            leaderboard_df = df.groupby('username')['points'].sum().reset_index()
            leaderboard_df.sort_values(by='points', ascending=False, inplace=True)
            leaderboard_df['rank'] = leaderboard_df['points'].rank(method='min', ascending=False).astype(int)
            return leaderboard_df
        else:
            st.error("Expected data columns missing in the race results.")
            return pd.DataFrame(columns=['Username', 'Total Points', 'Rank'])
    else:
        st.warning("No race results available yet.")
        return pd.DataFrame(columns=['Username', 'Total Points', 'Rank'])

def view_leaderboard_screen():
    add_bg_and_custom_css()
    st.title('Final Leaderboard')
    leaderboard_df = calculate_total_points()
    st.table(leaderboard_df)
    if st.button('Reset Game'):
        st.session_state.pop('total_races', None)
        st.session_state.pop('current_race', None)
        st.session_state.pop('race_results', None)
        users.clear()
        st.session_state.current_screen = 'welcome'
    if st.button('Quit Game'):
        st.session_state.current_screen = 'welcome'

# Initialize session state for users list if it's not already initialized
if 'users' not in st.session_state:
    st.session_state.users = []

# Initialize session state for navigation
if 'current_screen' not in st.session_state:
    st.session_state.current_screen = 'welcome'

# Render the current screen based on the session state
if st.session_state.current_screen == 'welcome':
    welcome_screen()
elif st.session_state.current_screen == 'register':
    register_user_screen()
elif st.session_state.current_screen == 'add_results':
    add_race_result_screen()
elif st.session_state.current_screen == 'view_leaderboard':
    view_leaderboard_screen()
