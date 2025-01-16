import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
import requests
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image

# Load environment variables from .env file
load_dotenv()

# Access the API key from environment variables
API_KEY = os.getenv("HIBP_API_KEY")
BASE_URL = "https://haveibeenpwned.com/api/v3"

# Initialize the Ollama model
model = ChatOllama(model="llama3.2", base_url="http://localhost:11434")


def get_breached_data(account):
    """
    Retrieve the breach data for the given account from the HIBP API.
    """
    url = f"{BASE_URL}/breachedaccount/{account}?truncateResponse=false"
    headers = {
        "hibp-api-key": API_KEY,
        "User-Agent": "PythonApp"  # Required by HIBP API
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        print(f"No breaches found for {account}")
        return []
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []


def plot_breaches(breach_data, account):
    """
    Plot the breach data and save as an image.
    """
    if not breach_data:
        return

    df = pd.DataFrame(breach_data)
    df['DataClassesCount'] = df['DataClasses'].apply(len)

    plt.figure(figsize=(10, 6))
    plt.bar(df['Name'], df['DataClassesCount'], color='skyblue')
    plt.title(f"Breach Data for '{account}'")
    plt.xlabel("Breach Name")
    plt.ylabel("Number of Data Classes")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Save plot as an image
    plt.savefig(f"{account}_breach_data.png")
    print(f"Plot saved as '{account}_breach_data.png'")


def generate_pdf_report(df, summary, account):
    """
    Generate a detailed PDF report using ReportLab with a properly scaled table and wrapped text.
    """
    pdf_filename = f"{account}_breach_report.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title = Paragraph(f"Breach Report for {account}", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Adjust column widths to fit within the page
    max_width = 500  # Total width for the table
    column_widths = [max_width * 0.2,  # Name
                     max_width * 0.2,  # Breach Date
                     max_width * 0.2,  # Is Verified
                     max_width * 0.4]  # Data Classes

    # Prepare table data with text wrapping for 'Data Classes'
    data = [['Name', 'Breach Date', 'Verified', 'Data Classes']]
    for _, row in df.iterrows():
        data.append([
            Paragraph(row['Name'], styles['BodyText']),
            Paragraph(row['BreachDate'], styles['BodyText']),
            Paragraph(str(row['IsVerified']), styles['BodyText']),
            Paragraph(", ".join(row['DataClasses']), styles['BodyText'])  # Wrapping long text
        ])

    # Create and style the table
    table = Table(data, colWidths=column_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(table)
    elements.append(Spacer(1, 12))

    # Summary
    summary_title = Paragraph("Summary", styles['Heading2'])
    elements.append(summary_title)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(summary, styles['BodyText']))

    # Add breach data plot image
    image_path = f"{account}_breach_data.png"
    if os.path.exists(image_path):
        elements.append(Spacer(1, 12))
        elements.append(Image(image_path, width=400, height=300))

    # Build the PDF
    doc.build(elements)
    print(f"PDF report saved as '{pdf_filename}'")
def main():
    """
    Main flow of the script:
      1. Prompt user for input.
      2. Get breach data.
      3. Print the results.
      4. Plot the results.
      5. Use ChatOllama to generate a summary.
      6. Save the report.
    """
    account = ""  # Replace this with your target account
    breach_data = get_breached_data(account)

    if breach_data:
        df = pd.DataFrame(breach_data)
        print("\nBreach Data:")
        print(df[['Name', 'BreachDate', 'IsVerified', 'DataClasses']])

        # Plot the breach data
        plot_breaches(breach_data, account)

        # Generate summary using ChatOllama
        prompt = (
            f"Below is the JSON breach data for '{account}':\n\n"
            f"{breach_data}\n\n"
            "Please provide a short summary of these breaches."
        )
        response = model.invoke(prompt)

        # Extract the content from the AIMessage object
        summary = response.content if hasattr(response, 'content') else str(response)
        print("\n=== Ollama Summary ===")
        print(summary)

        # Generate PDF report
        generate_pdf_report(df, summary, account)
    else:
        print("No breach data found.")


if __name__ == "__main__":
    main()
