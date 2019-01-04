# Django 2 docker-compose boilerplate

The goal of this repository is to simplify the project creation process and make a common boilerplate for all new projects using Django.

## Getting started
Please follow the instructions to set up the Django project.


### Prerequisites
* Docker version 18 or higher
* Docker compose 1.20 or higher

### Installing
1. Start docker-compose by running
    ```bash
    docker-compose up -d
    ```

2. Run migrations.
    ```bash
    docker-compose exec app python manage.py migrate
    ```
    
3. Dump static files.
    ```bash
    docker-compose exec app python manage.py collectstatic --no-input
    ```


## Authors

* **Eduards Mukans** - *Initial work* - [emukans](https://github.com/emukans)


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
