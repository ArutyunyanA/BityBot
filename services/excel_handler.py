import os
import asyncio
import pandas as pd
from tabulate import tabulate
from dotenv import load_dotenv


load_dotenv()
EXCEL_DIR = os.getenv("EXCEL_DIR", "")

class ExcelHandler:

    def __init__(self):
        self.search_dirs = [x.strip() for x in EXCEL_DIR.split(",") if x.strip()]
        self.home = os.path.expanduser("~")

    async def open_excel_file(self, filename: str) -> str:
        if not filename:
            return "[ERROR] Filename is empty."
        
        for base_dir in self.search_dirs:
            full_path = os.path.join(self.home, base_dir, filename)
            if os.path.isfile(full_path):
                try:
                    df = await asyncio.to_thread(pd.read_excel, full_path)
                    return "[INFO] File is empty." if df.empty else tabulate(df, headers='keys', tablefmt='grid')
                except Exception as e:
                    return f"[ERROR] Failed to open file: {e}"
        
        return "[INFO] File not found in specified directories."

    async def edit_excel_file(self, filename: str, row: int, column: str, value) -> str:
        for base_dir in self.search_dirs:
            full_path = os.path.join(self.home, base_dir, filename)
            if os.path.isfile(full_path):
                try:
                    df = await asyncio.to_thread(pd.read_excel, full_path)
                    if str(row).isdigit():
                        row_index = int(row)
                    else:
                        matches = df.index[df['Name'] == row].tolist()
                        if not matches:
                            return f"[ERROR] Row '{row}' not found."
                        row_index = matches[0]
                    try:
                        if str(value).isdigit() or '.' in str(value):
                            value = float(value)
                        else:
                            value = int(value)
                    except ValueError:
                        pass
                    df.at[row_index, column] = value
                    await asyncio.to_thread(df.to_excel, full_path, index=False)
                    return "[SUCCESS] File updated successfully."
                except Exception as e:
                    return f"[ERROR] Failed to edit file: {e}"
        
        return "[ERROR] File not found."

