import openpyxl

def read_excel_column_to_list(file_path, sheet_name, column, start_row, end_row):
    # Load the workbook and select the desired worksheet
    workbook = openpyxl.load_workbook(file_path)
    worksheet = workbook[sheet_name]

    # Read cells from the specified column and row range into a list
    output = [cell.value for cell in worksheet[column][start_row-1:end_row]]

    return output, workbook, worksheet