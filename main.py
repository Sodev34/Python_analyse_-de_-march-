
import requests #permet d'envoyer des requêtes HTTP en utilisant Python
from bs4 import BeautifulSoup # bibliothèque Python permettant d'extraire des données de fichiers HTML et XML
import csv # implémente des classes pour lire et écrire des données tabulaires au format CSV
import time  # Pour ajout delai dans exécution code pour éviter saturer site
import os  # module système pour navigation dans l'arborescence des dossiers
import wget # pour le téléchargement des images 



# url de base pour les fonctions
url_site = 'https://books.toscrape.com' 

# gestion des fichiers pour le téléchargement
CSV_FOLDER = 'CSV/'
IMAGES_FOLDER = 'Images/'

if not os.path.exists(CSV_FOLDER):
    os.mkdir(CSV_FOLDER)
if not os.path.exists(IMAGES_FOLDER):
    os.mkdir(IMAGES_FOLDER)


# liste de l'ensemble des catégories du site
categories_index = []
# liste des livres pour l'ensemble du site
link_books = []
# liste des informations pour un livre
informations_book = []

# fonction pour obtenir liste des liens par catégorie
def list_of_categories():
    # interroge le site
    response = requests.get(url_site)
    soup = BeautifulSoup(response.content, 'html.parser') 
    # cherche url des catégorie pour l'ensemble du site
    lis = soup.find('div', {'class': 'side_categories'}).findAll('a')
    # pour obtenir le nom de la catégorie
    category_name = soup.find('h1').text
    # boucle pour récupérer url de chaque catégorie
    for a in lis:
        categoriy_index = a['href']
        # ajoute url de chaque catégorie a la liste des catégories
        categories_index.append( url_site + '/' + categoriy_index )
    # suppression de la catégorie books     
    del categories_index[0]    

    return categories_index



# fonction qui crée un fichier csv pour chaque catégorie à partir de la liste des catégories: 
def categories_csv():
    # boucle sur la liste des categories 
    for category_index in categories_index:   
        # interroge le site 
        response = requests.get(category_index)
        soup = BeautifulSoup(response.content, 'html.parser') 
        # pour obtenir le nom de la catégorie
        category_name = soup.find('h1').text
        # en-tête fichier csv pour informations book
        en_tete = 'product_page_url', 'category', 'title', 'image_url', 'product_description', 'universal_ product_code', 'price_including_tax', 'price_excluding_tax', 'number_available', 'review_rating'
        print(category_name)

        # création d'un fichier csv par catégorie avec en-tête 
        with open( CSV_FOLDER + category_name +'.csv','w', newline='') as csv_file :
            writer = csv.writer( csv_file, delimiter=',')
            writer.writerow(en_tete)
        

# fonction pour obtenir la liste des livres pour l'ensemble du site
def list_of_books_site():
    # boucle sur les 50 pages du site
    for i in range(5):
        # url de base pour la pagination
        url_catalogue = 'https://books.toscrape.com/catalogue/'
        # permet de reconstituer url site pour chaque page
        url_site = url_catalogue + 'page-' + str(i) + '.html'
        # interroge le site 
        response = requests.get(url_site)
        soup = BeautifulSoup(response.content, 'html.parser')
        # pour obtenir url de chaque livre sur une page du site
        lis = soup.findAll('h3')
        if response.ok:
            # ajoute url de chaque  livre a la liste des livres
            for h3 in lis:
                a = h3.find('a')
                link_book = url_catalogue + a['href']
                link_books.append(link_book.replace(' ',url_catalogue))
    # pause de 3 secondes entre chaque requête             
    time.sleep(3) 

    return (link_books)

            
# fonction pour obtenir les informations  de chaque livre du site pour placement dans dossier csv
def list_of_books_information_site():
        # boucle sur la liste des livres 
        for link_book in link_books:
            # interrgore url d'un livre
            response = requests.get(link_book)
            soup = BeautifulSoup(response.content, 'html.parser')
            # récupération du titre du livre
            title = soup.find('h1').text
            # récupération url image
            image = soup.find('img')['src']
            link_image = ('http://books.toscrape.com/'+ str(image.replace('../', '')))
            # récupétation de la décription du livre
            description= soup.find("div", {"id": "product_description"})
            # récupération upc , prix ht, prix ttc, stock disponible
            product_info = soup.findAll('td')
            # récupération de la notation
            rating = soup.find('p', class_='star-rating').get('class')[1] + ' stars'
            # récupération du nom de la catégorie
            a = soup.find("ul", {"class": "breadcrumb"}).find_all("a")[2]
            category_name = a.get_text()
            # permet d'évite un message d'erreur si un livre n'a pas de déscription
            if description is not None:
                description = soup.find("div", {"id": "product_description"}).find_next("p").get_text()
            else:
                # précise qu'il n'y a pas de description pour un livre en l'absence de déscription
                description = 'no description'
            # regroupe l'ensemble des informations nécessaires pour un livre    
            informations_book = link_book + ',' + category_name + ',' + title.replace(',', '').replace(';', '') + ',' + link_image + ',' + str(description).replace(',', '').replace(';', '') + ',' + product_info[0].text + ',' + product_info[2].text+ ',' + product_info[3].text+ ',' + product_info[5].text+ ',' + rating + '\n'
        
            print(informations_book)

            # intègre le livre avec ses informations au fichier csv de la catégorie qui lui correspond
            with open( CSV_FOLDER + category_name +'.csv','a', newline='') as csv_file :
                csv_file.write(informations_book)

# fonction pour le téléchargement de chaque image avec intégration dans son dossier catégorie            
def image_names():
        # boucle sur la liste des livres
        for link_book in link_books:
            # interrgore url d'un livre
            response = requests.get(link_book)
            soup = BeautifulSoup(response.content, 'html.parser')
            # récupération du nom de la catégorie
            a = soup.find("ul", {"class": "breadcrumb"}).find_all("a")[2]
            category_name = a.get_text()
            # pour obtenir sous dossier image par catégorie
            category_image = IMAGES_FOLDER + category_name + '/'
            # récupération du titre du livre
            title = soup.find('h1')
            # permet d'obtenir le titre de l'image du livre au format image
            title_image = title.get_text() + '.jpg'
            title_image = title_image.replace('/', '')
            # récupération url image
            image = soup.find('img')['src']
            link_image = ('http://books.toscrape.com/'+ str(image.replace('../', '')))


            # création des sous dossiers images pour chaque catégorie
            if not os.path.exists(category_image):
                os.mkdir(category_image)

            # téléchargement des images
            wget.download(link_image, out= category_image + str(title_image))

            
            

# fonction final 
def main():
    list_of_categories()
    categories_csv()
    list_of_books_site()
    image_names()
    list_of_books_information_site()


if __name__ == "__main__": 
        main()