from fastapi import APIRouter, Path, Query
from fastapi.responses import HTMLResponse
import config

router = APIRouter()

@router.get("/table/{file_name}", response_class=HTMLResponse)
def get_table_html(file_name:str = Path(..., title="文件名")):
    try:
        with open(f"table_html/{file_name}.html","r",encoding="utf-8") as html_file:
            html_content = html_file.read()
        return html_content
    except Exception:
        return "ops Something went wrong."

@router.get("/logs", response_class=HTMLResponse)
async def read_logs(secret_key: str = Query(..., description="Your secret key")):
    if secret_key != config.SECRET_KEY:
        return "Oops! Something went wrong."
    
    try:
        with open("log.txt", "r", encoding="utf-8") as log_file:
            lines = log_file.readlines()
            recent_lines = lines[-min(1000, len(lines)):]
        
        html_content = f"""
        <html>
        <head>
          <style>
            body {{
              font-family: monospace;
              background-color: #1f1f1f;
              color: #ffffff;
              padding: 20px;
            }}

            h1 {{
              color: #00ff00;
            }}

            ul {{
              list-style-type: none;
              padding: 0;
            }}

            li {{
              padding: 5px 10px;
              margin-bottom: 5px;
              border-left: 2px solid #00ff00;
            }}

            li:nth-child(odd) {{
              background-color: #333333;
            }}
          </style>
        </head>
        <body>
          <h1>Recent Logs</h1>
          <ul>
            {''.join(f'<li>{line}</li>' for line in recent_lines)}
          </ul>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
    except Exception as e:
        print(e)
        return "Oops! Something went wrong."