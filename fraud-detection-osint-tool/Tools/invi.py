import os
from dotenv import load_dotenv
import openai
import requests
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet

# Load environment variables from .env file
load_dotenv()

# Access the API keys from environment variables
HIBP_API_KEY = os.getenv("HIBP_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Ensure that API keys are available
if not HIBP_API_KEY:
    raise ValueError("HIBP_API_KEY not found in environment variables.")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

# Initialize the OpenAI API key
openai.api_key = OPENAI_API_KEY

# HIBP API Base URL
BASE_URL = "https://haveibeenpwned.com/api/v3"

def get_breached_data(account):
    """
    Retrieve the breach data for the given account from the HIBP API.
    """
    url = f"{BASE_URL}/breachedaccount/{account}?truncateResponse=false"
    headers = {
        "hibp-api-key": HIBP_API_KEY,
        "User-Agent": "PythonApp"  # Required by HIBP API
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        print(f"No breaches found for {account}.")
        return []
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []

def plot_breaches(breach_data, account):
    """
    Plot the breach data and save it as an image.
    """
    if not breach_data:
        return None

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
    image_filename = f"{account}_breach_data.png"
    plt.savefig(image_filename)
    plt.close()
    print(f"Plot saved as '{image_filename}'")
    return image_filename

def generate_pdf_report(df, summary, account, image_path):
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
    column_widths = [
        max_width * 0.2,  # Name
        max_width * 0.2,  # Breach Date
        max_width * 0.2,  # Is Verified
        max_width * 0.4   # Data Classes
    ]

    # Prepare table data with text wrapping for 'Data Classes'
    data = [['Name', 'Breach Date', 'Is Verified', 'Data Classes']]
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
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 12))

    # Summary
    summary_title = Paragraph("Summary", styles['Heading2'])
    elements.append(summary_title)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(summary, styles['BodyText']))

    # Add breach data plot image
    if image_path and os.path.exists(image_path):
        elements.append(Spacer(1, 12))
        elements.append(Image(image_path, width=400, height=300))

    # Build the PDF
    doc.build(elements)
    print(f"PDF report saved as '{pdf_filename}'")

def generate_summary(breach_data, account):
    """
    Generate a summary of breach data using OpenAI's GPT-4.
    """
    prompt = (
        f"Below is the JSON breach data for '{account}':\n\n"
        f"{breach_data}\n\n"
        f"You are an expert in cybersecurity data analysis. Your task is to:\n"
        f"1. Summarize the key details of the breach, including affected parties, compromised data types, and the timeline of events.\n"
        f"2. Identify any notable patterns or trends in the data.\n"
        f"3. Suggest additional insights, such as potential vulnerabilities exploited, mitigation strategies, "
        f"   and implications for future security practices.\n"
        f"4. Highlight any data points or metadata that could add value to a security report."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1024,
            temperature=0.7,
        )
        return response.choices[0].message["content"]
    except Exception as e:
        print(f"Error generating summary: {e}")
        return "No summary could be generated."

def main():
    # Prompt the user for the account
    account = input("Enter the account (email/username/etc.) you want to check: ")

    # Fetch breach data
    breach_data = get_breached_data(account)
    if not breach_data:
        print("No breach data available.")
        return

    # Convert to DataFrame for reporting
    df = pd.DataFrame(breach_data)

    # Generate plot
    image_path = plot_breaches(breach_data, account)

    # Generate summary using OpenAI
    summary = generate_summary(breach_data, account)

    # Generate PDF report
    generate_pdf_report(df, summary, account, image_path)

if __name__ == "__main__":
    main()
