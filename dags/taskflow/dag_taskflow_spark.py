from airflow.decorators import dag, task
from datetime import datetime
from pyspark import SparkContext
from pyspark.sql import SparkSession
import pandas as pd


@dag(
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    doc_md=__doc__,
    default_args={"owner": "Astro", "retries": 3},
    tags=["python", "taskflow"],
)
def dag_taskflow_pyspark():
    @task.pyspark(conn_id="spark_default")
    def spark_task(spark: SparkSession, sc: SparkContext) -> pd.DataFrame:

        df = spark.createDataFrame(
            [
                (1, "John Doe", 21),
                (2, "Jane Doe", 22),
                (3, "Joe Bloggs", 23),
            ],
            ["id", "name", "age"],
        )
        df.show()

        return df.toPandas()

    spark_task()


dag_taskflow_pyspark()
