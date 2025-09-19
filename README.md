<h1 align="center"> API YaMDb </h1>

The **YaMDb** project collects user reviews for various works. The works themselves are not stored or provided - users cannot watch movies or listen to music directly on the platform.

Works are grouped into categories such as **Books**, **Movies**, and **Music**. The list of categories can be extended (e.g., you could add categories like "Visual Art" or "Jewelry").


## Features
- REST API backend implemented only
- User authentication implemented using JWT token with data verification and password reset via email
- Complex database relationships with cascade deletion
- Complex serialization with nested serializers 
- Data import from CSV file using custom management-command


## 🛠️ Tech Stack

![Python](https://img.shields.io/badge/Python_3.x-3776AB?logo=python&logoColor=yellow)
![Django](https://img.shields.io/badge/Django-092E20?logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF%20(Django%20REST)-8C1D40?logo=django&logoColor=white)
![SQLite](https://img.shields.io/badge/-SQLite-003B57?logo=sqlite&logoColor=white)


## How to Run the Project

1. Clone the repository and navigate into the project directory:

```bash
git clone https://github.com/bashval/api_yamdb.git
cd api_yamdb
```

2. Create and activate a virtual environment:

```bash
python3 -m venv env
source env/bin/activate
```

3. Install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

4. Apply database migrations:

```bash
python3 manage.py migrate
```

5. Run the development server:

```bash
python3 manage.py runserver
```


## Importing Fixtures from CSV

The project supports importing data from CSV files into the database.
To do this, use the custom Django management command:

```bash
python3 manage.py load_CSV <file_name>
```

* The filename must match the model name into which the data is being imported.
* Column names for foreign key fields must end with `_id`.

Example fixture files for all models can be found in the directory:
`api_yamdb/static/data/`


## API Documentation

Once the server is running, API documentation is available at:
[http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)


## Contributors

* [Valentin Bashkatov](https://github.com/bashval)
* [Sergey Oleynikov](https://github.com/Sergey-Anatoli4)
* [Sanzhar Serik](https://github.com/S4nzh4r)
