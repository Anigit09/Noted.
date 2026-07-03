# Noted.
# FastAPI-based notes web app deployed on Render

Noted is a note-taking web application that allows users to create, edit, delete, and share notes with configurable permissions. Shared notes can be made either view-only or editable, enabling simple collaborative workflows.

## Features

* JWT-based authentication with dedicated endpoints for handling user registration and login.
* Mail SMTP integration to demonstrate confirmation of user email after user registration.
* Error handling to manage faults and errors on the client side.
* Connection-pooled PostgreSQL database hosted on Supabase.
* Manual implementation of offset-based pagination to handle large transfers of data as a response.
* Dedicated validation and transformation pipeline through Pydantic v2.

## Tech Stack

- **Backend:** FastAPI
- **Database:** PostgreSQL (Supabase)
- **ORM:** SQLAlchemy
- **Validation:** Pydantic v2
- **Authentication:** JWT
- **Email Service:** Mailgun SMTP
- **Deployment:** Render
- **Frontend:** HTML, CSS, JavaScript


## Architecture diagram
  
<img width="679" height="550" alt="image" src="https://github.com/user-attachments/assets/3db8c9b7-856e-4618-a7fa-097d03543384" />

## Instructions to use
* Deployed website :- https://noted-tfej.onrender.com/
* Demo Account :- example@example.com
* Password :- 12345

## API Documentation
https://noted-tfej.onrender.com/docs

