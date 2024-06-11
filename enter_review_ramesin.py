Skip to content
Navigation Menu
iniperusahaanbaru
/
reviewramesin

Type / to search

Code
Issues
Pull requests
Actions
Projects
Wiki
Security
Insights
Settings
Editing enter_review_ramesin.py in reviewramesin
Breadcrumbsreviewramesin
/
enter_review_ramesin.py
in
main

Edit

Preview
Indent mode

Spaces
Indent size

4
Line wrap mode

No wrap
Editing enter_review_ramesin.py file contents
Selection deleted
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
99
100
101
102
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

    
if __name__ == "__main__":
    main()

Use Control + Shift + m to toggle the tab key moving focus. Alternatively, use esc then tab to move to the next interactive element on the page.
Editing reviewramesin/enter_review_ramesin.py at main · iniperusahaanbaru/reviewramesin
