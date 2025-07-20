import streamlit as st
import pandas as pd
import altair as alt
import google.generativeai as genai

# ===== Page Visuals =====
st.set_page_config(
    page_title="Club Analysis Dashboard",
    page_icon="🐣",
    layout="wide",
    initial_sidebar_state="expanded")

alt.theme.enable("dark")

# - Page Title -
col1, col2 = st.columns(2)
with col1:
    st.title("Club Analysis Dashboard")
with col2:
    st.header("Use this dashboard to turn your club data into insights.")

# ===== Upload File =====
uploaded_file = st.file_uploader("Choose a CSV or Excel file to begin", type=["csv", "xlsx"])

# Does not run anything unless file was uploaded properly
if uploaded_file is not None:
    # ===== Creating DataFrame =====
    # Get the file extension and create the DataFrame
    file_extension = uploaded_file.name.split('.')[-1]
    if file_extension == "csv":
        df = pd.read_csv(uploaded_file)
    elif file_extension == "xlsx":
        df = pd.read_excel(uploaded_file)

    st.success("File uploaded successfully! Your dashboard is below.")
    st.divider()

    # ===== Data Analysis Container =====
    with st.container(border=True):
        col6, col7, col8 = st.columns(3)

        with col6:
            st.subheader("Top Club Members:")
            meeting_counts = df['Name (First, Last)'].value_counts()
            st.dataframe(meeting_counts)

        with col7:
            meeting_attendees = df['Meeting'].value_counts()
            st.header("Attendance Throughout the Year:")
            st.line_chart(meeting_attendees)

        with col8:
            st.header("Club Stats this Quarter:")
            num_meetings = len(df['Meeting'].unique())
            st.subheader(f"{num_meetings} Meetings held.")

            attendee_meeting_counts = df['Name (First, Last)'].value_counts()
            recurring_attendees = attendee_meeting_counts[attendee_meeting_counts > 1]
            st.subheader(f"{len(recurring_attendees)} recurring members.")

            total_attendees = len(df['Name (First, Last)'].unique())
            st.subheader(f"{total_attendees} total unique attendees.")

        st.subheader(f"Most popular event: {meeting_attendees.idxmax()} ({meeting_attendees.max()} attendees)")

    # ===== GEMINI EVENT RECOMMENDER =====
    # Gather data to feed into model
    popular_events_summary = df['Meeting'].value_counts().nlargest(3).to_dict()
    major_summary = df['Major'].value_counts().nlargest(5).to_dict()
    dietary_summary = df['Food Restrictions'].dropna().unique().tolist()

    # GEMINI Recommendations Container
    with st.container(border=True):  
        st.header("Generate Event Ideas with Gemini")
        # API KEY INPUT
        st.write("Enter your API key here:")
        gemini_key = st.text_input("Enter your Gemini API key here:", type="password")
        if gemini_key:
            st.write("Successfully updated API key.")
        st.write("Pick a category to generate event ideas based on your club data:")
        
        left, middle1, middle2, right = st.columns(4)
        event_topics = ""
        if left.button("Workshops", icon="😸", use_container_width=True):
            event_topics = "Workshops"
        elif middle1.button("Socials", icon="🙋‍♀️", use_container_width=True):
            event_topics = "Socials"
        elif middle2.button("Career Prep", icon="💼", use_container_width=True):
            event_topics = "Career Prep"
        elif right.button("All of them", use_container_width=True):
            event_topics = "Workshops, Socials, Career Prep"

        if event_topics:
            if not gemini_key:
                st.warning("Please enter your Gemini API key above to generate ideas.")
                st.stop()
            
            with st.spinner("Generating ideas..."):
                try:
                    genai.configure(api_key=gemini_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"""
                    You are an expert event planner for a university student club. Your task is to generate creative event ideas based on our club's data.

                    **Context from Club Data:**
                    * **Most Popular Past Events:** {popular_events_summary}
                    * **Most Common Majors:** {major_summary}
                    * **Common Dietary Restrictions:** {dietary_summary}

                    **Your Task:**
                    Generate 3 distinct event ideas for EACH of the following topics: {event_topics}.
                    If the topic list is "Workshops, Socials, Career Prep", generate 2 distinct ideas for each instead.

                    **Output Format Instructions:**
                    For each topic, provide a markdown heading (e.g., "## Workshops").
                    For each idea under a topic, provide:
                    1.  A creative, bolded title.
                    2.  A one to two-sentence description explaining the event.
                    3.  A brief note on how it caters to our members, citing the provided data context.
                    """
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"An error occurred with the Gemini API: {e}")
else:
    # Warning if dataset is not loaded
    st.info("Please upload your club's data file to get started.")