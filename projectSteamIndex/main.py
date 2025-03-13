from website import create_app  # since website is a python package with the __init__.py anytime we import it, it will automatically run whatever is in the __init__.py

app = create_app()

if __name__ == '__main__':  # only want it to run the webserver if we run the main
    app.run(debug=True)

