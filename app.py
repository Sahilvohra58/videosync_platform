from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transcript.db'
db = SQLAlchemy(app)

class Transcript_Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(5000), nullable=False)
    start_time = db.Column(db.Float, nullable=False)
    end_time = db.Column(db.Float, nullable=False)
    def __repr__(self):
        return f'<Task {self.id}>'


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        start_time = request.form['Start time']
        end_time = request.form['End time']          
        new_task = Transcript_Data(content=task_content,
                                    end_time=end_time,
                                    start_time=start_time)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'

    else:
        tasks = Transcript_Data.query.order_by(Transcript_Data.start_time).all()
        return render_template('index.html', tasks=tasks)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Transcript_Data.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Transcript_Data.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']
        task.start_time = request.form['start_time']
        task.end_time = request.form['end_time']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task'

    else:
        return render_template('update.html', task=task)




# app=app
# if __name__ == "__main__":
#     app.run(debug=True)
