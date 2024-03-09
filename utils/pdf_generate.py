"""
Views for generating the receipts
"""
# import io
# from datetime import date

# from django.conf import settings
import jinja2

from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration


def convert_html_to_pdf(
        data, html_path: str = "receipt.html", pdf_path: str = ""):
    """Generate and render PDF from HTML"""
    font_config = FontConfiguration()
    css = CSS(
        string="""
        @font-face {
            font-family: Times New Roman;
            font-style: normal;
            font-weight: 100;
            font-size: 10px;
            src: url(https://example.com/fonts/Gentium.otf);
        }
        @page {
            size: Letter;
            margin: 0in 0.44in 0.2in 0.44in;
        }
        html {
        font-size: 1.3333px;
      }
      body {
        font-family: "Times New Roman";
        margin: 0;
      }

      h3 {
        margin: 0;
      }

      .container {
        max-width: 1024px;
        min-height: 100vh;
        padding: 0 3rem;
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
      }

      .addresses {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 10rem;
        margin: 2.5rem 0;
      }

      #business_details {
        width: 100%;
        border: 1px;
        margin-right: 10px;
        display: inline-block;
        font-family: "Calibri", sans-serif;
        font-size: medium;
        font-style: italic;
      }

      #business_details > div {
        padding: 0.25rem 0;
      }

      #business_details > h3 {
        font-weight: 600;
        font-style: normal;
        margin: 0 0 1rem 0;
      }

      #business_details > h3.buyer_name {
        margin: 0 0 0.5rem 0;
      }

      .metadata {
        width: 100%;
        background-color: #f9f9f9;
        padding: 1.5rem;
        font-size: medium;
      }

      .metadata > .item {
        display: flex;
        justify-content: space-between;
        margin: 0.5rem;
      }

      table {
        font-family: arial, sans-serif;
        border-collapse: collapse;
        width: 100%;
      }

      td,
      th {
        border-bottom: 1px solid #dddddd;
        text-align: left;
        padding: 16px;
      }

      tr:nth-child(even) {
        background-color: #dddddd;
      }

      .total-amount {
        display: flex;
        padding: 3rem 1rem 1rem 1rem;
        gap: 3rem;
      }

      .total-amount > .info {
        display: flex;
        gap: 0.50rem;
        font-size: small;
        font-weight: 100;
        color: #23c6b9;
        margin-bottom: 10rem;
      }

      .footer {
        border-top: 2px gray solid;
        padding: 1rem 0;
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }

      .footer__item {
        font-family: "Calibri", sans-serif;
        font-size: small;
      }

      .footer__item > h3 {
        margin-bottom: 0.5rem;
      }

      .footer__item > div {
        margin-bottom: 0.5rem;
        font-size: small;
      }
        div { font-size: 10px }
        h1 { font-family: Times New Roman, font-size: 10px }""",
        font_config=font_config,
    )
    html = read_html_file(html_path)
    html_string = jinja2.Template(html).render(data)
    # print(html_string)
    try:
        html_pdf = HTML(string=html_string)
        html_pdf.write_pdf(
            pdf_path,
            stylesheets=[css],
            font_config=font_config,
            optimize_images=True,
            jpeg_quality=60,
            dpi=150,
        )
        print(f"PDF generated and saved at {pdf_path}")
        return True
    except Exception as e:
        print(f"PDF generation failed: {e}")
        return False


def read_html_file(file_path):
    with open(file_path, "r") as file:
        return file.read()
