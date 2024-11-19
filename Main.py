import streamlit as st
from Data_Scraping import scrap_articles_by_category, analyze_data  # Replace with your actual module name


st.set_page_config(page_title="Blog Comment Sentiment Analyzer", layout="centered")



# Method 3: If you want to add a caption
st.sidebar.image('Hespress-logo.png', 
                 width=300, 
                 caption='HesPress Sentiment Analyzer')

st.sidebar.write("""
### HesPress Sentiment Insights 

A powerful Streamlit application that scrapes articles from Hespress, 
analyzing comments through advanced sentiment detection. 
Uncover public opinion across different news categories 
with multilingual (Arabic/French) sentiment analysis, 
transforming raw comments into meaningful insights.
""")

st.title("HesPress Sentiment Insights: Moroccan News Comment Analyzer")


categories = [
    "Politique",  
    "Economie",   
    "Sport",     
    "Societe",    
    "Monde",    
    "Culture",    
]
st.markdown("""
<style>
.metric-card {
    background-color: #f0f2f6;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 15px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}

.metric-card:hover {
    transform: scale(1.02);
    box-shadow: 0 6px 8px rgba(0,0,0,0.15);
}

.metric-value {
    font-size: 2.5em;
    font-weight: bold;
    color: #4CAF50;
    margin-bottom: 10px;
}

.metric-label {
    font-size: 1em;
    color: #666;
    text-transform: uppercase;
}
</style>
""", unsafe_allow_html=True)

def metric_card(value, label, icon=None):
    # If an icon is provided, you can add it to the card
    icon_html = f'<i class="{icon}"></i>' if icon else ''
    
    card_html = f"""
    <div class="metric-card">
        {icon_html}
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def display_metrics(total_articles, total_comments):
    # Create columns for metrics
    col1, col2 = st.columns(2)
    
    with col1:
        metric_card(str(total_articles), "Total Articles", "fas fa-newspaper")
    
    with col2:
        metric_card(str(total_comments), "Total Comments", "fas fa-comments")


# Title and intro
st.write("### Choose a category to analyze Hespress comments")
st.write("""
Dive into the sentiment of Moroccan news by selecting a category. 
Our application will scrape articles, analyze comments, 
and provide deep insights into public opinion across different news domains.
""")

# Initialize session state for selected category
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = None

# Create columns for cards
cols = st.columns(3)  # 3 columns

# Render category cards
for i, category in enumerate(categories):
    with cols[i % 3]:
        # Create a button that looks like a card
        card_selected = st.button(
            label=f"{category}", 
            key=category
        )
        if card_selected:
            st.session_state.selected_category = category

# Display selected category
if st.session_state.selected_category:
    
    st.success(f"Selected Category:{st.session_state.selected_category}")
    
    # Add your scraping logic here
    if st.button("Start Scraping", use_container_width=True):
        category = st.session_state.selected_category.lower()
        
        # Call scraping function
        with st.spinner(f"Scraping articles and comments for '{category}'..."):
            scrap_articles_by_category(category)
        
        # Call analysis function
        with st.spinner("Analyzing data..."):
            analysis_result = analyze_data(category)
        
        # Display analysis results
        if analysis_result:
            total_articles = analysis_result["total_articles"]
            total_comments = analysis_result["total_comments"]
            comments_by_date = analysis_result["comments_by_date"]

            # Display metrics as cards
            display_metrics(total_articles, total_comments)


            # Plot comments by date
            st.write("### Comments by Date")
            if not comments_by_date.empty:
                chart_data = comments_by_date[['date', 'count']]
    
                st.line_chart(
                    data=chart_data,
                    x='date',
                    y='count'
                )
            else:
                st.warning("No comments available to analyze.")
        else:
            st.error("Analysis failed. Please check your data.")