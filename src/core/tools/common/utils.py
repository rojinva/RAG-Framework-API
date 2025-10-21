import csv
from io import StringIO

from dotenv import load_dotenv
load_dotenv(override=True)


def convert_csv_to_markdown_table(csv_text, columns=None):
    # Create a StringIO object to read the CSV text
    csv_file = StringIO(csv_text)
    reader = csv.DictReader(csv_file)

    # Clean the column names by stripping whitespace
    reader.fieldnames = [field.strip() for field in reader.fieldnames]

    # If columns_to_keep is not provided, use all columns from the CSV
    if columns is None:
        columns = reader.fieldnames

    # Prepare the header for the Markdown table
    markdown_table = f"| {' | '.join(columns)} |\n"
    markdown_table += f"| {' | '.join(['-' * len(col) for col in columns])} |\n"

    # Process each row in the CSV
    for row in reader:
        row_data = []
        for col in columns:
            row_data.append(row[col])

        # Add the row to the Markdown table
        markdown_table += f"| {' | '.join(row_data)} |\n"

    return markdown_table
