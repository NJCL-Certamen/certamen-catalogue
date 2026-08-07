# Database Script

This script is intended to help someone who has cloned this project to convert the *Certamen* question yaml files contained therein to rows in a database. This is intended to be engine agnostic and work for any SQL database, but it's possible some tweaks may be necessary; you may also choose to tweak the provided schema to your needs, in which case you will likely need to tweak the python script as well.

## Running the Script

From **the root folder** of the project run the following command `/bin/python3 scripts/db/v1/import_questions.py` (your python executable may vary). If you get an error about 'yaml' not being a module you may need to install pyyaml (`pip install pyyaml`)

### DB Parameters

You will need to pass some or all of the following parameters in order for the script to access your database. These parameters can be passed as arguments to the script or set as environment variables

| Param             | Command Line Flag   | Environment Variable    |
|-------------------|---------------------|-------------------------|
| Host              | `--host`            | `CERTAMEN_SQL_HOST`     |
| Port              | `--port`            | `CERTAMEN_SQL_PORT`     |
| Socket (optional) | `--socket`          | `CERTAMEN_SQL_SOCKET`   |
| User              | `--user`            | `CERTAMEN_SQL_USER`     |
| Database          | `--database`        | `CERTAMEN_SQL_DATABASE` |
| Password          | `--password`        | `CERTAMEN_SQL_PASSWORD` |

## Contents

### V1 Folder

As we continue the project of cataloging *Certamen* questions, it is possible if not likely that the structure of the round files will change and with them the database schema and the script for inserting the questions into it. With each new change a new version folder will be created with a new script and a guide for converting from the old version of the schema to the new.

### schema.sql

This file contains the structure of the database and will need to be applied to your database before running the script

### drop_schema.sql

This file is used for deleting the whole schema if you want to clean up or start over

### import_questions.py

The main python script file. This script iterates through all the files and folders within the question folder in order to get all the question files to feed to the other script

### import_yaml_to_db.py

This file has the functions to read a single yaml file and insert the contents into the database. If you want to tweak the schema, you'll need to tweak this file as well so that the data is inserted correctly.
