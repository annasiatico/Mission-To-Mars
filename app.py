from flask import Flask, render_template, redirect
import pymongo
import scrape_mars

client = pymongo.MongoClient('mongodb://localhost:27017')
db = client.mars_db
collection = db.mars

app = Flask(__name__)

@app.route('/')
def home():
	mars = collection.find_one()
	return render_template('index.html', mars=mars)

@app.route('/scrape')
def scrape():
	scrape_mars.scrape()
	return redirect('/', code = 302)


if __name__ == '__main__':
	app.run(debug=True)