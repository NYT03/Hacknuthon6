import streamlit as st
import json
from figma_api import fetch_figma_data


def save_response_to_file(data, filename="figma_response.json"):
    """Save JSON response to a file."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def main():
    """Main function to run the Streamlit app."""
    st.title("Figma API Explorer")
    st.write("Select an endpoint to fetch data from the Figma API.")

    # User inputs
    endpoint_type = st.selectbox("Select Endpoint Type", [
        "files", "images", "projects", "team_projects", "components", "component_sets",
        "styles", "comments", "user_me", "file_nodes", "team_components", "team_styles"
    ])
    param = st.text_input("Enter Parameter (e.g., FILE_KEY, PROJECT_ID, TEAM_ID)")

    # Additional input for node_id when 'file_nodes' is selected
    node_id = None
    if endpoint_type == "file_nodes":
        node_id = st.text_input("Enter Node ID")

    # API request when button is clicked
    if st.button("Fetch Data"):
        query_params = {'ids': node_id} if node_id else None
        data, error = fetch_figma_data(endpoint_type, param, query_params)

        if error:
            st.error(error)
        else:
            st.success("API Request Successful!")
            st.json(data)  # Display response

            # Save response to a file
            save_response_to_file(data)

            st.download_button(
                label="Download JSON",
                data=json.dumps(data, indent=4),
                file_name="figma_response.json",
                mime="application/json"
            )


if __name__ == "__main__":
    main()
