from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator


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
    dag_id='dag_xcom',
    default_args=default_args,
    description='XCom DAG',
    schedule="@daily",
    catchup=False,
    tags=["python"],
)


def get_name_v1():
    return "John"


def get_name_v2(ti):
    ti.xcom_push(key='first_name', value='John')
    ti.xcom_push(key='last_name', value='Doe')


def get_age_v1():
    return 30


def get_age_v2(ti):
    ti.xcom_push(key='age', value=30)


def greet_v1(ti):
    name = ti.xcom_pull(task_ids='get_name_v1')
    age = ti.xcom_pull(task_ids='get_age_v1')
    return f"Hello {name}, you are {age} years old!"


def greet_v2(ti):
    first_name = ti.xcom_pull(task_ids='get_name_v2', key='first_name')
    last_name = ti.xcom_pull(task_ids='get_name_v2', key='last_name')
    age = ti.xcom_pull(task_ids='get_age_v2', key='age')
    return f"Hello {first_name} {last_name}, you are {age} years old!"


get_name_task_v1 = PythonOperator(
    task_id='get_name_v1',
    python_callable=get_name_v1,
    dag=dag,
)

get_age_task_v1 = PythonOperator(
    task_id='get_age_v1',
    python_callable=get_age_v1,
    dag=dag,
)

greet_task_v1 = PythonOperator(
    task_id='greet_v1',
    python_callable=greet_v1,
    dag=dag,
)

get_name_task_v2 = PythonOperator(
    task_id='get_name_v2',
    python_callable=get_name_v2,
    dag=dag,
)

get_age_task_v2 = PythonOperator(
    task_id='get_age_v2',
    python_callable=get_age_v2,
    dag=dag,
)

greet_task_v2 = PythonOperator(
    task_id='greet_v2',
    python_callable=greet_v2,
    dag=dag,
)


[get_name_task_v1, get_age_task_v1] >> greet_task_v1
[get_name_task_v2, get_age_task_v2] >> greet_task_v2
