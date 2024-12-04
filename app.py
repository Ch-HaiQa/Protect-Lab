import os
import cohere
import json
import subprocess
from dotenv import load_dotenv
from flask import Flask, request, render_template, send_file, jsonify, redirect, url_for
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import matplotlib
matplotlib.use('Agg')  # Set non-interactive backend to avoid Tkinter issues
from matplotlib import pyplot as plt
import io


# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize Cohere client
cohere_api_key = os.getenv("COHERE_API_KEY")
co = cohere.Client(cohere_api_key)

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    code_content = file.read().decode('utf-8')
    analysis_type = request.form.get('analysis_type')

    if analysis_type == 'api':
        return analyze_with_api(code_content)
    elif analysis_type == 'bandit':
        return analyze_with_bandit(code_content)
    else:
        return "Invalid analysis type selected", 400

def analyze_with_api(code_content):
    """
    Analyzes code using Cohere API and generates a PDF report.
    """
    try:
        prompt = f"Analyze the following code for security vulnerabilities:\n\n{code_content}\n\nProvide a detailed explanation of potential vulnerabilities and risks."
        response = co.generate(
            model='command-xlarge-nightly',
            prompt=prompt,
            max_tokens=300,
            temperature=0.5
        )
        analysis = response.generations[0].text

        # Generate PDF report with graphs
        pdf_path = generate_pdf_report(analysis, "API-Based Code Analysis Report", [])
        return render_template('report.html', analysis=analysis, pdf_path=pdf_path)
    except Exception as e:
        print(e)
        return render_template('error.html', message="API request failed.")

def analyze_with_bandit(code_content):
    """
    Analyzes code using Bandit and generates a PDF report.
    """
    try:
        # Create a temporary file to store the code for analysis
        temp_filename = 'temp_code.py'
        with open(temp_filename, 'w') as temp_file:
            temp_file.write(code_content)

        # Run Bandit analysis on the temporary file
        analysis, summary = run_bandit(temp_filename)
        
        # Remove the temporary file after analysis
        os.remove(temp_filename)

        # If no issues are found, display a "No issues found" message
        if analysis == "No issues found.":
            return render_template('banditReport.html', analysis=analysis, pdf_path=None)

        # Generate graph for vulnerability severity levels
        graph_path = generate_graph(summary)

        # Generate pie chart for secure vs insecure code
        pie_chart_path = generate_pie_chart(summary)

        # Generate PDF report
        pdf_path = generate_pdf_report(analysis, "Bandit Analysis Report", summary, graph_path, pie_chart_path)
        return render_template('banditReport.html', analysis=analysis, pdf_path=pdf_path)

    except Exception as e:
        print(f"Error during analysis: {e}")
        return render_template('error.html', message="Bandit analysis failed.")


def run_bandit(filename):
    """
    Runs Bandit on the given filename and returns results and a summary of severity levels.
    """
    try:
        # Run the Bandit command to analyze the Python code
        command = ['bandit', '-r', filename, '--format', 'json', '-q']
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if stderr:
            raise Exception(f"Bandit error: {stderr.decode('utf-8')}")

        analysis_results = json.loads(stdout.decode('utf-8'))
        results = analysis_results.get('results', [])

        # If no issues are found, return a message indicating no issues
        if not results:
            return "No issues found.", {}

        # Process the results and format them for the report
        formatted_results = []
        severity_summary = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0}

        for result in results:
            issue_text = (
                f"File: {result['filename']}\n"
                f"Issue: {result['issue_text']}\n"
                f"Severity: {result['issue_severity']}\n"
                f"Confidence: {result['issue_confidence']}\n"
                f"Line Number: {result['line_number']}\n"
                "---------------------------------------"
            )
            severity_summary[result['issue_severity']] += 1
            formatted_results.append(issue_text)

        formatted_text = "\n\n".join(formatted_results) if formatted_results else "No issues found."
        return formatted_text, severity_summary

    except Exception as e:
        # Return the error message if Bandit fails to run
        return f"Error: {e}", {}


def generate_graph(summary):
    """
    Generates a bar chart for vulnerability severity levels and saves it as an image.
    """
    labels = list(summary.keys())
    counts = list(summary.values())

    plt.bar(labels, counts, color=['green', 'orange', 'red'])
    plt.title('Vulnerability Severity Levels')
    plt.xlabel('Severity')
    plt.ylabel('Count')

    graph_path = 'severity_graph.png'
    plt.savefig(graph_path)
    plt.close()
    return graph_path

def generate_pie_chart(summary):
    """
    Generates a pie chart for secure vs insecure code and saves it as an image.
    """
    # Categorize secure vs insecure
    secure = sum(count for level, count in summary.items() if level == 'LOW')
    insecure = sum(count for level, count in summary.items() if level != 'LOW')

    labels = ['Secure', 'Insecure']
    sizes = [secure, insecure]
    colors = ['lightgreen', 'lightcoral']

    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.title('Secure vs Insecure Code')

    pie_chart_path = 'secure_insecure_pie_chart.png'
    plt.savefig(pie_chart_path)
    plt.close()
    return pie_chart_path

def generate_pdf_report(analysis_text, title, summary=None, graph_path=None, pie_chart_path=None):
    """
    Generates a PDF report based on the analysis text, including graphs and summary tables.
    """
    pdf_path = 'analysis_report.pdf'
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 12))

    if summary:
        elements.append(Paragraph("Vulnerability Summary:", styles['Heading2']))
        table_data = [["Severity", "Count"]] + [[k, v] for k, v in summary.items()]
        table = Table(table_data)
        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                   ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                   ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                   ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
        elements.append(table)
        elements.append(Spacer(1, 12))

    elements.append(Paragraph("Analysis Results:", styles['Heading2']))
    analysis_paragraphs = [Paragraph(line, styles['BodyText']) for line in analysis_text.split('\n') if line.strip()]
    elements.extend(analysis_paragraphs)
    elements.append(Spacer(1, 12))

    if graph_path:
        from reportlab.platypus import Image
        elements.append(Paragraph("Severity Graph:", styles['Heading2']))
        elements.append(Image(graph_path, width=400, height=200))
        elements.append(Spacer(1, 12))

    if pie_chart_path:
        elements.append(Paragraph("Secure vs Insecure Code:", styles['Heading2']))
        elements.append(Image(pie_chart_path, width=400, height=200))
        elements.append(Spacer(1, 12))

    doc.build(elements)
    return pdf_path

@app.route('/download_report')
def download_report():
    return send_file('analysis_report.pdf', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
