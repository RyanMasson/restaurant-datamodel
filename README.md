# restaurant-datamodel

This is the codebase for my portfolio project "Building a Dimensional Data Model with Snowflake and dbt for Restaurant Cost Control", which can be found on my website https://ryanmasson.carrd.co/

This repository contains four parts:

- A dimensional model schema rendered on dbdiagram.io using DBML code
- The generation of mock operational data from a restaurant business
- The setup of a Snowflake environment with the mock data loaded into a data warehouse called "raw"
- The building of the dimensional model in a different warehouse called "analytics" using dbt
- A SQL file monthly_cogs_query.sql to demonstrate a business use case of querying the analytics warehouse

Acknowledgment: I used Claude (Sonnet 5) in developing the scripts used in this project. 
