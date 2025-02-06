terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 2.13"
    }
  }
}

provider "docker" {}

resource "docker_volume" "minio_data" {}
resource "docker_volume" "postgres_data" {}

resource "docker_container" "minio" {
  image = "minio/minio:latest"
  name  = "minio"
  env = [
    "MINIO_ACCESS_KEY=minioadmin",
    "MINIO_SECRET_KEY=minioadmin",
    "MINIO_STORAGE_USE_HTTPS=False"
  ]
  command = ["server", "/data", "--console-address", ":9001"]

  ports {
    internal = 9000
    external = 9000
  }
  ports {
    internal = 9001
    external = 9001
  }
  volumes {
    volume_name    = docker_volume.minio_data.name
    container_path = "/data"
  }
  networks_advanced {
    name = docker_network.spark_minio_network.name
  }
}

resource "docker_container" "spark_master" {
  image = "bitnami/spark:latest"
  name  = "spark-master-minio-iceberg"
  env = [
    "SPARK_LOCAL_IP=localhost",
    "SPARK_MODE=master",
    "SPARK_SUBMIT_ARGS=--packages org.apache.iceberg:iceberg-spark3-runtime:0.12.0 --conf spark.driver.host=localhost --conf spark.driver.port=7078"
  ]
  ports {
    internal = 7077
    external = 7077
  }
  ports {
    internal = 7078
    external = 7078
  }
  networks_advanced {
    name = docker_network.spark_minio_network.name
  }
}

resource "docker_container" "spark_worker" {
  image = "bitnami/spark:latest"
  name  = "spark-worker-minio-iceberg"
  env = [
    "SPARK_LOCAL_IP=localhost",
    "SPARK_MASTER_URL=spark://spark-master-minio-iceberg:7077",
    "SPARK_MODE=worker",
    "SPARK_SUBMIT_ARGS=--packages org.apache.iceberg:iceberg-spark3-runtime:0.12.0"
  ]
  depends_on = [
    docker_container.spark_master
  ]
  ports {
    internal = 8081
    external = 8081
  }
  networks_advanced {
    name = docker_network.spark_minio_network.name
  }
}

resource "docker_container" "postgres" {
  image = "postgres:latest"
  name  = "postgres"
  env = [
    "POSTGRES_USER=postgres",
    "POSTGRES_PASSWORD=postgres",
    "POSTGRES_DB=mydatabase",
    "PGPORT=5433"
  ]
  ports {
    internal = 5433
    external = 5433
  }
  volumes {
    volume_name    = docker_volume.postgres_data.name
    container_path = "/var/lib/postgresql/data"
  }
  networks_advanced {
    name = docker_network.spark_minio_network.name
  }
}

resource "docker_network" "spark_minio_network" {
  name = "spark_minio_network"
}
