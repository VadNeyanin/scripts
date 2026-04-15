import subprocess
import pandas as pd
import numpy as np
from openpyxl import load_workbook
import duckdb
from datetime import datetime

def get_file_path(title):
    result = subprocess.run(
        ['zenity', '--file-selection', '--title=' + title],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        return result.stdout.strip()
    else:
        return None
    

    
def programs(filename, sprav):
    def show_df_as_table_zenity(df, title):
      
        if df is None or df.empty:
            subprocess.run(['zenity', '--info', '--title=' + title,
                        '--text=Нет данных для отображения'])
            return
        df_display = df.head(50)
        if len(df_display.columns) > 10:
            df_display = df_display.iloc[:, :10]
        cmd = ['zenity', '--list',
            '--title=' + title,
            '--text=Показано ' + str(len(df_display)) + ' строк',
            '--width=1200',
            '--height=700',
            '--column=№ строки']
        
        for col in df_display.columns:
            cmd.append('--column=' + str(col)[:30])
        for i, (idx, row) in enumerate(df_display.iterrows()):
            cmd.append(str(i+1))
            for col in df_display.columns:
                value = str(row[col])
                if len(value) > 100:
                    value = value[:97] + "..."
                cmd.append(value)
        
        subprocess.run(cmd)
    df = pd.read_excel(
        filename, header=0, dtype=
        {'Основное средство': str, 
         'Инвентарный номер': str, 
         'Дата принятия к учету': str, 
         'Страна происхождения': str,
         'Класс ПО': str,
         'Номер ПО в реестре': str
         }
        )
    df = df.drop(len(df)-1)
    data = ['02.09', '03.06', '02.04', '03.01', '03.10', '03.11', '06.03', '06.09', '06.10', '06.11', '06.04', '05.14', '06.12', '06.06', '06.07', '(BI) (11)', '05.05', '06.02']
    df['Месяц'] = 1
    df['Год'] = 1
    move = df.pop('Месяц')
    df.insert(df.columns.get_loc('Дата принятия к учету')+1, 'Месяц', move)
    move = df.pop('Год')
    df.insert(df.columns.get_loc('Дата принятия к учету')+2, 'Год', move)
    df_sprav = pd.read_excel(sprav, header=0, dtype={'Инвентарный номер': str, 'Страна происхождения': str, 'Класс ПО': str, 'Номер ПО в реестре': str})    
    df['Страна происхождения'] = df['Страна происхождения'].fillna('').astype(str)
    df['Класс ПО'] = df['Класс ПО'].fillna('').astype(str)
    df['Номер ПО в реестре'] = df['Номер ПО в реестре'].fillna('').astype(str)
    df_sprav['Страна происхождения'] = df_sprav['Страна происхождения'].fillna('').astype(str)
    print(df.dtypes)
    print(df_sprav.dtypes)
    duckdb.sql("CREATE TABLE test AS SELECT * FROM df")
    result = duckdb.sql("PRAGMA table_info('test')")
    print(result)
    duckdb.sql("CREATE TABLE sprav AS SELECT * FROM df_sprav")
    result = duckdb.sql("PRAGMA table_info('sprav')")
    print(result)
    duckdb.sql('UPDATE test SET "Дата принятия к учету" = strptime("Дата принятия к учету", \'%d.%m.%Y\')')
    duckdb.sql('''
       CREATE OR REPLACE TABLE test AS 
       SELECT
            "Дата принятия к учету"::DATE as "Дата принятия к учету",
            * EXCLUDE ("Дата принятия к учету")
        FROM test
    ''')
    df = duckdb.sql('SELECT * FROM test').df()
    move = df.pop('Дата принятия к учету')
    df.insert(df.columns.get_loc('Месяц'), 'Дата принятия к учету', move)
    duckdb.sql("CREATE OR REPLACE TABLE test AS SELECT * FROM df")
    duckdb.sql('UPDATE test SET "Дата принятия к учету" = "Дата принятия к учету"::DATE')
    duckdb.sql('UPDATE test\
                SET\
                    Месяц = EXTRACT(MONTH FROM "Дата принятия к учету"), \
                    Год = EXTRACT(YEAR FROM "Дата принятия к учету")')
    duckdb.sql('''
        CREATE OR REPLACE TABLE test_new AS 
        SELECT
            "№ п/п",
            "Основное средство",
            "Инвентарный номер",
            STRFTIME("Дата принятия к учету", '%d.%m.%Y') as "Дата принятия к учету",
            "Месяц",
            "Год",
            "Срок полезного использования",
            "Место хранения",
            "МОЛ",
            "Балансовая стоимость",
            "Количество",
            "Страна происхождения",
            "Класс ПО",
            "Номер ПО в реестре",
            "Типовая деятельность",
            "Аренда",
            "Серверное"
        FROM test
    ''')

    duckdb.sql("DROP TABLE test")
    duckdb.sql("ALTER TABLE test_new RENAME TO test")
    #duckdb.sql('ALTER TABLE test ADD "Класс ПО" VARCHAR')
    #duckdb.sql('ALTER TABLE test ADD "Номер ПО в реестре" VARCHAR')
    duckdb.sql('ALTER TABLE test ADD "Название в реестре" VARCHAR')
    #duckdb.sql('ALTER TABLE test ADD "Аренда" INTEGER')
    #duckdb.sql('ALTER TABLE test ADD "Серверное" INTEGER')
    duckdb.sql('''
        UPDATE test 
        SET
            "Количество" = sprav."Количество",
            "Страна происхождения" = sprav."Страна происхождения",
            "Класс ПО" = sprav."Класс ПО", 
            "Номер ПО в реестре" = sprav."Номер ПО в реестре",
            "Аренда" = sprav."Аренда",
            "Серверное" = sprav."Серверное",
            "Название в реестре" = sprav."Название в реестре"
        FROM sprav
        WHERE test."Инвентарный номер" = sprav."Инвентарный номер"
    ''')
    data = [f"'{item}'" for item in data]
    duckdb.sql(f'CREATE OR REPLACE TABLE stats_1 AS SELECT * FROM test WHERE "Класс ПО" IN ({",".join(data)})')
    result = duckdb.sql('SELECT MAX(Год) FROM stats_1').fetchone()
    current_year = result[0]
    result = duckdb.sql('SELECT MAX(Месяц) FROM stats_1 WHERE Год = (SELECT MAX(Год) FROM stats_1)').fetchone()
    print(result[0])
    query = f'''
    CREATE OR REPLACE TABLE stats_2 AS 
    SELECT 
        "Название в реестре", 
        "Класс ПО", 
        "Номер ПО в реестре", 
        SUM(Количество) AS Количество,
        COUNT(CASE WHEN "Год" = {current_year} THEN 1 END) as "Количество {current_year} год"
    FROM "stats_1" 
    GROUP BY "Класс ПО", "Номер ПО в реестре", "Название в реестре"
    ORDER BY "Количество" DESC
    '''

    duckdb.sql(query)
    #duckdb.sql('CREATE OR REPLACE TABLE stats_2 AS SELECT "Название в реестре", "Класс ПО", "Номер ПО в реестре", COUNT(*) as "Количество", \
    #FROM "stats_1" \
    #GROUP BY "Класс ПО", "Номер ПО в реестре", "Название в реестре"\
    #ORDER BY "Количество" DESC')
    duckdb.sql('''
    CREATE OR REPLACE TABLE stats_1 AS 
    -- Сгруппированные записи с номером в реестре (суммируем)
    SELECT
        ANY_VALUE("№ п/п") as "№ п/п",
        ANY_VALUE("Основное средство") as "Основное средство",
        ANY_VALUE("Инвентарный номер") as "Инвентарный номер",
        ANY_VALUE("Дата принятия к учету") as "Дата принятия к учету",
        ANY_VALUE("Месяц") as "Месяц",
        ANY_VALUE("Год") as "Год",
        ANY_VALUE("Срок полезного использования") as "Срок полезного использования",
        ANY_VALUE("Место хранения") as "Место хранения",
        ANY_VALUE("МОЛ") as "МОЛ",
        SUM("Балансовая стоимость") as "Балансовая стоимость",
        SUM("Количество") as "Количество",
        ANY_VALUE("Страна происхождения") as "Страна происхождения",
        ANY_VALUE("Класс ПО") as "Класс ПО",
        "Номер ПО в реестре",
        ANY_VALUE("Название в реестре") as "Название в реестре"
    FROM test
    WHERE "Номер ПО в реестре" IS NOT NULL
    GROUP BY "Номер ПО в реестре"

    UNION ALL

    -- Негруппированные записи с NULL номером (оставляем как есть)
    SELECT
        "№ п/п",
        "Основное средство",
        "Инвентарный номер",
        "Дата принятия к учету",
        "Месяц",
        "Год",
        "Срок полезного использования",
        "Место хранения",
        "МОЛ",
        "Балансовая стоимость",
        "Количество",
        "Страна происхождения",
        "Класс ПО",
        "Номер ПО в реестре",
        "Название в реестре"
    FROM test
    WHERE "Номер ПО в реестре" IS NULL
    ''')
    duckdb.sql('''
    CREATE OR REPLACE TABLE stats_1 AS 
    -- Сгруппированные записи с номером в реестре (суммируем)
    SELECT
        ANY_VALUE("№ п/п") as "№ п/п",
        "Основное средство",
        ANY_VALUE("Инвентарный номер") as "Инвентарный номер",
        ANY_VALUE("Дата принятия к учету") as "Дата принятия к учету",
        ANY_VALUE("Месяц") as "Месяц",
        ANY_VALUE("Год") as "Год",
        ANY_VALUE("Срок полезного использования") as "Срок полезного использования",
        ANY_VALUE("Место хранения") as "Место хранения",
        ANY_VALUE("МОЛ") as "МОЛ",
        SUM("Балансовая стоимость") as "Балансовая стоимость",
        SUM("Количество") as "Количество",
        ANY_VALUE("Страна происхождения") as "Страна происхождения",
        ANY_VALUE("Класс ПО") as "Класс ПО",
        ANY_VALUE("Номер ПО в реестре") as "Номер ПО в реестре",
        ANY_VALUE("Название в реестре") as "Название в реестре"
    FROM stats_1
    GROUP BY "Основное средство"
    ORDER BY "Количество" DESC
    ''')
    
    duckdb.sql('''
    UPDATE stats_1
    SET
        "Основное средство" = "Название в реестре"
    WHERE "Название в реестре" IS NOT NULL
    ''')
#    df_1 = duckdb.sql('SELECT * FROM stats_1').df()
    duckdb.sql('ALTER TABLE stats_1 DROP COLUMN "Название в реестре"')
    duckdb.sql('ALTER TABLE stats_1 DROP COLUMN "№ п/п"')
    duckdb.sql('ALTER TABLE stats_1 DROP COLUMN "Инвентарный номер"')
    duckdb.sql('ALTER TABLE stats_1 DROP COLUMN "Дата принятия к учету"')
    duckdb.sql('ALTER TABLE stats_1 DROP COLUMN "Месяц"')
    duckdb.sql('ALTER TABLE stats_1 DROP COLUMN "Год"')
    duckdb.sql('ALTER TABLE stats_1 DROP COLUMN "Срок полезного использования"')
    duckdb.sql('ALTER TABLE stats_1 DROP COLUMN "Место хранения"')
    duckdb.sql('ALTER TABLE stats_1 DROP COLUMN "МОЛ"')

    print(duckdb.sql('''CREATE OR REPLACE TABLE stats_3 AS
                SELECT  test.*
                FROM    test
                FULL JOIN
                        sprav
ON      test."Инвентарный номер" = sprav."Инвентарный номер"
WHERE   test."Инвентарный номер" IS NULL OR sprav."Инвентарный номер" IS NULL
               '''))
    df_stat_3 = duckdb.sql('SELECT * FROM stats_3').df()
    duckdb.sql(f'UPDATE test SET "Типовая деятельность" = 1 WHERE "Класс ПО" IN ({",".join(data)})')
    duckdb.sql('''CREATE OR REPLACE TABLE stats_4 AS
            SELECT sprav.* FROM sprav
            LEFT JOIN test
               ON sprav."Инвентарный номер" = test."Инвентарный номер"
            WHERE test."Инвентарный номер" IS NULL''')
    df = duckdb.sql('SELECT * FROM test').df()
    df_stat_1 = duckdb.sql('SELECT * FROM stats_1').df()
    df_stat_2 = duckdb.sql('SELECT * FROM stats_2').df()
    df_stat_4 = duckdb.sql('SELECT * FROM stats_4').df()
    today = datetime.now().strftime('%d.%m.%Y')
    filename = f'software_{today}.xlsx'
    with pd.ExcelWriter(filename) as writer:
        df.to_excel(writer, sheet_name='МОН', index=False)
        df_stat_1.to_excel(writer, sheet_name='Сгруппированные', index=False)
        df_stat_2.to_excel(writer, sheet_name='Количество типовой деятельности', index=False)
        df_stat_3.to_excel(writer, sheet_name='Новые позиции', index=False)
        df_stat_4.to_excel(writer, sheet_name='Списанное', index=False)
filename = get_file_path('Выберите выгрузку ПО')
sprav = get_file_path('Выберите справочник')
res = programs(filename, sprav)
