# Scheme: "postgres+psycopg2://<USERNAME>:<PASSWORD>@<IP_ADDRESS>:<PORT>/<DATABASE_NAME>"
DATABASE_URI = 'postgres+psycopg2://bongdaxanh_user:SF9HIxMahuMY9k8@localhost:5432/bongdaxanh_db'

try:
    from config_local import *
except ImportError:
    pass
