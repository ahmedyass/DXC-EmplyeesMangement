from app import app


app.secret_key = "super secret key"

if __name__ == '__main__':
    db.create_all()
    app.run(debug = True)