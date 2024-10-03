"""Dashboard 'About' page."""

import streamlit as st

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    st.markdown("<h1 style='color: #e3298c;'>🌱 About Us 🌱</h1>",
                unsafe_allow_html=True)
    
    st.write("""
    **Liverpool Museum of Natural History (LMNH)** is at the forefront of botanical science, dedicated to conserving and showcasing the incredible 
    diversity of plant life. With the opening of our new botanical wing, we are excited to share the wonders of the plant world with visitors and researchers alike.
    
    Our conservatory houses a wide variety of plants from around the world, each of which contributes to a dynamic ecosystem that we work hard to maintain.
    In our efforts to preserve these plants, we have integrated cutting-edge technology to monitor their health in real-time.
    """)

    st.image("https://dsmmagazine.com/wp-content/uploads/2020/10/conservatory_sipandstroll-1536x1028.jpg",
            caption="Liverpool Natural History Museum's Conservatory", width=500)

    st.subheader("Our Plant Monitoring Initiative")
    st.write("""
        The LMNH plant health monitoring project is designed to give our team of botanists and gardeners detailed insights into the health and well-being of 
        each plant in our conservatory. With sensors placed throughout the space, we track essential environmental factors such as soil moisture, temperature, 
        humidity, and more.

        This data is collected and processed continuously, ensuring that our team can address any issues promptly to keep the plants thriving.
        """)

    st.subheader("Real-Time Data & Visualisations")
    st.write("""
        Our interactive data dashboard, built using Streamlit, allows both stakeholders and the museum's gardening team to monitor the short-term and long-term health 
        of our plants. With visualisations tracking trends and highlighting any potential risks, our goal is to make plant care as efficient and effective as possible.

        The dashboard leverages AWS infrastructure to ensure reliable data storage and retrieval, with short-term data stored in an RDS instance and long-term data 
        archived in an S3 bucket.
        """)

    st.subheader("Commitment to Plant Conservation")
    st.write("""
        At LNHM, we believe that preserving plant life is critical to maintaining biodiversity. Through this project, we are not only safeguarding the health of 
        the plants in our conservatory but also contributing to ongoing research in plant conservation and care.

        We are committed to using technology in a way that supports our mission of education, preservation, and sustainability.
        """)

    st.subheader("Contact Us")
    st.write("""
        If you'd like to learn more about our plant monitoring initiative or collaborate with us on future projects, don't hesitate to reach out!

        - **Website**: [www.lmnh.co.uk](https://www.lmnh.co.uk)
        - **Phone**: 0151 555 5555
        - **Address**: Liverpool Natural History Museum, 123 Plant Conservatory Lane, Liverpool, UK
        """)
