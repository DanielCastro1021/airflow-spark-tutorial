from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

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
    dag_id='dag_cron',
    default_args=default_args,
    description='A Cron DAG',
    schedule_interval="0 3  * * Tue",
    catchup=True,
    tags=["python"],
)


cron_task = PythonOperator(
    task_id='cron_task',
    python_callable=lambda: print("Hello, Cron!"),
    dag=dag,
)
