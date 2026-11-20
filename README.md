# Smart Recipe Finder

Smart Recipe Finder is a Flask web application for discovering recipes from food images or a text search. It also lets users manage recipes and generate a custom recipe with Google's Gemini generative AI.

## Features

- Register and log in to the application, with a separate admin login flow.
- Upload a food image for classification with the included convolutional neural network (`final_cnn.h5`).
- Look up a recipe by name.
- Generate a recipe based on meal, calorie target, cuisine, ingredients to include, preferences, and ingredients to avoid.
- Administer recipe records: add, view, update, and delete recipes.
- Display recipe ingredients, preparation steps, images, and video links.

The image classifier recognizes these labels: burger, butter naan, chai, chapati, chole bhature, dal makhani, dhokla, fried rice, idli, jalebi, kaathi rolls, kadai paneer, kulfi, masala dosa, momos, paani puri, pakode, pav bhaji, pizza, and samosa. A matching recipe must also exist in the database for the app to show its recipe details.

## Requirements

- Python 3.9–3.11 (TensorFlow 2.15 is pinned in the supplied dependency list)
- MySQL Server
- A Google Gemini API key for recipe generation

## Setup

Run the following commands from the project directory.

1. Create and activate a virtual environment:

   ```powershell
   py -3.10 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install the project dependencies:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r libraries.txt
   ```

   `libraries.txt` is the provided pinned package list and includes packages beyond the runtime imports used by this web app.

3. Set up the database. Review `db.sql` first: it drops and recreates the `foods` database, then creates the `users` and `recipies` tables and inserts sample recipes. Run it against your MySQL server, for example:

   ```powershell
   mysql -u root -p < db.sql
   ```

   Update the MySQL connection settings in `app.py` to match your local server.

4. Configure a valid Gemini API key in the Gemini configuration in `app.py`. Keep API keys and other secrets out of source control.

5. Start the Flask application:

   ```powershell
   python app.py
   ```

6. Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Project structure

```text
.
├── app.py                 # Flask routes and application logic
├── db.sql                 # MySQL schema and sample recipe data
├── final_cnn.h5           # Trained food image classification model
├── libraries.txt          # Pinned Python package list
├── static/
│   ├── images/            # Recipe images
│   └── user_images/       # Uploaded food images
└── templates/             # Jinja HTML pages
```

## Notes

- Image uploads are saved under `static/user_images/`. The uploaded image is resized to 224 × 224 pixels before classification.
- The model predicts a food label, then the app searches the `recipies` table for a recipe with the same name. Add or rename database records as needed so their names match the model labels.
- Gemini recipe generation requires a working internet connection and a valid API key.
- The current app is intended for local demonstration. Before deployment, configure secrets securely and replace the development server settings with production-ready authentication, session handling, upload validation, and server configuration.
