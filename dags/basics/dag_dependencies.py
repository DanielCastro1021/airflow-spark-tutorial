from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import logging


def get_pyspark():
    import pyspark
    logging.info(f"PySpark version: {pyspark.__version__}")


def get_pandas():
    import pandas
    logging.info(f"Pandas version: {pandas.__version__}")


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
    dag_id='dag_dependencies',
    default_args=default_args,
    description='A download dependency check DAG',
    schedule="@daily",
    catchup=False,
    tags=["python"],
)

get_pyspark = PythonOperator(
    task_id='get_pyspark',
    python_callable=get_pyspark,
    dag=dag,
)

get_pandas = PythonOperator(
    task_id='get_pandas',
    python_callable=get_pandas,
    dag=dag,
)

[get_pyspark, get_pandas]
