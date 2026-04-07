# MyBlog
## Description
The application is a platform for blogging, where users can create, edit, and delete their own posts, leave comments on blogs, reply to other users' comments, add categories and photos to their blogs if desired, and search for blogs by category name.

A flexible access control system using RBAC (role-based access control) is implemented. The system supports user roles such as Administrator and Guest. A Guest can create, edit, and delete their own blogs, view other users' blogs, write comments, and delete only their own comments. Users can attach photos to their blogs. The Administrator has extended capabilities, such as deleting any blog or any user's comment.

## Name
**MyBlog** – this name reflects the platform's purpose and the core idea of the service: maintaining one's own blog.

## Subject Area
The application is designed for creating and managing blogs. It targets users who wish to maintain personal blogs or manage thematic articles. The system supports content and role administration, as well as blog classification by categories for better organization and navigation. A comment hierarchy is implemented. The main system entities include blogs, comments, categories, and users.

## Data
### User:
* Name (required, unique)
* Email (required, unique)
* Password (required, hashed)
* Role (admin, guest, default value – guest)

To register, you fill in all this data to create an account. To log into an account, you need to authenticate using your email and password.
After logging in, you can create, edit, view, and delete blogs.

### Blogs:
To create a blog, you need to specify:
* Blog title (required, max 255 characters)
* Blog content (required)
* Blog category (optional)
* Blog photo (optional)

To delete, edit, or retrieve a specific blog, simply enter the blog ID.
To attach a photo, you only need to specify the photo ID. A user can only attach photos they have uploaded themselves.
Blogs can be sorted by text size and the number of comments on them.
Comments can be left on created blogs, deleted, and all comments under a specific blog can be viewed.

### Comments
To create a comment, you need to specify:
* Blog ID
* Content of the comment
* Parent comment ID (if you want to reply to someone else's comment)

To view all comments under a blog, you need to specify the blog ID.
To delete a comment, you need to specify the comment ID.
To moderate a comment, you need to specify the comment ID and change the moderation flag.

### Categories
As mentioned earlier, we can optionally specify categories when creating a blog, but besides that, we can add categories ourselves and view the entire existing unique list.
There is a possibility to search for blogs by category name. To do this, we need to enter a category name from the list of categories, and we will get all blogs associated with that name.

# Constraints for each data element:
* Blog title – maximum 255 characters
* Blog content – minimum 1 character and maximum 20000
* Category name – maximum 100 characters
* Number of categories that can be specified for a blog – no more than 5
* Number of photos that can be attached – 1
* Images must be in .jpg and .png format; if files of another format are selected, an error will be displayed: "Failed to upload photo: An error occurred while uploading the photo."
* Email must conform to the email format
* Comment content – minimum 1 character
* Password – must be at least 6 characters long, contain at least one uppercase and one lowercase letter; otherwise, the message is displayed: "Password must be at least 6 characters long and contain at least one digit and one uppercase letter."
* Username must be unique; otherwise, the message is displayed: "The name is taken. Choose another one."
* Email must be unique and valid; otherwise, the message is displayed: "Email already registered"

# General Integrity Constraints
* Data validation
* Access restrictions for different roles

# User Roles
There are two roles within the service:
* Guest: creating blogs, updating and deleting their own posts, viewing all blogs, finding a blog by blog ID, leaving and deleting comments, replying to other comments, viewing moderated comments under a specific blog (by blog ID), retrieving blogs by category name, adding to the category list and viewing it, creating their own user, retrieving a user by ID and deleting their own user, retrieving a sorted list of blogs by blog length and the number of moderated comments, uploading photos, viewing a photo by photo ID, attaching a photo to a blog (if the blog has no photo), creating a blog with a photo, viewing the photo attached to a blog, viewing a list of all photos uploaded by the user.
* Administrator: has extended capabilities, such as deleting any user's blog and deleting any comment, moderating comments, viewing all users and deleting them, retrieving a sorted list of blogs by the total number of all comments.
* Moderator: after a user sends a message, the moderator views it -> moderates it -> after successful moderation, the comment becomes available to everyone or is deleted.

When sorting blogs by the number of comments, the moderator and admin see the total number of all comments (moderated/unmoderated), while the guest sees only the number of moderated comments.

# API
REST API for data management (create, edit, delete) of blogs, comments, and categories.
Swagger API documentation for the project is located at the path docs/, where all available endpoints, possible requests, parameters, and responses for each operation are described.

# Development Technologies
* **FastAPI** — API creation and routing.
* **SQLAlchemy** — ORM for database interaction.
* **OAuth2** — user authentication management.
* **Passlib** — password hashing.
* **JWT (JSON Web Tokens)** — authentication token management.
* **Docker** — containerization and application deployment tool.
* **Pydantic** — for data validation and schema creation.
* **unittest** — for writing tests.
* **alembic** — for migrations.

# Database Schema

![image](![Untitled (6)](https://github.com/user-attachments/assets/9171ff1c-5923-4207-aea1-72ed3bf98c18))

# Programming Language
* Python 3.12.6

# Database Management System (DBMS)
* PostgreSQL

# Tests
The tests are located in the `test` folder, and to run them you need to:
   ```bash
   export PYTHONPATH=.
   pytest
or:
   ```bash
   make tests
   ```
# Instructions for running the application

1. **Preliminarily install Docker** for your system.

2. **Clone the repository:**:

   ```bash
   git clone <Repository_URL>
   cd <repository_folder_name>
   ```

3. **Create and activate a virtual environment:**:

   - **For Mac or Linux**:
     ```bash
     python3 -m venv env
     source env/bin/activate
     ```

   - **For Windows**:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```

4. **Build and run the containers**:

   ```bash
   make run-docker
   ```

5. **Apply migrations**:

   ```bash
   make run-migration
   ```

6. **Access the application**:

   After successfully applying the migrations, the application will be available at: [http://localhost:8000](http://localhost:8000).

7. **Stop the containers and remove the created images**:

   ```bash
   make stop-docker
