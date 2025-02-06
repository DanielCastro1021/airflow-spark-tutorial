from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from pyspark.sql import SparkSession
from minio import Minio
import logging

minio_bucket = "my-first-bucket"
source_file = '/usr/local/airflow/include/data/Electric_Vehicle_Population_Data.csv'
destination_file = 'data.csv'

iceberg_table_location = f"s3a://{minio_bucket}/iceberg_data/default"

client = Minio("host.docker.internal:9000", access_key="minioadmin",
               secret_key="minioadmin", secure=False)

iceberg_builder = SparkSession.builder \
    .appName("iceberg-spark-minio-example") \
    .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.0,org.apache.iceberg:iceberg-hive-runtime:1.5.0") \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.spark_catalog.type", "hadoop") \
    .config("spark.sql.catalog.spark_catalog.warehouse", f"s3a://{minio_bucket}/iceberg_data/") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://host.docker.internal:9000") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .enableHiveSupport()


def create_bucket_if_not_exists():
    try:
        if not client.bucket_exists(minio_bucket):
            client.make_bucket(minio_bucket)
            logging.info("Bucket created successfully.")
        else:
            logging.info("Bucket already exists.")
    except Exception as e:
        logging.error(f"Error checking or creating bucket: {e}")
        raise


def upload_file():
    try:
        found = client.stat_object(minio_bucket, destination_file)
        if found:
            logging.info("File already exists in the bucket.")
        else:
            logging.info("Uploading file...")
            client.fput_object(minio_bucket, destination_file, source_file)
            logging.info("File uploaded successfully.")
    except Exception as e:
        if e.code == 'NoSuchKey':
            logging.info("Uploading file...")
            client.fput_object(minio_bucket, destination_file, source_file)
            logging.info("File uploaded successfully.")
        else:
            logging.error(f"Error uploading file: {e}")
            raise


def spark_iceberg_job():
    iceberg_spark = iceberg_builder.getOrCreate()
    try:
        df = iceberg_spark.read.format('csv').option(
            'header', 'true').option('inferSchema', 'true').load(source_file)

        df.write.format("iceberg").mode(
            "append").saveAsTable("iceberg_table_name")

        iceberg_df = iceberg_spark.read.format("iceberg").load(
            f"{iceberg_table_location}/iceberg_table_name")

        logging.info("Schema of the Iceberg table:")
        iceberg_df.printSchema()

        logging.info("Data in the Iceberg table:")
        iceberg_df.show()
    except Exception as e:
        logging.error(f"Error running Spark job: {e}")
        raise


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
    'dag_spark_iceberg_s3',
    default_args=default_args,
    schedule=None,
    catchup=False,
    tags=["python", "spark", "iceberg", "s3"],
)

create_bucket_if_not_exists_task = PythonOperator(
    task_id='create_bucket_if_not_exists',
    python_callable=create_bucket_if_not_exists,
    dag=dag,
)

upload_file_task = PythonOperator(
    task_id='upload_file',
    python_callable=upload_file,
    dag=dag,
)

spark_iceberg_job_task = PythonOperator(
    task_id='spark_iceberg_job',
    python_callable=spark_iceberg_job,
    dag=dag,
)


create_bucket_if_not_exists_task >> upload_file_task >> spark_iceberg_job_task
