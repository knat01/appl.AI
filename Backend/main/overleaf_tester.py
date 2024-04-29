from flask import Flask, render_template_string
import base64
import urllib.parse

app = Flask(__name__)

@app.route('/')
def index():
    # Basic LaTeX document
    latex_content = r"""
\documentclass{article}
\begin{document}
Hello, World! This is a test document.
\end{document}
    """
    # Encode the LaTeX content into Base64 and URL encode the result
    encoded_content = base64.b64encode(latex_content.encode('utf-8')).decode('utf-8')
    url_encoded_content = urllib.parse.quote(encoded_content)  # URL encode the Base64 string
    data_url = f"data:application/x-tex;base64,{url_encoded_content}"

    # HTML form that submits to Overleaf
    form_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Open LaTeX in Overleaf</title>
    </head>
    <body>
        <h1>Submit LaTeX to Overleaf</h1>
        <form action="https://www.overleaf.com/docs" method="post" target="_blank">
            <input type="hidden" name="snip_uri" value="{data_url}">
            <input type="submit" value="Open in Overleaf">
        </form>
    </body>
    </html>
    """
    return render_template_string(form_html)

if __name__ == '__main__':
    app.run(debug=True)
