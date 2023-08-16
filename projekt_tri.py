author =(
'''
projekt_tri.py: treti projekt do Engeto Online Python Akademie  (druha verze tretiho projektu, prvni zamitnuta)
author: Ales Stransky
email: ales.stransky@seznam.cz
discord: Ales S#5138
''')




from requests import get
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys




def get_list_of_parties(url_adress_of_parties):
    parties_list=[" "]    
   
    html_code = get(url_adress_of_parties)
    soup = BeautifulSoup(html_code.text, 'html.parser')
    table = soup.find('table')
    cells = table.find_all('td')

    parties_list_big=[]
    for cell in cells:
        parties_list_big.append(cell.text)

    for i in range(2,len(parties_list_big),3):    
       parties_list.append(parties_list_big[i])
       
    return parties_list   # index of parties in list is equal to number of party used in table with results


def write_header_into_file(handle_csv_file,parties_list):
    handle_csv_file.write('"code","location","registered","envelopes","valid"')
    for i in range(1,len(parties_list)):
         handle_csv_file.write(',' + '"' + parties_list[i] + '"'   )



def which_links_can_be_submited_as_parameter(url_adress):
    absolute_link=[]
    base_url = url_adress
    response = get(url_adress)
  
    soup = BeautifulSoup(response.text, features="html.parser")

    for a in soup.find_all('a', href=True):
        # change relative link to absolute url link
        odkazy_absolute_url = urljoin(base_url, a['href'])
        absolute_link.append(odkazy_absolute_url)
  
    list_of_available_links=[]
    for link in absolute_link:
        
        """all links which user can put as parametr and is possible to evaluate them
        are begining by string 'https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj='  """
        if (link[:52] == "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj="):
            list_of_available_links.append(link)
            
    return(list_of_available_links)




def get_list_of_particular_municipalities(url_in_input_argument):
    code_name_link=[]
    list_code_name_link=[]
    
    response = get(url_in_input_argument)
    soup = BeautifulSoup(response.text, features="html.parser")

    cells = soup.find_all('td')
    counter=1
    for cell in cells:
     
         #first cell - cislo
         if counter==1:
            if cell.text == "-":   #if cell is empty, there is char "-"
                break  # first cell is empty, it means we are at the end of table
            else:
              code_name_link.append(cell.text)    #code of village
              relative_link = cell.find('a').get('href')   #link to village

              base_url= url_in_input_argument
              absolute_link = urljoin(base_url, relative_link)              

              code_name_link.append(absolute_link)  #link to village
              counter+=1
              
         else:
             if counter==2:
                 #second cell - nazev
                 code_name_link.append(cell.text)  #name of village
                 counter+=1
             else:
             #third cell - Vyber okrsku  
               counter=1
               #print(code_name_link)
               list_code_name_link.append(code_name_link)
               code_name_link=[]
              
    return list_code_name_link


 
def put_result_from_table(cells_table, results_of_parties):
  
  party_number=""
  cell_number=1  # in row of cells_table are 5 cells: first is number of party (cell_number=1), third is total votes for party (cell_number=3) 
  for cell in (cells_table):
 
      if cell_number==1:
          if cell.text != "-":   #if cell is empty, there is char "-"
            party_number=int(cell.text)
          else:
            break # first cell is empty, it means we are at the end of table
      if cell_number==3:
          results_of_parties[party_number]=cell.text
          
      cell_number+=1
      if (cell_number)==6:
          cell_number=1
 
  return results_of_parties
 
 

def process_particular_municipality(municipality_code_name_link, parties_list, handle_csv_file) : 

  municipality_code=municipality_code_name_link[0]
  municipality_link=municipality_code_name_link[1]
  municipality_name=municipality_code_name_link[2]

  #+print(municipality_link)

  results_of_parties=[]  #how many votes party obtained in this particular municipality
  for i in range(len(parties_list)):
      results_of_parties.append("-")
 

  html_code = get(municipality_link)
  soup = BeautifulSoup(html_code.text, 'html.parser')
  
  all_table = soup.find_all('table')

  cells_table_0 = all_table[0].find_all('td')

  #volici v seznamu - registered
  registered = cells_table_0[3].text
  
  #vydane obalky  - envelopes
  envelopes = cells_table_0[4].text
  
  #platne hlasy - valid
  valid = cells_table_0[7].text
 
  handle_csv_file.write(f"\n{municipality_code},{municipality_name},{registered},{envelopes},{valid}")
  
  
  

  #results from left and right table
  cells_table_1 = all_table[1].find_all('td')
  results_of_parties = put_result_from_table(cells_table_1, results_of_parties)

  cells_table_2 = all_table[2].find_all('td')
  results_of_parties = put_result_from_table(cells_table_2, results_of_parties)

  
  for i in range(1,len(parties_list)):
      handle_csv_file.write(","+ results_of_parties[i])
  
  



##############################################         Start of programme          ###################################################

url_main_page="https://volby.cz/pls/ps2017nss/ps3?xjazyk=CZ"
url_adress_of_parties_list="https://volby.cz/pls/ps2017nss/ps82?xjazyk=CZ"

list_of_available_links = which_links_can_be_submited_as_parameter(url_main_page)


url_in_input_argument=str(sys.argv[1])  # first parameter
file_name=str(sys.argv[2])      # second parameter

if not(url_in_input_argument in list_of_available_links):
    print ("Jako prvni parametr byl zadan nespravny webovy odkaz, beh programu je ukoncen")
    quit()


parties_list = get_list_of_parties(url_adress_of_parties_list)

handle_csv_file = open(file_name, mode="w")
write_header_into_file(handle_csv_file,parties_list)



#process second page
list_code_name_link=get_list_of_particular_municipalities(url_in_input_argument)

#process third page
for municipality_code_name_link in list_code_name_link:
    process_particular_municipality(municipality_code_name_link, parties_list, handle_csv_file)

handle_csv_file.close()
