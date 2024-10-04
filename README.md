# LMNH Botanical Pipeline

## Background

This project is being developed to support the Liverpool Natural History Museum (LNMH) in its efforts to monitor the health of the plants in its newly opened botanical wing. LNMH has been a well-known destination for showcasing the natural history of the region, including fossils, wildlife, and marine life. In response to the increasing interest in botanical science, the museum introduced a botanical wing in 2023, which features diverse plant species and highlights their importance in the ecosystem. This new wing is designed to attract visitors from various backgrounds, such as families, students, and researchers, while also raising awareness of plant conservation efforts.

One of the main attractions of this new wing is the large conservatory, which houses a wide variety of plants from different regions around the world. However, maintaining the health of these plants has become a challenge for the museum's team of gardeners due to the complexity and sheer number of species that require different environmental conditions. To address this, the museum is seeking a solution that will allow them to monitor the plants' health in real-time and proactively alert the gardening staff when a plant requires attention.

### Problem Statement

LNMH has deployed an array of sensors connected to Raspberry Pi devices to monitor key environmental factors for each plant, such as soil moisture, temperature, humidity, and light intensity. These sensors currently report data through a basic API endpoint in real-time. While this allows for momentary monitoring, the museum needs a more comprehensive system that can track plant health trends over time and provide alerts for potential issues.

### Project Goal

This project aims to create a robust data pipeline that extracts sensor data from the museum's plant monitoring API every minute using AWS Lambda. The collected data will be stored in an AWS RDS (Relational Database Service) instance for short-term storage (up to 24 hours) and will then be archived in an Amazon S3 bucket for long-term storage.

Additionally, stakeholders will have access to both the short-term and long-term data through a Streamlit dashboard. This dashboard will provide real-time and historical visualisations of plant health metrics, enabling better monitoring and decision-making for plant maintenance and research.

The system will:

- Collect sensor data every minute using AWS Lambda.
- Store the last 24 hours of data in RDS for easy querying.
- Automatically archive older data to an S3 bucket for cost-efficient long-term storage.
- Provide stakeholders with an intuitive dashboard for visualising plant health data over time.

## Installation and Setup

This project consists of multiple components, each located in a separate subfolder. To set up the project correctly, you will need to follow the specific installation instructions provided in the README.md file within each subfolder.

1. **Navigate to each subfolder:** Each component of the project is organized into its own directory. Make sure to visit each subfolder to set up the necessary environment, dependencies, and configurations.

2. **Read the README.md file:** In each subfolder, you will find a README.md file with detailed instructions on how to install and configure that particular component. Follow the steps in the respective README.md to complete the setup.

3. **Install dependencies:** Some components may require additional libraries or tools. Ensure you run the appropriate commands, such as pip install -r requirements.txt or other installation steps, as instructed in the subfolder's README.md.

4. **Environment Configuration:** If environment variables or configurations are required, they will be specified in the corresponding README.md files. Make sure to configure those settings correctly.

5. **Run the Project:** After following the setup instructions in all necessary subfolders, the project will be ready to run. Refer to the top-level README.md or subfolder-specific instructions for details on running the project.