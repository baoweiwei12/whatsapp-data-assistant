from fastapi import APIRouter, Path, Query
from fastapi.responses import HTMLResponse
import config
import psutil

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
def read_logs(secret_key: str = Query(..., description="Your secret key")):
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
    
@router.get("/server_status",response_class=HTMLResponse)
def get_server_status(secret_key: str = Query(..., description="Your secret key")):
    if secret_key != config.SECRET_KEY:
      return "Oops! Something went wrong."  
    # 获取CPU使用率
    cpu_usage = psutil.cpu_percent(interval=1)
    cpu_info = f"CPU使用率: {cpu_usage}%"

    # 获取内存使用情况
    mem = psutil.virtual_memory()
    total_mem = mem.total / (1024**3)  # 总内存大小 (GB)
    used_mem = mem.used / (1024**3)    # 已使用内存大小 (GB)
    percent_mem = mem.percent          # 内存使用率 (%)
    mem_info = f"总内存: {total_mem} GB<br>已使用内存: {used_mem} GB<br>内存使用率: {percent_mem}%"

    # 获取磁盘空间使用情况
    disk = psutil.disk_usage('/')
    total_disk = disk.total / (1024**3)  # 总磁盘空间 (GB)
    used_disk = disk.used / (1024**3)    # 已使用磁盘空间 (GB)
    percent_disk = disk.percent          # 磁盘空间使用率 (%)
    disk_info = f"总磁盘空间: {total_disk} GB<br>已使用磁盘空间: {used_disk} GB<br>磁盘使用率: {percent_disk}%"

    # 获取网络连接信息
    net_connections = psutil.net_connections()
    net_info = "网络连接信息:<br>"
    for conn in net_connections:
        net_info += f"{conn}<br>"

    # 生成HTML文件
    html = f"""
    <html>
    <head>
    <style>
    body {{
        font-family: Arial, sans-serif;
        padding: 20px;
    }}
    h1 {{
        color: #333;
    }}
    .info {{
        background-color: #f4f4f4;
        padding: 10px;
        margin-top: 20px;
    }}
    </style>
    </head>
    <body>
    <h1>服务器运行状态</h1>
    <div class="info">
        <h2>CPU信息</h2>
        <p>{cpu_info}</p>
    </div>
    <div class="info">
        <h2>内存信息</h2>
        <p>{mem_info}</p>
    </div>
    <div class="info">
        <h2>磁盘信息</h2>
        <p>{disk_info}</p>
    </div>
    <div class="info">
        <h2>网络连接信息</h2>
        <p>{net_info}</p>
    </div>
    </body>
    </html>
    """ 
    return html
        
    