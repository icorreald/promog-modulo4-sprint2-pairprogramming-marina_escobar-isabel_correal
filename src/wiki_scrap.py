from bs4 import BeautifulSoup
import requests


def get_rewards (url):
    
    # Crea el dataframe
    df = {'Award' : [],
          'Year' : [],
          'Recipient' : [],
          'Category' : []}
    
    # Obtiene la respuesta de la url
    res_url = requests.get(url)
    
    # Parsea el contenido HTML de la respuesta usando BeautifulSoup
    soup_url = BeautifulSoup(res_url.content, 'html.parser')
    
    # Encuentra todas las tablas en la página
    all_tables = soup_url.find_all("table")
    
    # Asigna la sexta tabla (la que contiene la info de las películas) a la variable 'table'
    table = all_tables[2]
    
    # Encuentra todas las filas en la tabla
    rows = table.find_all("tr")
    award_names = table.find_all("th")
    award_names = [element.text.replace("\n", "").strip() for element in award_names[6::]]
    album_names = ['Taylor Swift', 'Fearless', 'Speak Now', 'Red', '1989', 'Reputation', 'Lover', 'Folklore', 'Evermore', 'Midnights']
    
    all_rows = []
    
    for i, row in enumerate(rows[1::]):
        
        row_elements = row.text.split("\n")
        row_elements = [element for element in row_elements if element != '']
        
        if len(row_elements) == 6:
            all_rows.append(row_elements)
        
            if "Won" in row_elements:               
                df['Award'].append(row_elements[0])
                df['Year'].append(row_elements[1])
                df['Recipient'].append(row_elements[2])
                df['Category'].append(row_elements[3])
                
        else:
            award = [element if element in award_names else all_rows[i-1][0] for element in row_elements]
            year = [element if element.isdigit() and element != '1989' else all_rows[i-1][1] for element in row_elements]
            recipient = [element if element in album_names or element == 'Swift' or '"' in element else all_rows[i-1][2] for element in row_elements]
            category = [element if len(element.split(" ")) >= 2 and element != recipient[0] else all_rows[i-1][3] for element in row_elements]
            
            all_rows.append([award[0], year[0], recipient[0], category[0]])
            
            if 'Won' in row_elements:
                df['Award'].append(award[0])
                df['Year'].append(year[0])
                df['Recipient'].append(recipient[0])
                df['Category'].append(category[0])
            
    return df