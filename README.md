## Project Overview:

This project utilized the google trends international dataset, which contains the weekly top 25 searched terms for international countries in a 5 year window. For this project we decided to only use the top 5 ranked searched terms for the weeks of 03/16/25 and 03/25/25. Our main priorities were to explore trends regarding search terms across intenraitonal countries and to display categorical data in away simalr to numerical data. By using docker, we were able to create containers that run the ETL process, load the data into postgresSQL, and creates a streamlit dashboard displaying the trends using the databse from postgresSQL.


## Instructions:
To run the project, first clone the repository by executing `git clone https://github.com/TejasTadikonda04/google_trends` in your terminal. After cloning, navigate into the project directory using `cd google_trends`. Once inside, create a copy of the environment configuration by running `cp .env.sample .env`. This will generate a `.env` file containing the default environment variables required by Docker. Next, run `docker-compose up --build` to build and launch all services: the ETL pipeline, PostgreSQL database, and Streamlit dashboard. Once all containers are running successfully, open your browser and go to `http://localhost:8501` to access the interactive dashboard.

## Screenshot of Streamlit Dashboard:
![Alt text](/streamlit_screenshot.png)
## Contributions:

Tejas Tadikonda - 

Ryan Rosario - I helped with the ETL process by validating whether the translated terms were translate correctly. I also created the transformation and DBSCAN algorithm to create collections of similar words to use for the top countries by term visualization.

Andy Rodriguez - I helped with the transformation part of the ETL process, specifically with checking if each country alligned with both their country and region code. Additionally, I assisted with the creation of the postgreSQL container.

Gabriel Gonzalez - I worked on the transformation/cleaning, loading the cleaned dataset into postgres, the streamlit app, and tweaking code to make it Docker friendly. 
