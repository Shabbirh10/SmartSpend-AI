from app import create_app

app = create_app()

if __name__ == '__main__':
    # Bind to 0.0.0.0 to listen on all interfaces (IPv4 and IPv6 mapping)
    app.run(debug=True, host='0.0.0.0', port=8000)
