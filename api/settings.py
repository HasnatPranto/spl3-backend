import os

# JWT Config
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or "boost_secret"
#os.getenv("JWT_SECRET_KEY")