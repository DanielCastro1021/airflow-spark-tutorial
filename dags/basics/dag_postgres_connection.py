from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    dag_id='dag_postgres_connection',
    default_args=default_args,
    description='A Postgres Connection DAG',
    schedule_interval="0 0 * * *",
    catchup=False,
    tags=["python", "postgres"],
)


create_table = PostgresOperator(
    task_id='create_table_task',
    sql="""
    CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL PRIMARY KEY,
        username VARCHAR NOT NULL,
        email VARCHAR NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """,
    postgres_conn_id="postgres_default",
    dag=dag,
)

populate_table = PostgresOperator(
    task_id='populate_table_task',
    sql="""
    INSERT INTO users (username, email) VALUES ('john_doe', 'email@gmail.com');
    """,
    postgres_conn_id="postgres_default",
    dag=dag,
)

create_table >> populate_table
