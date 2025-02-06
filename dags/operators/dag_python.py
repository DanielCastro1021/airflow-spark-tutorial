from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
import logging


def my_task():
    astronauts = ["Neil Armstrong", "Buzz Aldrin",
                  "Sally Ride", "Yuri Gagarin"]
    for astronaut in astronauts:
        logging.info(astronaut)


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'dag_python',
    default_args=default_args,
    description='A simple python DAG',
    schedule="@daily",
    catchup=False,
    tags=["python"],
)

start = EmptyOperator(
    task_id='start',
    dag=dag,
)

hello_task = PythonOperator(
    task_id='hello_task',
    python_callable=my_task,
    dag=dag,
)

end = EmptyOperator(
    task_id='end',
    dag=dag,
)

start >> hello_task >> end
