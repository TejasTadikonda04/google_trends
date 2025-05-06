## Project Overview:

This project utilized the google trends international dataset, which contains the weekly top 25 searched terms for international countries in a 5 year window. For this project we decided to only use the top 5 ranked searched terms for the weeks of 03/16/25 and 03/25/25. Our main priorities were to explore trends regarding search terms across intenraitonal countries and to display categorical data in away simalr to numerical data. By using docker, we were able to create containers that run the ETL process, load the data into postgresSQL, and creates a streamlit dashboard displaying the trends using the databse from postgresSQL.

## Environment Setup

Before running the project, copy the example environment file:
cp .env.sample .env


## Instructions:
In your terminal, change the directory to the folder that contains the information in this github repository. Once you are in that specific directory, simply run the command "docker-compose up --build". Once this command is entered, the etl, postgreSQL, and streamlit containers should begin running. Once all containers have run, navigate to the website "http://localhost:8501" to access the streamlit dashboard.

## Screenshot of Streamlit dashboard:
![Alt text](/streamlit_screenshot.png)
## Contributions:

Tejas Tadikonda - 

Ryan Rosario - 

Andy Rodriguez - I helped with the transformation part of the ETL process, specifically with checking if each country alligned with both their country and region code. Additionally, I assisted with the creation of the postgreSQL container.

Gabriel Gonzalez
