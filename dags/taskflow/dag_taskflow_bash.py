from airflow.decorators import dag, task
from datetime import datetime


@dag(
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    doc_md=__doc__,
    default_args={"owner": "Astro", "retries": 3},
    tags=["bash", "taskflow"],
)
def dags_taskflow_bash():
    @task
    def get_dogs():
        dog_owner_data = {
            "names": ["Trevor", "Grant", "Marcy", "Carly", "Philip"],
            "dogs": [1, 2, 2, 1, 4],
        }
        return dog_owner_data

    @task.bash
    def print_dog_needs(dog_owner_data):
        names_of_dogless_people = []
        for name, dog in zip(dog_owner_data["names"], dog_owner_data["dogs"]):
            if dog < 1:
                names_of_dogless_people.append(name)

        if names_of_dogless_people:
            if len(names_of_dogless_people) == 1:
                # this bash command is executed if only one person has no dog
                return f'echo "{names_of_dogless_people[0]} urgently needs a dog!"'
            else:
                names_of_dogless_people_str = " and ".join(
                    names_of_dogless_people)
                # this bash command is executed if more than one person has no dog
                return f'echo "{names_of_dogless_people_str} urgently need a dog!"'
        else:
            # this bash command is executed if everyone has at least one dog
            return f'echo "All good, everyone has at least one dog!"'

    print_dog_needs(dog_owner_data=get_dogs())


# Instantiate the DAG
dags_taskflow_bash()
