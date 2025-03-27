import os
from app import create_app

# Create application instance
app = create_app()

if __name__ == '__main__':
    # Start the app with debugging enabled
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))