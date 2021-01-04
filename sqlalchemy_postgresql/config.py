# Scheme: "postgres+psycopg2://<USERNAME>:<PASSWORD>@<IP_ADDRESS>:<PORT>/<DATABASE_NAME>"
DATABASE_URI = 'postgres+psycopg2://bongdaxanh_user:SF9HIxMahuMY9k8@localhost:5432/bongdaxanh_db'
# DATABASE_URI = 'postgres+psycopg2://postgres:1@localhost:5432/bongdaxanh_db'

try:
    from sqlalchemy_postgresql.config_local import DATABASE_URI
except ImportError:
    pass
