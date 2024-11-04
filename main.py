from website import create_app #have to run program from this python file

app = create_app()

if __name__== '__main__':
    app.run(debug=True)
