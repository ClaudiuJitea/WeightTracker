from app import create_app
from app.models import User, WeightEntry, CalorieEntry
from app.extensions import db

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'WeightEntry': WeightEntry,
        'CalorieEntry': CalorieEntry
    } 

if __name__ == '__main__':
    app.run(debug=True)