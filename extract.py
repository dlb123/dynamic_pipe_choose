import xlrd


def data_extract(filename):
    notebook = xlrd.open_workbook(filename)
    try:
        sheet = notebook.sheet_by_index(0)
        rows = list(sheet.get_rows())
        row_data = []
        row_num = []
        for row in rows:
            if row[1].ctype != 0:
                row_data.append(int(row[0].value))
                row_num.append(int(row[1].value))
            else:
                if row[0].ctype != 0:
                    row_data.append(int(row[0].value))
                    row_num.append(int(1))

        print('读取到的管路下料数据: ')
        print(str(row_data) +'\n' + str(row_num))
        return row_data, row_num
    except Exception as e:
        print(str(e))
        print('Excel文件错误, 请重新选择文件!')
        return


if __name__ == '__main__':
    row_data, row_num = data_extract('C:/Users/10706/Desktop/数据样例.xlsx')
    print(row_data, row_num)
