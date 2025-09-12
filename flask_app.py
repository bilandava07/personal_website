from flask import Flask, render_template 


app = Flask(__name__)

@app.route('/')
def home_page():
    return render_template('home_page.html')

@app.route('/bike')
def cycling_page():
    return render_template('cycling_page.html')



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

