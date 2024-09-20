import json
import csv
from tqdm import tqdm

def convert_to_csv(json_file, csv_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        for year, reports in data.items():
            for link, report_list in tqdm(reports.items()):
                for report in report_list:
                    date_time, text = report
                    writer.writerow([year, link, date_time, text])

convert_to_csv("pool_reports_2020.json", "pool_reports.csv")