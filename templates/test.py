@app.route('/filter', methods=['GET', 'POST'])
def filter():
    if request.method=='POST':
        city = request.form['filter_city']
    user=open("user","r")
    users=user.readlines()
    email = users[0]
    user.close()
    all_create= food.query.filter_by(city=city)
    return render_template('collect_food.htm' , all_create=all_create , email=email)