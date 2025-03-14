import os
from website import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Use the port assigned by Render
    app.run(host='0.0.0.0', port=port, debug=False)  # Debug should be False in production
