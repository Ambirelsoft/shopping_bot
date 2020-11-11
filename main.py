from server.app import app

# точка входа. Урлы смотреть в server - routes
app.run(debug=True, host='0.0.0.0')
