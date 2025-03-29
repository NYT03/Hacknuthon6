import streamlit as st
from figma_api import fetch_figma_data

def main():
    """Main function to run the Streamlit app."""
    st.title("Figma API Explorer")
    st.write("Select an endpoint to fetch data from Figma API.")

    # User inputs
    endpoint_type = st.selectbox("Select Endpoint Type", [
        "files", "images", "projects", "team_projects", "components", "component_sets",
        "styles", "comments", "user_me", "file_nodes", "team_components", "team_styles"
    ])  
    param = st.text_input("Enter Parameter (FILE_KEY, PROJECT_ID, TEAM_ID, NODE_ID, etc.)")
    
    # API request when button is clicked
    if st.button("Fetch Data"):
        data, error = fetch_figma_data(endpoint_type, param)
        
        if error:
            st.error(error)
        else:
            st.success("API Request Successful!")
            st.json(data)  # Display response

if __name__ == "__main__":
    main()
