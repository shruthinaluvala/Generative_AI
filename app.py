import streamlit as st
import google.generativeai as genai
import os # Used for potentially getting API key from environment variables later

# --- Configuration ---
st.set_page_config(page_title="Flavour Fusion AI Blogger", page_icon="🍲", layout="wide")

# --- Function to Generate Blog Post ---
def generate_recipe_blog(api_key, topic, word_count):
    """Uses Google Gemini to generate a recipe blog post."""
    try:
        genai.configure(api_key=api_key)

        # --- MODEL NAME UPDATE ---
        # Use a more current/available model name. 'gemini-1.5-pro-latest' is often recommended.
        # If you still encounter issues, try 'gemini-1.0-pro'.
        model_name = 'gemini-1.5-pro-latest'
        st.info(f"Using model: {model_name}") # Optional: Show which model is being used
        model = genai.GenerativeModel(model_name)
        # --- END MODEL NAME UPDATE ---

        # Constructing a detailed prompt for better results
        prompt = f"""
        You are an expert food blogger writing for the 'Flavour Fusion' blog.
        Your task is to generate a detailed, engaging, unique, and well-structured recipe blog post.

        **Topic:** {topic}
        **Approximate Word Count:** {word_count} words

        **Instructions:**
        1.  **Title:** Create a catchy and relevant title for the blog post.
        2.  **Introduction:** Write a brief, enticing introduction about the recipe, perhaps its origin, why it's special, or who it's perfect for.
        3.  **Ingredients:** Provide a clear list of ingredients with precise quantities (e.g., cups, grams, tbsp).
        4.  **Instructions:** Give step-by-step preparation and cooking instructions. Make them easy to follow. Use clear action verbs.
        5.  **Tips/Variations (Optional but recommended):** Include a small section with helpful tips, serving suggestions, or possible variations (e.g., making it vegan, gluten-free, spicier).
        6.  **Conclusion:** A short concluding remark.
        7.  **Tone:** Write in a friendly, approachable, and enthusiastic tone suitable for a food blog.
        8.  **Length:** Ensure the total content is close to the requested {word_count} words.
        9.  **Formatting:** Use Markdown for structure (like headings ##, lists *, bold **).

        **Generate the blog post now:**
        """

        response = model.generate_content(prompt)

        # Safer check for response content
        try:
            # Accessing text directly is usually fine for simple generation
            return response.text
        except ValueError:
             # If the response was blocked (often raises ValueError)
             # Access safety ratings and blocked reason if needed
             reason = "Unknown"
             try:
                 reason = response.prompt_feedback.block_reason.name
             except AttributeError:
                 pass # No block reason available
             st.warning(f"Content generation potentially blocked. Reason: {reason}")
             # Check if parts exist even if blocked (sometimes partial content is there)
             if response.parts:
                 return f"Warning: Content generation issue (Reason: {reason}). Partial content (if any): {response.parts[0].text}"
             else:
                 return f"Error: Content generation failed or was blocked (Reason: {reason}). No content available."
        except Exception as inner_e:
            # Catch other potential issues accessing response parts/text
            return f"Error: Could not parse the response content. Details: {inner_e}"


    except Exception as e:
        # Improved error handling
        st.error(f"An error occurred during API call or processing: {e}")
        error_message = f"Error: An unexpected error occurred during generation. Details: {e}"
        if "API key not valid" in str(e):
             error_message = "Error: The provided Google API Key is invalid. Please check and try again."
        elif "permission" in str(e).lower():
             error_message = "Error: API key valid, but might lack permissions for the Gemini API. Please check your Google Cloud Project settings."
        elif "404" in str(e) and "models/" in str(e):
             error_message = f"Error: Model '{model_name}' not found or inaccessible with your API key/region. Try alternatives like 'gemini-1.0-pro' or check available models in Google AI Studio. Original error: {e}"
        # Add more specific checks if needed
        return error_message

# --- Streamlit App Interface ---

st.title("🍲 Flavour Fusion: AI-Driven Recipe Blogging 🧑‍🍳")
st.markdown("Generate unique recipe blog posts using Google's Generative AI. Just provide a topic and desired word count!")

# --- API Key Input ---
api_key = st.text_input("Enter your Google API Key:", type="password", help="Get your key from Google AI Studio.")

# --- User Inputs ---
recipe_topic = st.text_input("Enter the Recipe Topic (e.g., 'Vegan Chocolate Cake', 'Quick Weeknight Pasta', 'Spicy Thai Green Curry'):")
word_count = st.number_input("Desired Word Count (approximate):", min_value=150, max_value=3000, value=600, step=50)

# --- Generate Button ---
generate_button = st.button("✨ Generate Recipe Blog ✨")

# --- Output Area ---
if generate_button:
    if not api_key:
        st.warning("Please enter your Google API Key.")
    elif not recipe_topic:
        st.warning("Please enter a recipe topic.")
    else:
        with st.spinner(f"🧑‍🍳 Generating a delicious blog post on '{recipe_topic}'... This might take a moment..."):
            # Call the generation function
            blog_content = generate_recipe_blog(api_key, recipe_topic, word_count)

            # Display the result
            st.subheader("Generated Recipe Blog Post:")
            if blog_content and blog_content.startswith(("Error:", "Warning:")):
                # Show errors/warnings using appropriate Streamlit elements
                if blog_content.startswith("Error:"):
                    st.error(blog_content)
                else:
                    st.warning(blog_content)
            elif blog_content:
                st.markdown(blog_content) # Use markdown to render formatting
            else:
                st.error("Error: Received empty content from the API.")


# --- Footer ---
st.markdown("---")
st.caption("Powered by Google Generative AI & Streamlit")