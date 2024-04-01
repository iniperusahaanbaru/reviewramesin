import streamlit as st
from google.cloud import storage, firestore
from google.oauth2 import service_account
import json
import io
import datetime
import copy


# Google Cloud configuration
BUCKET_NAME = "fotorestoran"
FIRESTORE_COLLECTION = "reviews"

# Initialize Google Cloud clients using environment variables
credentials_dict = {
    'type': st.secrets['GOOGLE_CREDENTIALS_JSON']['type'],
    'project_id': st.secrets['GOOGLE_CREDENTIALS_JSON']['project_id'],
    'private_key_id': st.secrets['GOOGLE_CREDENTIALS_JSON']['private_key_id'],
    # Ensure the private_key's newline characters are handled correctly
    'private_key': st.secrets['GOOGLE_CREDENTIALS_JSON']['private_key'].replace('\\n', '\n'),
    'client_email': st.secrets['GOOGLE_CREDENTIALS_JSON']['client_email'],
    'client_id': st.secrets['GOOGLE_CREDENTIALS_JSON']['client_id'],
    'auth_uri': st.secrets['GOOGLE_CREDENTIALS_JSON']['auth_uri'],
    'token_uri': st.secrets['GOOGLE_CREDENTIALS_JSON']['token_uri'],
    'auth_provider_x509_cert_url': st.secrets['GOOGLE_CREDENTIALS_JSON']['auth_provider_x509_cert_url'],
    'client_x509_cert_url': st.secrets['GOOGLE_CREDENTIALS_JSON']['client_x509_cert_url'],
}

# Create a credentials object from the service account info
credentials = service_account.Credentials.from_service_account_info(credentials_dict)

# Initialize Google Cloud clients with the credentials
storage_client = storage.Client(credentials=credentials)
firestore_db = firestore.Client(project=credentials_dict['project_id'], credentials=credentials)

def upload_image_to_gcs(image_content, destination_blob_name):
    """
    Uploads an image to Google Cloud Storage and generates a signed URL for access.
    :param image_content: The content of the image to upload.
    :param destination_blob_name: GCS blob name (path) under which to store the image.
    :return: Signed URL of the uploaded image.
    """
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(image_content.getvalue(), content_type="image/jpeg")
    
    # Generate a signed URL for the uploaded blob
    url = blob.generate_signed_url(
        expiration=datetime.timedelta(hours=1),  # URL expires in 1 hour
        method='GET',
        version="v4",
    )
    return url

def store_review_in_firestore(review_text, image_url, reviewer_name, rating):
    """
    Stores a review in Firestore.
    :param review_text: The text of the review.
    :param image_url: URL of the associated image stored in GCS.
    :param reviewer_name: Name of the reviewer.
    :param rating: The rating given by the reviewer.
    """
    doc_ref = firestore_db.collection(FIRESTORE_COLLECTION).document()
    doc_ref.set({
        "review_text": review_text,
        "image_url": image_url,
        "timestamp": firestore.SERVER_TIMESTAMP,
        "restoran_name": "Restoran Ramesin",
        "reviewer_name": reviewer_name,  # Include the reviewer's name
        "rating": rating  # Include the rating
    })

def show_submission_form():
    with st.form(key='review_form'):
        order_id = st.text_input("Enter your order ID", help="Enter the order ID associated with your meal.")
        image = st.camera_input("Capture or upload a picture of your meal", help="Use your camera to take a picture of the meal or upload an image.")
        review_text = st.text_area("Enter your review", help="Write your review about the meal and your experience.")
        reviewer_name = st.text_input("Enter your name", help="Your name as the reviewer.")  # New field for reviewer's name
        rating = st.slider("Rating", 1, 5, 5, help="Your rating of the meal from 1 to 5.")  # New field for rating
        submit_button = st.form_submit_button(label='Submit Review')
        return submit_button, order_id, image, review_text, reviewer_name, rating

def main():
    st.title('Masukan Review Untuk RAMESINDONG :-)')
    st.title('\n')
    st.title('\n')
    # Initialize 'show_result' in session state if it doesn't exist
    if 'show_result' not in st.session_state:
        st.session_state.show_result = False

    if not st.session_state.show_result:
        submit_button, order_id, image, review_text, reviewer_name, rating = show_submission_form()

        if submit_button:
            if order_id and image is not None and review_text and reviewer_name and rating and order_id == "devay123" or order_id == "Devay123" or order_id == "DEVAY123":
                # Generate a signed URL for the image uploaded to GCS
                destination_blob_name = f"reviews/{order_id}/{datetime.datetime.now().isoformat()}.jpg"
                image_url = upload_image_to_gcs(image, destination_blob_name)
                
                # Store the review in Firestore including the reviewer's name and rating
                store_review_in_firestore(review_text, image_url, reviewer_name, rating)
                
                st.session_state.show_result = True
                st.session_state.submitted_image = image
                st.session_state.submitted_review = review_text
                
                # Rerun to show the result page
                st.rerun()
            else:
                st.error("order id salah")
    else:
        # Display the result
        st.success("Review submitted successfully!")
        st.image(st.session_state.submitted_image, caption='Uploaded/Captured Meal Image', use_column_width=True)
        st.write("Your Review:", st.session_state.submitted_review)

        if st.button("Submit Another Review"):
            # Clear the session state for a new submission
            st.session_state.show_result = False
            del st.session_state['submitted_image']
            del st.session_state['submitted_review']

            # Rerun to reset the app
            st.rerun()

if __name__ == "__main__":
    main()
