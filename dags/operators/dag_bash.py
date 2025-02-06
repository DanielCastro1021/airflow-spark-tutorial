from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator


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
    'dag_bash',
    default_args=default_args,
    description='A simple bash DAG',
    schedule="@daily",
    catchup=False,
    tags=["bash"],
)

start = EmptyOperator(
    task_id='start',
    dag=dag,
)

hello_task = BashOperator(
    task_id='hello_task',
    bash_command='echo "Hello World"',
    dag=dag,
)

end = EmptyOperator(
    task_id='end',
    dag=dag,
)

start >> hello_task >> end
