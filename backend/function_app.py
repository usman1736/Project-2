import azure.functions as func
import logging
import csv
import json
import os
import time

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="analyze")
def analyze(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    start_time = time.time()

    csv_path = os.path.join(os.path.dirname(__file__), "All_Diets.csv")

    averages = {}

    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            diet_type = row["Diet_type"]

            if diet_type not in averages:
                averages[diet_type] = {
                    "Protein": 0.0,
                    "Carbs": 0.0,
                    "Fat": 0.0,
                    "count": 0
                }

            averages[diet_type]["Protein"] += float(row["Protein(g)"])
            averages[diet_type]["Carbs"] += float(row["Carbs(g)"])
            averages[diet_type]["Fat"] += float(row["Fat(g)"])
            averages[diet_type]["count"] += 1

    for diet in averages:
        count = averages[diet]["count"]
        averages[diet]["Protein"] = round(averages[diet]["Protein"] / count, 2)
        averages[diet]["Carbs"] = round(averages[diet]["Carbs"] / count, 2)
        averages[diet]["Fat"] = round(averages[diet]["Fat"] / count, 2)
        del averages[diet]["count"]

    labels = list(averages.keys())
    protein = [averages[diet]["Protein"] for diet in labels]
    carbs = [averages[diet]["Carbs"] for diet in labels]
    fat = [averages[diet]["Fat"] for diet in labels]

    execution_time_ms = int((time.time() - start_time) * 1000)

    result = {
        "macrosByDiet": {
            "labels": labels,
            "protein": protein,
            "carbs": carbs,
            "fat": fat
        },
        "executionTimeMs": execution_time_ms
    }

    return func.HttpResponse(
        json.dumps(result),
        mimetype="application/json",
        status_code=200
    )