import streamlit as st
from google.cloud import storage, firestore
from google.oauth2 import service_account
import datetime

# Google Cloud configuration
BUCKET_NAME = "fotorestoran"
FIRESTORE_COLLECTION = "reviews"

# Initialize Google Cloud clients using environment variables
credentials_dict = {
    'type': st.secrets['GOOGLE_CREDENTIALS_JSON']['type'],
    'project_id': st.secrets['GOOGLE_CREDENTIALS_JSON']['project_id'],
    'private_key_id': st.secrets['GOOGLE_CREDENTIALS_JSON']['private_key_id'],
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
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(image_content.getvalue(), content_type="image/jpeg")
    
    url = blob.generate_signed_url(
        expiration=datetime.timedelta(hours=1),
        method='GET',
        version="v4",
    )
    return url

def store_review_in_firestore(review_text, image_url, reviewer_name, rating):
    doc_ref = firestore_db.collection(FIRESTORE_COLLECTION).document()
    doc_ref.set({
        "review_text": review_text,
        "image_url": image_url,
        "timestamp": firestore.SERVER_TIMESTAMP,
        "restoran_name": "Restoran Tes",
        "reviewer_name": reviewer_name,
        "rating": rating
    })

def show_submission_form():
    with st.form(key='review_form'):
        order_id = st.text_input("Enter your order ID", help="Enter the order ID associated with your meal.")
        image = st.camera_input("Capture or upload a picture of your meal", help="Use your camera to take a picture of the meal or upload an image.")
        review_text = st.text_area("Enter your review", help="Write your review about the meal and your experience.")
        reviewer_name = st.text_input("Enter your name", help="Your name as the reviewer.")
        rating = st.slider("Rating", 1, 5, 5, help="Your rating of the meal from 1 to 5.")
        submit_button = st.form_submit_button(label='Submit Review')
        return submit_button, order_id, image, review_text, reviewer_name, rating

def main():
    st.title('Masukan Review Untuk Tes123 :-)')
    
    if 'show_result' not in st.session_state:
        st.session_state['show_result'] = False

    if not st.session_state.show_result:
        submit_button, order_id, image, review_text, reviewer_name, rating = show_submission_form()
    
        if submit_button:
            if order_id.lower() == "tes123" and image is not None and review_text and reviewer_name and rating:
                destination_blob_name = f"reviews/{order_id}/{datetime.datetime.now().isoformat()}.jpg"
                image_url = upload_image_to_gcs(image, destination_blob_name)
                
                store_review_in_firestore(review_text, image_url, reviewer_name, rating)
                
                st.session_state.show_result = True
                st.session_state.submitted_image = image
                st.session_state.submitted_review = review_text
                
                st.rerun()
            else:
                st.error("Invalid order ID. Please check and try again.")
        st.markdown("Klik disini untuk liat review nya! [Review Ramesindong](https://reviewbookramesindong.streamlit.app/)")
    else:
        st.success("Your review has been sent!")
        st.markdown("Klik disini untuk liat review nya! [Review Ramesindong](https://reviewbookramesindong.streamlit.app/)")
        if st.button("See Review"):
            # Redirect to the provided URL
            js = "window.location.href = 'https://reviewbookramesindong.streamlit.app/';"
            html = f'<script>{js}</script>'
            st.markdown(html, unsafe_allow_html=True)

        if st.button("Submit Another Review"):
            st.session_state.show_result = False
            st.rerun()

if __name__ == "__main__":
    main()
