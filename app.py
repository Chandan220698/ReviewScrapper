# Importing libraries
from flask import Flask, render_template,request
from flask_cors import CORS, cross_origin

from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as bs
import requests


app = Flask(__name__)  ## Initialising the Flash app with name 'app'
#CORS(app)

@app.route('/', methods = ['GET'])
@cross_origin()
def homepage():
    return render_template("index.html")
# base URL + /
# https://localhost:8000 + /
@app.route('/scrap', methods = ['POST'])
@cross_origin()
def index():
    if request.method == 'POST':

         # Form - class in the index HTML and content is field inside it
        searchString = request.form['content'].replace(" ", "") # Fetching the search string entered by user
        #searchString = searchString # Removing all the  blank spaces

        try:
        
            # No reviews are available in the scrapperDB
            # No collection with searchString
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            #flipkart_url = flipkart_url + searchString

            uClient = uReq(flipkart_url)  # requesting the webpage from the internet
            flipkartPage = uClient.read() # Reading the webpage (HTML code of webpage)
            uClient.close()

            flipkart_html = bs(flipkartPage, "html.parser")
            allProducts = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            #del allProducts[0:3]
            targetProduct = allProducts[3] # Getting the first product
            # Actual link for target product
            targetProductLink = "https://www.flipkart.com" + targetProduct.div.div.div.a['href']
            productPage = requests.get(targetProductLink)
            product_html = bs(productPage.text, "html.parser")
            reviewBox = product_html.find_all("div", {'class': "_16PBlm"})

            reviews = [] # List to store all the reviews under html class _16PBlm
            for review in reviewBox:
                try:
                    name = review.div.div.find_all('p', {'class': "_2sc7ZR _2V5EHH"})[0].text
                except:
                    name = 'No Name'

                try:
                    rating = review.div.div.div.div.text
                except:
                    rating = 'No Rating'

                try:
                    commentHead = review.div.div.div.p.text
                except:
                    commentHead = 'No Comment Heading'

                try:
                    comtag = review.div.div.find_all('div', {'class': ''})
                    custComment = comtag[0].div.text
                except:
                    custComment = 'No Customer Comment'

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                            "Comment": custComment}
                reviews.append(mydict)

            return render_template('results.html', reviews = reviews)

        except:
            return 'something is wrong'


if __name__ == "__main__":
    app.run(debug=True)