from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor

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
    dag_id='dag_s3_sensor',
    default_args=default_args,
    description='A DAG to demonstrate the S3 Sensor',
    schedule_interval="@daily",
    catchup=False,
    tags=["python", "s3"],
)

s3_sensor = S3KeySensor(
    task_id='s3_sensor_task',
    bucket_name='airflow',
    bucket_key='users.csv',
    aws_conn_id='aws_default',
    wildcard_match=True,
    timeout=18*60*60,
    poke_interval=60,
    mode='poke',
    dag=dag,
)

s3_sensor
